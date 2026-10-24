"""
e2e_delay_model.py - SEC-01 Phase 3: end-to-end V2X telemetry encryption delay model.
Paths: plain | AES-GCM | ECDSA | AES-GCM+ECDSA, plus authenticated-ECDH session setup.
HOST_MEASURED = median of saved host runs (C, Mbed TLS)  -> MEASURED (host)
M4_ESTIMATED  = only if m4_estimates.csv exists (Renode instruction counts) -> ESTIMATED
Everything else (rate, PHY overhead, sizes) is an ASSUMPTION listed below.
"""
import csv, os, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.join(HERE, "..", "02_Crypto_Benchmark", "phase2_latency")
AES_FILES = [os.path.join(P2, f) for f in ("results_c.csv", "results_c_run2.csv", "results_c_run3.csv")]
ECDSA_FILES = [os.path.join(HERE, f) for f in ("results_ecdsa.csv", "results_ecdsa_run2.csv", "results_ecdsa_run3.csv")]

# ---------------- ASSUMPTIONS (see assumptions_phase3.md) ----------------
RATE_MBPS = 6.0          # confirmed baseline PHY rate (Deepayan Das; Phase 3 PDF)
T_PHY_US = 40.0          # 802.11p 10 MHz preamble + SIGNAL; not valid for C-V2X PC5 framing
T_PROP_US = 1.0          # about 300 m
GCM_OVERHEAD_B = 28      # 12 B nonce + 16 B tag
SIG_B = 64               # raw ECDSA P-256 signature r||s
ID_CASES = {"id_digest_8B": 8, "id_cert_130B": 130}   # signer identity: ASSUMPTIONS, verify vs IEEE 1609.2
PUBKEY_B = 65            # uncompressed P-256 public key
PAYLOADS = (64, 256, 1024)
PERIODS_MS = {"10Hz": 100.0, "20Hz": 50.0}
CLOCK_MHZ = 168.0        # STM32F407 clock (assumption for M4 estimate)
CPI_LOW, CPI_HIGH = 1.0, 2.0   # assumed cycles per instruction range for M4 estimate
# --------------------------------------------------------------------------


def load(files):
    vals = {}
    for fn in files:
        with open(fn) as f:
            for r in csv.DictReader(f):
                vals.setdefault((r["op"], int(r["bytes"])), []).append(float(r["median_us"]))
    return {k: statistics.median(v) for k, v in vals.items()}


def build_times(src):
    t = {"aes": {}}
    for (op, b), v in src.items():
        if op.startswith("AES-128-GCM"):
            t["aes"][b] = v
        elif op == "ECDH P-256 keygen":
            t["keygen"] = v
        elif op == "ECDH P-256 shared secret":
            t["shared"] = v
        elif op == "ECDSA P-256 sign":
            t["sign"] = v
        elif op == "ECDSA P-256 verify":
            t["verify"] = v
    return t


def air(nbytes):
    return T_PHY_US + 8.0 * nbytes / RATE_MBPS


def message_rows(case, t):
    rows = []
    for L in PAYLOADS:
        if L not in t["aes"]:
            continue
        enc = dec = t["aes"][L]          # decrypt assumed equal to encrypt
        plain_total = air(L) + T_PROP_US
        paths = [("plain", "-", 0, 0.0, 0.0),
                 ("AES-GCM", "-", GCM_OVERHEAD_B, enc, dec)]
        for idn, idb in ID_CASES.items():
            paths.append(("ECDSA", idn, SIG_B + idb, t["sign"], t["verify"]))
            paths.append(("AES-GCM+ECDSA", idn, GCM_OVERHEAD_B + SIG_B + idb,
                          enc + t["sign"], dec + t["verify"]))
        for name, idn, ov, tx, rx in paths:
            total = tx + air(L + ov) + T_PROP_US + rx
            row = dict(case=case, path=name, signer_id=idn, payload_B=L, overhead_B=ov,
                       sender_compute_us=round(tx, 3), receiver_compute_us=round(rx, 3),
                       airtime_us=round(air(L + ov), 3), total_us=round(total, 3),
                       added_us=round(total - plain_total, 3))
            for rate, pms in PERIODS_MS.items():
                per_us = pms * 1000.0
                row[f"total_pct_{rate}"] = round(100.0 * total / per_us, 4)
                row[f"added_pct_{rate}"] = round(100.0 * (total - plain_total) / per_us, 4)
                row[f"sender_compute_pct_{rate}"] = round(100.0 * tx / per_us, 4)
                row[f"fits_{rate}"] = "yes" if total < per_us else "NO"
                row[f"receiver_compute_pct_{rate}"] = round(100.0 * rx / per_us, 4)
                row[f"fits_{rate}"] = "yes" if (total < per_us and tx < per_us and rx < per_us) else "NO"
            rows.append(row)
    return rows


