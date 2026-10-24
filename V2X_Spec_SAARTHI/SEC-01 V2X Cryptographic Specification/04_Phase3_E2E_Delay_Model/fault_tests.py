"""
fault_tests.py - SEC-01 Phase 3: crypto-layer fault-injection tests (software simulation).

Simulates an ARU sender and a receiver using AES-128-GCM with counter nonces, and injects the
faults named in the Phase 3 directive (power drops, communication cuts) plus tampering, spoofing,
replay and flooding. It tests PROTOCOL LOGIC in software. It does NOT test the HSM hardware,
the radio, or real flash behaviour. "NVM" below is a Python dict standing in for non-volatile memory.

Wire format: nonce (12 B = 4 B sender id + 8 B counter) || ciphertext || tag (16 B)  -> 28 B overhead.
"""
import csv, os, random, struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

HERE = os.path.dirname(os.path.abspath(__file__))
AAD = b"SEC01-TLM-v1"
SENDER_ID = 0x0A01
BLOCK = 100          # write-ahead reservation size for the nonce counter


class NonceReuseError(Exception):
    pass


class Sender:
    def __init__(self, key, sender_id, nvm, persistent=True):
        self.aes, self.sid, self.nvm, self.persistent = AESGCM(key), sender_id, nvm, persistent
        self.high = None                       # highest counter used in this power cycle
        if persistent:
            self.counter = nvm.get("reserved", 0)      # resume at the reserved value (skips unused ones)
            self.limit = self.counter + BLOCK
            nvm["reserved"] = self.limit               # write-ahead: persist BEFORE using the block
        else:
            self.counter, self.limit = 0, None         # volatile counter: restarts at 0 after power loss

    def next_nonce(self):
        if self.high is not None and self.counter <= self.high:
            raise NonceReuseError(f"counter {self.counter} already used")
        if self.persistent and self.counter >= self.limit:
            self.limit += BLOCK
            self.nvm["reserved"] = self.limit
        n = struct.pack(">IQ", self.sid, self.counter)
        self.high = self.counter
        self.counter += 1
        return n

    def send(self, payload):
        n = self.next_nonce()
        return n + self.aes.encrypt(n, payload, AAD)


class Receiver:
    def __init__(self, key, nvm, persistent=True, known=(SENDER_ID,), auth_budget=None):
        self.aes, self.nvm, self.persistent, self.known = AESGCM(key), nvm, persistent, set(known)
        self.last = dict(nvm.get("rx_last", {})) if persistent else {}
        self.auth_budget, self.budget_left = auth_budget, auth_budget
        self.stats = {"accepted": 0, "decrypt_calls": 0}
        self.log = []
        self.seq = nvm.get("seq", 0) if persistent else 0

    def _event(self, name, ctr=None):
        self.seq += 1
        if self.persistent:
            self.nvm["seq"] = self.seq
        self.log.append((self.seq, name, ctr))
        self.stats[name] = self.stats.get(name, 0) + 1

    def new_window(self):
        self.budget_left = self.auth_budget

    def receive(self, wire):
        if len(wire) < 28:
            self._event("rejected_malformed"); return None
        nonce = wire[:12]
        sid, ctr = struct.unpack(">IQ", nonce)
        if sid not in self.known:                                   # cheap pre-checks, no decrypt
            self._event("rejected_unknown_sender", ctr); return None
        if ctr <= self.last.get(sid, -1):
            self._event("rejected_replay_or_old", ctr); return None
        if self.budget_left is not None:
            if self.budget_left <= 0:
                self._event("rejected_rate_limited", ctr); return None
            self.budget_left -= 1
        self.stats["decrypt_calls"] += 1
        try:
            pt = self.aes.decrypt(nonce, wire[12:], AAD)
        except InvalidTag:
            self._event("rejected_auth_fail", ctr); return None      # state is NOT advanced
        self.last[sid] = ctr
        if self.persistent:
            self.nvm["rx_last"] = dict(self.last)
        self._event("accepted", ctr)
        return pt


results, all_logs = [], []


def record(test, req, ok, detail, control=False):
    kind = "CONTROL" if control else "TEST"
    outcome = ("WEAKNESS SHOWN (expected)" if ok else "NOT SHOWN") if control else ("PASS" if ok else "FAIL")
    results.append((test, kind, req, outcome, detail))


def fresh():
    return os.urandom(16)


def t1_valid():
    k, s, r = fresh(), None, None
    s = Sender(k, SENDER_ID, {}); r = Receiver(k, {})
    ok = all(r.receive(s.send(b"telemetry %d" % i)) == b"telemetry %d" % i for i in range(20))
    record("T1 valid messages accepted", "ZT-01", ok and r.stats["accepted"] == 20, f"{r.stats['accepted']} of 20 accepted")
    all_logs.append(("T1", r.log))


def t2_tamper():
    k = fresh(); s = Sender(k, SENDER_ID, {}); r = Receiver(k, {})
    good = s.send(b"speed=50")
    bad_ct = bytearray(good); bad_ct[14] ^= 0x01                      # flip a ciphertext bit
    bad_tag = bytearray(good); bad_tag[-1] ^= 0x80                    # flip a tag bit
    bad_nonce = bytearray(good); bad_nonce[11] ^= 0x01                # change counter (nonce) in transit
    rej = [r.receive(bytes(x)) is None for x in (bad_ct, bad_tag, bad_nonce)]
    follow = r.receive(s.send(b"speed=51")) == b"speed=51"            # system still works afterwards
    ok = all(rej) and follow and r.stats["rejected_auth_fail"] == 3
    record("T2 tampered messages rejected", "ZT-01, ZT-09", ok, "3 of 3 tampered rejected; later valid message accepted")
    all_logs.append(("T2", r.log))


def t3_wrong_key_spoof():
    k = fresh(); s = Sender(k, SENDER_ID, {}); r = Receiver(k, {})
    attacker = Sender(fresh(), SENDER_ID, {}); attacker.counter = 5000   # right id, wrong key, high counter
    forged = attacker.send(b"speed=0")
    unknown = Sender(fresh(), 0x0BAD, {}).send(b"hello")
    r1, r2 = r.receive(forged), r.receive(unknown)
    legit = r.receive(s.send(b"speed=50"))                               # forged high counter must not block real traffic
    ok = (r1 is None and r2 is None and legit == b"speed=50"
          and r.stats["rejected_auth_fail"] == 1 and r.stats["rejected_unknown_sender"] == 1
          and r.last[SENDER_ID] == 0)
    record("T3 wrong-key and spoofed sender rejected", "ZT-01, ZT-02, ZT-09", ok,
           "forged (wrong key) and unknown sender rejected; receiver state not advanced by forgery")
    all_logs.append(("T3", r.log))


def t4_replay():
    k = fresh(); s = Sender(k, SENDER_ID, {}); r = Receiver(k, {})
    msgs = [s.send(b"m%d" % i) for i in range(10)]
    for m in msgs: r.receive(m)
    replays = [r.receive(msgs[i]) is None for i in (9, 5, 0)]            # newest, middle, oldest
    ok = all(replays) and r.stats["rejected_replay_or_old"] == 3 and r.stats["decrypt_calls"] == 10
    record("T4 replayed messages rejected", "ZT-05", ok, "3 of 3 replays rejected without decryption")
    all_logs.append(("T4", r.log))


def t5_power_drop_sender():
    rng = random.Random(2026)
    k, nvm = fresh(), {}
    seen, dup = set(), 0
    for cycle in range(200):                                              # 200 power drops at random points
        s = Sender(k, SENDER_ID, nvm)
        for _ in range(rng.randint(1, 2 * BLOCK + 7)):
            n = s.next_nonce()
            if n in seen: dup += 1
            seen.add(n)
    record("T5 sender power drops: nonce never reused", "ZT-04",
           dup == 0, f"200 power cycles, {len(seen)} nonces issued, {dup} duplicates (persistent write-ahead counter)")
    # control: same test with a volatile counter
    nvm2, seen2, dup2 = {}, set(), 0
    for cycle in range(200):
        s = Sender(k, SENDER_ID, nvm2, persistent=False)
        for _ in range(rng.randint(1, 2 * BLOCK + 7)):
            n = s.next_nonce()
            if n in seen2: dup2 += 1
            seen2.add(n)
    record("T5c volatile counter (negative control)", "ZT-04", dup2 > 0,
           f"{dup2} nonce reuses after power drops: shows why the counter must be persistent", control=True)


def t6_comms_cut_and_receiver_reboot():
    k, nvm_r = fresh(), {}
    s = Sender(k, SENDER_ID, {}); r = Receiver(k, nvm_r)
    msgs = [s.send(b"m%d" % i) for i in range(50)]
    delivered = [i for i in range(50) if not (10 <= i < 30)]              # link cut: messages 10..29 lost
    got = [r.receive(msgs[i]) for i in delivered]
    late = r.receive(msgs[15]) is None                                    # a lost message arrives late: rejected
    ok1 = all(g is not None for g in got) and late
    r2 = Receiver(k, nvm_r)                                               # receiver power drop, persistent state
    replay_after_reboot = r2.receive(msgs[45]) is None
    resume = r2.receive(s.send(b"after reboot")) == b"after reboot"
    record("T6 communication cut and receiver reboot", "ZT-05, ZT-09", ok1 and replay_after_reboot and resume,
           "30 of 30 delivered accepted across the gap; late old message rejected; replay after reboot rejected; traffic resumes")
    r3 = Receiver(k, {}, persistent=False)                                # control: receiver forgets its counters
    accepted_replay = r3.receive(msgs[45]) is not None
    record("T6c volatile receiver state (negative control)", "ZT-05", accepted_replay,
           "replay accepted after a reboot when counters are not persistent", control=True)
    all_logs.append(("T6", r.log + r2.log))