def setup_rows(case, t):
    rows = []
    for idn, idb in ID_CASES.items():
        h = PUBKEY_B + SIG_B + idb
        total = 2 * (t["keygen"] + t["sign"] + t["verify"] + t["shared"]) + 2 * (air(h) + T_PROP_US)
        row = dict(case=case, signer_id=idn, handshake_msg_B=h, setup_total_us=round(total, 3),
                   setup_total_ms=round(total / 1000.0, 4))
        for rate, pms in PERIODS_MS.items():
            row[f"setup_pct_of_{rate}_period"] = round(100.0 * total / (pms * 1000.0), 3)
        rows.append(row)
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# ---------------- build cases ----------------
host = build_times({**load(AES_FILES), **load(ECDSA_FILES)})
cases = [("HOST_MEASURED", host)]

m4_file = os.path.join(HERE, "m4_estimates.csv")   # columns: op,bytes,instr_count
if os.path.exists(m4_file):
    counts = {}
    with open(m4_file) as f:
        for r in csv.DictReader(f):
            counts[(r["op"], int(r["bytes"]))] = float(r["instr_count"])
    for label, cpi in (("M4_ESTIMATED_LOW_CPI1.0", CPI_LOW), ("M4_ESTIMATED_HIGH_CPI2.0", CPI_HIGH)):
        us = {k: v * cpi / CLOCK_MHZ for k, v in counts.items()}
        t = build_times(us)
        if all(k in t for k in ("keygen", "shared", "sign", "verify")) and t["aes"]:
            cases.append((label, t))

msg, setup = [], []
for name, t in cases:
    msg += message_rows(name, t)
    setup += setup_rows(name, t)

write_csv(os.path.join(HERE, "e2e_model_output.csv"), msg)
write_csv(os.path.join(HERE, "e2e_setup_output.csv"), setup)

# ---------------- print summary (payload 64 B) ----------------
print("MEASURED (host) crypto times used, us:", {k: v for k, v in host.items() if k != "aes"}, "AES:", host["aes"])
print()
for name, _ in cases:
    print(f"== {name} | payload 64 B ==")
    print(f"{'path':<15}{'signer_id':<14}{'tx_us':>13}{'rx_us':>13}{'added_us':>13}{'total_us':>13}"
          f"{'tot%100ms':>11}{'tot%50ms':>10}{'fits10/20':>11}")
    for r in msg:
        if r["case"] == name and r["payload_B"] == 64:
            print(f"{r['path']:<15}{r['signer_id']:<14}{r['sender_compute_us']:>13}{r['receiver_compute_us']:>13}"
                  f"{r['added_us']:>13}{r['total_us']:>13}{r['total_pct_10Hz']:>11}{r['total_pct_20Hz']:>10}"
                  f"{r['fits_10Hz'] + '/' + r['fits_20Hz']:>11}")
    for r in setup:
        if r["case"] == name:
            print(f"  session setup ({r['signer_id']}): {r['setup_total_ms']} ms "
                  f"({r['setup_pct_of_10Hz_period']}% of 100 ms)")
    print()

# ---------------- charts ----------------
sel = [r for r in msg if r["case"] == "HOST_MEASURED" and r["payload_B"] == 64 and r["path"] != "plain"]
labels = [f"{r['path']}\n{r['signer_id']}" if r["signer_id"] != "-" else r["path"] for r in sel]
crypto = [r["sender_compute_us"] + r["receiver_compute_us"] for r in sel]
extra_air = [r["added_us"] - c for r, c in zip(sel, crypto)]
plt.figure(figsize=(9, 5))
plt.bar(labels, crypto, label="Crypto compute (MEASURED, host)")
plt.bar(labels, extra_air, bottom=crypto, label="Extra airtime from overhead (MODELED)")
plt.ylabel("Added delay per message (us)")
plt.title("Added delay at 6 Mbps, 64 B payload (host crypto, MODELED airtime)")
plt.legend()
plt.xticks(fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "e2e_added_delay.png"), dpi=150)

m4_cases = [c for c in cases if c[0].startswith("M4")]
if m4_cases:
    plt.figure(figsize=(9, 5))
    names = ["AES-GCM", "ECDSA sign", "ECDSA verify", "ECDH keygen", "ECDH shared"]
    for label, t in m4_cases:
        vals = [t["aes"].get(64, float("nan")), t["sign"], t["verify"], t["keygen"], t["shared"]]
        plt.bar([f"{n}\n{label[-8:]}" for n in names], vals, alpha=0.6, label=label)
    plt.axhline(50000, color="r", ls="--", label="50 ms period (20 Hz)")
    plt.axhline(100000, color="k", ls="--", label="100 ms period (10 Hz)")
    plt.yscale("log")
    plt.ylabel("Estimated time (us, log scale)")
    plt.title("Cortex-M4 compute time (ESTIMATED from Renode instruction counts)")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "m4_compute_vs_period.png"), dpi=150)

print("Saved e2e_model_output.csv, e2e_setup_output.csv, e2e_added_delay.png"
      + (", m4_compute_vs_period.png" if m4_cases else " (no m4_estimates.csv yet: host case only)"))