def t7_nonce_reuse():
    k = fresh(); aes = AESGCM(k); n = struct.pack(">IQ", SENDER_ID, 7)
    p1, p2 = b"speed=050 pos=1234", b"speed=120 pos=9999"
    c1, c2 = aes.encrypt(n, p1, AAD)[:len(p1)], aes.encrypt(n, p2, AAD)[:len(p2)]
    leak = bytes(a ^ b for a, b in zip(c1, c2)) == bytes(a ^ b for a, b in zip(p1, p2))
    record("T7c nonce reuse leaks plaintext relation (control)", "ZT-04", leak,
           "C1 xor C2 equals P1 xor P2 when a nonce is reused", control=True)
    s = Sender(k, SENDER_ID, {})
    for _ in range(10): s.send(b"x")
    s.counter = 3                                                         # fault: counter rolled back
    try:
        s.send(b"y"); guard = False
    except NonceReuseError:
        guard = True
    record("T7 sender refuses to reuse a nonce", "ZT-04", guard, "counter rollback detected and send blocked")


def t8_flood():
    k = fresh(); s = Sender(k, SENDER_ID, {}); r = Receiver(k, {}, auth_budget=50)
    msgs = [s.send(b"m%d" % i) for i in range(20)]
    for m in msgs: r.receive(m)
    r.new_window()
    before = r.stats["decrypt_calls"]
    for i in range(400): r.receive(msgs[i % 20])                          # 400 replays
    for i in range(300): r.receive(Sender(fresh(), 0x0BAD, {}).send(b"z"))  # 300 unknown senders
    pre_ok = r.stats["decrypt_calls"] == before
    atk = Sender(fresh(), SENDER_ID, {}); atk.counter = 10_000
    for i in range(300): r.receive(atk.send(b"f"))                        # 300 forgeries with fresh counters
    limited = r.stats["decrypt_calls"] - before == 50 and r.stats["rejected_rate_limited"] == 250
    r.new_window()
    legit = r.receive(s.send(b"real")) == b"real"
    record("T8 flood: pre-checks and rate limit before expensive verification", "ZT-15, ZT-11",
           pre_ok and limited and legit,
           "700 replays or unknown senders cost 0 decryptions; 300 forgeries capped at 50 authentication attempts; real traffic resumed")
    all_logs.append(("T8", r.log))


for t in (t1_valid, t2_tamper, t3_wrong_key_spoof, t4_replay, t5_power_drop_sender,
          t6_comms_cut_and_receiver_reboot, t7_nonce_reuse, t8_flood):
    t()

# ZT-14: security-event log must carry a strictly increasing counter
mono = all(all(a[0] < b[0] for a, b in zip(lg, lg[1:])) for _, lg in all_logs)
record("T9 security events logged with a monotonic counter", "ZT-14", mono and sum(len(l) for _, l in all_logs) > 0,
       f"{sum(len(l) for _, l in all_logs)} events across all tests")

print(f"{'test':<68}{'kind':<9}{'requirement':<20}result")
for name, kind, req, outcome, detail in results:
    print(f"{name:<68}{kind:<9}{req:<20}{outcome}")
    print(f"    {detail}")
tests = [r for r in results if r[1] == "TEST"]
controls = [r for r in results if r[1] == "CONTROL"]
print(f"\nTESTS PASSED: {sum(1 for r in tests if r[3] == 'PASS')} of {len(tests)}")
print(f"CONTROLS (weakness shown as expected): {sum(1 for r in controls if r[3].startswith('WEAKNESS'))} of {len(controls)}")
print("Scope: software simulation of protocol logic only (not HSM hardware, radio or flash).")

with open(os.path.join(HERE, "fault_test_results.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["test", "kind", "requirement", "result", "detail"]); w.writerows(results)
with open(os.path.join(HERE, "security_event_log.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["test", "seq", "event", "counter"])
    for tname, lg in all_logs:
        for seq, ev, ctr in lg: w.writerow([tname, seq, ev, ctr])
print("Saved fault_test_results.csv and security_event_log.csv")
raise SystemExit(0 if all(r[3] == "PASS" for r in tests) and all(r[3].startswith("WEAKNESS") for r in controls) else 1)