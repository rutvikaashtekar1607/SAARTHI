# SAARTHI — SEC-01 Phase 3: End-to-End V2X Encryption Delay, Cortex-M4 Instruction Counts and Zero-Trust Specification

**Project:** SAARTHI
**Organization:** EduRankAI
**Owner:** Rutvika Ashtekar
**Role:** Cybersecurity Lead (Aerospace Security)
**Domain:** Cryptography & Threat Analysis
**Task Reference:** SEC-01 Phase 3 (per SAARTHI-SYS-P3-TASK-002, Phase 3 Task Allocation Matrix & Virtual Integration Directive, Days 19 to 25, 7-day milestone)
**Repository:** https://github.com/rutvikaashtekar1607/SAARTHI

---

## 📌 What Is SAARTHI

SAARTHI is an autonomous public-mobility, public-management, and distributed infrastructure system designed as an interoperable digital coordination layer across urban infrastructure. It connects road traffic, public transit, parking hubs, emergency dispatch, and civic reporting into a single federated operational view, without replacing existing municipal applications.

## 📌 Purpose of This Phase

Phase 2 produced host-laptop latency for AES-GCM and ECDH P-256, a V2X encryption-delay model and the Section 12A threat assumptions. It did not cover ECDSA, Cortex-M4 timing or a zero-trust specification.

The official Phase 3 task is:

> End-to-End V2X Telemetry Encryption Delay Models (AES-GCM / ECC over 6 Mbps / 10 Hz) & STRIDE Zero-Trust Spec.

Work package 12 asks to model the cryptographic processing delay of AES-GCM and ECC over an 802.11p/C-V2X direct channel (6 Mbps PHY rate, 10 Hz / 20 Hz telemetry) "to ensure zero control loop latency degradation." The directive also requires virtual fault injection (power drops, communication cuts).

This phase therefore delivers:

- **ECDSA P-256** host benchmark (C, Mbed TLS 3.6.7).
- **Cortex-M4 instruction counts** for AES-GCM, ECDH P-256 and ECDSA P-256 in Renode, with ESTIMATED times.
- An **end-to-end V2X delay model** for AES-GCM, ECDSA and AES-GCM + ECDSA.
- A **Zero-Trust specification** (Section 14 of the STRIDE file, ZT-01 to ZT-15).
- **Fault-injection tests** of the crypto layer (software simulation).

---

## 🏷️ Labeling Rule

Every number in Phase 3 is tagged:

| Tag | Meaning |
|---|---|
| **MEASURED (host)** | Timed on the host laptop (Intel Core i5-1135G7, Windows 11, C, Mbed TLS 3.6.7) |
| **MEASURED (Renode)** | Executed-instruction count read in the Renode 1.16.0 STM32F4 emulator. Renode counts instructions, not cycles |
| **MODELED** | Calculated from the delay equations and the stated assumptions |
| **ESTIMATED** | Cortex-M4 times derived from Renode instruction counts with an assumed 168 MHz clock and an assumed 1.0 to 2.0 cycles per instruction (CPI) |

⚠️ **Host timings are not Cortex-M4 timings. Cortex-M4 times in this phase are ESTIMATED, not measured.**

---

## 📁 Folder Contents

Paths are relative to the `V2X_Spec_SAARTHI` folder. `P3` = `SEC-01 V2X Cryptographic Specification/04_Phase3_E2E_Delay_Model`.

| File / Folder | Purpose |
|---|---|
| `SEC-01 V2X Cryptographic Specification/Phase3_Report.md` | Phase 3 report (Sir's 5-section structure + next-task recommendation) |
| `SEC-01 V2X Cryptographic Specification/Phase3_README.md` | This file |
| `SEC-01 V2X Cryptographic Specification/01_SEC-01_STRIDE_Threat_Model.md` | Threat model; new Section 14 (Zero-Trust Specification, Phase 3) |
| `P3/bench_ecdsa.c` | ECDSA P-256 host benchmark (C, Mbed TLS 3.6.7) |
| `P3/results_ecdsa.csv`, `results_ecdsa_run2.csv`, `results_ecdsa_run3.csv` | ECDSA host results, three runs |
| `P3/e2e_delay_model.py` | End-to-end delay model |
| `P3/e2e_model_output.csv`, `P3/e2e_setup_output.csv` | Model outputs (per-message and session setup) |
| `P3/assumptions_phase3.md` | Phase 3 model assumptions |
| `P3/m4_bench.c`, `config_m4.h`, `linker.ld`, `startup.c` | Cortex-M4 timing firmware |
| `P3/build_m4.ps1`, `P3/run_m4.resc`, `P3/parse_m4_counts.py` | Build, Renode run and parse scripts |
| `P3/m4_estimates.csv`, `P3/m4_counts_detail.csv` | Renode instruction counts and estimated times |
| `P3/fault_tests.py` | Fault-injection tests (software simulation) |
| `P3/fault_test_results.csv`, `P3/security_event_log.csv` | Fault-test results and event log |
| `P3/e2e_added_delay.png` | Figure: added delay at 6 Mbps, 64 B payload |
| `P3/m4_compute_vs_period.png` | Figure: Cortex-M4 compute time vs message periods (log scale) |
| `03_Phase2_Latency_Model/trust_boundaries.png` | Figure: trust boundaries TB-04 to TB-07 (from Phase 2) |
| `Evidence/Phase3_*.png` | Phase 3 screenshots |

Notes:

- Phase 2 files (host AES-GCM and ECDH results, `03_Phase2_Latency_Model`) are inputs to this work and were **not changed**.
- The Phase 1 Renode firmware (`aes_gcm_benchmark.elf`, `ecc_benchmark.elf`) was **not used**. The Cortex-M4 firmware was rebuilt from the source files listed above.
- Build artifacts (`bench_ecdsa.exe`, object files, `.elf`, `.map`) are excluded from the repository.

---

## 🛠️ Benchmark Environment

| Item | Used |
|---|---|
| Host CPU | 11th Gen Intel Core i5-1135G7 @ 2.40 GHz |
| Host OS | Windows 11 |
| Host build | C, gcc `-O2`, Mbed TLS 3.6.7 |
| Target architecture | ARM Cortex-M4 / STM32F4 (STM32F407) |
| Execution environment | Renode 1.16.0 |
| Cortex-M4 toolchain | Arm GNU Toolchain 12.2.MPACBTI-Rel1 (gcc 12.2.1), `-O2` |
| Cryptographic library | Mbed TLS 3.6.7 with minimal configuration `config_m4.h` |
| Firmware size | 29,404 B code (text), 88 B data, 10,872 B bss |
| Assumed clock | 168 MHz (STM32F407) |
| Assumed CPI range | 1.0 to 2.0 |

---

## 🔏 ECDSA P-256 Latency (C, Mbed TLS 3.6.7) — MEASURED (host)

### Operation

* ECDSA P-256 sign and verify, timed separately
* 100 calls per repeat, 15 repeats, 3 saved runs
* Correctness check: a valid signature verified and a tampered digest was rejected in all three runs
* DER signature length: 70 to 71 B

### Result (median latency per operation, µs)

| Operation | Run 1 | Run 2 | Run 3 | Median of runs |
|---|---:|---:|---:|---:|
| ECDSA P-256 sign | 263.188 | 262.403 | 263.235 | 263.188 |
| ECDSA P-256 verify | 868.598 | 906.572 | 890.081 | 890.081 |

AES-GCM and ECDH host results come from Phase 2 (AES-GCM 64 B: 0.469 µs, 256 B: 1.272 µs, 1024 B: 3.110 µs; ECDH key generation 243.612 µs; shared secret 670.224 µs; median of three runs).

---

## 🧮 Cortex-M4 Instruction Counts (Renode) — MEASURED (Renode); times ESTIMATED

### Method

* Each operation runs once as warm-up and five times between start and end markers.
* Renode hooks read the executed-instruction count at each marker.
* The run finished with `bench_done = 1`, `bench_status = 0` and **70 markers** captured.
* Estimate: `t = N × CPI / f`, with `f` = 168 MHz and CPI between 1.0 and 2.0.

### Result

| Operation | Bytes | Median instructions (min to max) | Est. time, CPI 1.0 | Est. time, CPI 2.0 |
|---|---|---|---:|---:|
| AES-128-GCM encrypt | 64 | 9,138 (9,138 to 9,144) | 0.054 ms | 0.109 ms |
| AES-128-GCM encrypt | 256 | 30,438 (30,438 to 30,444) | 0.181 ms | 0.362 ms |
| AES-128-GCM encrypt | 1024 | 115,638 (115,638 to 115,644) | 0.688 ms | 1.377 ms |
| ECDH P-256 key generation | n/a | 4,712,615 (4,698,804 to 4,720,414) | 28.051 ms | 56.103 ms |
| ECDH P-256 shared secret | n/a | 13,169,923 (13,164,342 to 13,186,541) | 78.392 ms | 156.785 ms |
| ECDSA P-256 sign | 32 (digest) | 6,230,018 (6,223,693 to 6,237,141) | 37.083 ms | 74.167 ms |
| ECDSA P-256 verify | 32 (digest) | 20,848,784 (20,848,784 to 20,848,787) | 124.100 ms | 248.200 ms |

The conclusions below hold at both CPI values.

---

## 📡 End-to-End V2X Delay Model — MODELED

### Equations

```text
T_total = T_tx + T_air + T_prop + T_rx
T_air   = T_phy + 8 (L + O) / R
ΔT      = T_total - (T_phy + 8 L / R + T_prop)
T_setup = 2 (T_keygen + T_sign + T_verify + T_shared) + 2 (T_air(H) + T_prop),  H = 65 + 64 + id bytes
t       = N × CPI / f,   f = 168 MHz,   CPI in [1.0, 2.0]
```

### Inputs

| Parameter | Value | Source |
|---|---|---|
| PHY rate R | 6 Mbps | Confirmed by Deepayan Das; stated in the Phase 3 directive |
| Message rates | 10 Hz (100 ms) and 20 Hz (50 ms) | Phase 3 directive |
| PHY overhead T_phy | 40 µs | Assumption (802.11p 10 MHz); does not apply to C-V2X PC5 framing |
| Propagation T_prop | 1 µs | Assumption (about 300 m) |
| Decrypt time | T_dec = T_enc | Assumption |
| Telemetry payload | 64 B base case; 256 B and 1024 B sensitivity | Author's assumption from the state vector x_ARU (Adarsh Anurag left such assumptions to the author) |
| AES-GCM overhead O | 28 B (12 B nonce + 16 B tag) | AES-GCM format |
| ECDSA overhead O | 64 B signature + signer id (8 B digest or 130 B certificate) | Assumptions, to verify against IEEE 1609.2 |

### Result A: host crypto times (MEASURED), airtime MODELED, 64 B payload

Baseline unsecured total: 126.333 µs.

| Path | Signer id | Added delay | Total one-way | % of 100 ms (10 Hz) | % of 50 ms (20 Hz) |
|---|---|---:|---:|---:|---:|
| AES-GCM | n/a | 38.271 µs | 164.605 µs | 0.165% | 0.329% |
| ECDSA | 8 B digest | 1249.269 µs | 1375.602 µs | 1.376% | 2.751% |
| AES-GCM + ECDSA | 8 B digest | 1287.540 µs | 1413.874 µs | 1.414% | 2.828% |
| ECDSA | 130 B cert | 1411.936 µs | 1538.269 µs | 1.538% | 3.077% |
| AES-GCM + ECDSA | 130 B cert | 1450.207 µs | 1576.540 µs | 1.577% | 3.153% |

### Result B: Cortex-M4 crypto times (ESTIMATED), airtime MODELED, 64 B payload (low = CPI 1.0, high = CPI 2.0)

| Path | Signer id | Total, low | Total, high | % of 100 ms | % of 50 ms | Fits period? |
|---|---|---:|---:|---|---|---|
| AES-GCM | n/a | 0.272 ms | 0.381 ms | 0.27% to 0.38% | 0.54% to 0.76% | **Yes** |
| ECDSA | 8 B digest | 161.4 ms | 322.6 ms | 161% to 323% | 323% to 645% | **No** |
| AES-GCM + ECDSA | 8 B digest | 161.6 ms | 322.8 ms | 162% to 323% | 323% to 646% | **No** |
| ECDSA | 130 B cert | 161.6 ms | 322.8 ms | 162% to 323% | 323% to 646% | **No** |
| AES-GCM + ECDSA | 130 B cert | 161.7 ms | 323.0 ms | 162% to 323% | 323% to 646% | **No** |

### Result C: authenticated session setup (ECDH + ECDSA on both handshake messages)

| Case | 8 B digest | 130 B certificate |
|---|---:|---:|
| Host (MEASURED crypto) | 4.58 ms | 4.91 ms |
| Cortex-M4 (ESTIMATED), CPI 1.0 | 535.7 ms | 536.0 ms |
| Cortex-M4 (ESTIMATED), CPI 2.0 | 1071.0 ms | 1071.3 ms |

### Result D: compute load per message period on the Cortex-M4 (ESTIMATED)

| Operation | At 10 Hz (100 ms) | At 20 Hz (50 ms) |
|---|---|---|
| AES-GCM, 64 B | 0.05% to 0.11% | 0.11% to 0.22% |
| ECDSA sign | 37% to 74% | 74% to 148% |
| ECDSA verify | 124% to 248% | 248% to 496% |

Results for 256 B and 1024 B payloads are in `e2e_model_output.csv`.

### Key findings

* The **AES-GCM path** (per-message protection after an authenticated session) fits both the 10 Hz and 20 Hz periods on the Cortex-M4 (ESTIMATED).
* **Software ECDSA P-256 per message does not fit** either period at 168 MHz, even at the optimistic 1.0 cycles per instruction. This applies to a generic C build of Mbed TLS; optimized or hardware-accelerated ECC could be much faster and was not measured.
* Recommended architecture (a design recommendation, not a measured result): **ECDH + AES-GCM sessions for unicast links**, and **HSM or hardware ECDSA (or a selective-verification policy) for broadcast safety messages**.

---

## ✅ Pass Criteria for "Zero Control-Loop Latency Degradation"

"Zero" cannot be proven in general, so the author defined the criteria below. The FreeRTOS schedule used is the one provided by Rakshita Lakkanna B.: GNC 10 ms (priority 4), Sensing 20 ms (priority 3), Communications 50 ms (priority 2), Telemetry 100 ms (priority 1).

| # | Criterion | Result |
|---|---|---|
| C1 | Crypto runs below GNC and Sensing priority and holds no shared lock | Design requirement ZT-10; **not yet verified** |
| C2 | Crypto compute plus airtime fits inside the message period | AES-GCM: **met** (host and Cortex-M4). Software ECDSA: **not met** on the Cortex-M4 |
| C3 | Per-operation compute load stays under 100% of the period | AES-GCM: met. ECDSA sign: 37% to 148%. ECDSA verify: 124% to 496%, **not met** |
| C4 | Interference from Sensing and Communications tasks included | **Not included**: their execution times are not yet measured |

---

## 🛡️ Zero-Trust Specification (Section 14 of the STRIDE file)

Section 14 extends the STRIDE analysis (Sections 5, 6 and 12A) for the ARU (Autonomous Roadside Unit) with five principles: no implicit trust, verify explicitly, least privilege, assume breach and fail closed, short-lived secrets.

### Link-type decision

| Link | Pattern |
|---|---|
| ARU to Command Centre (unicast, TB-07) | Mutually authenticated ECDH + ECDSA session, then per-message AES-128-GCM with counter nonces. Public-key cost is paid once per session |
| ARU broadcast (TB-06) | Per-message sender authentication required, because a shared symmetric key cannot show which key holder sent a message. The path is an **open decision** (ZT-12) |

### Requirements ZT-01 to ZT-15

| ID | Requirement (summary) | Status |
|---|---|---|
| ZT-01 | Authenticate every message crossing TB-06 and TB-07; drop and log failures | Verified in software simulation |
| ZT-02 | Never trust a message by apparent sender address or radio source | Verified in software simulation |
| ZT-03 | Unicast sessions start with mutually authenticated ECDH + ECDSA, outside control-loop tasks | Open (setup time ESTIMATED 0.54 to 1.07 s) |
| ZT-04 | Never reuse an AES-GCM nonce; counter survives power loss and reboot | Verified in software simulation; HSM counter to be confirmed (Mohan) |
| ZT-05 | Reject replays; last accepted counter survives reboot | Verified in software simulation |
| ZT-06 | Rotate keys before counter or NIST SP 800-38D limits and on a policy interval | Open (interval to be set) |
| ZT-07 | Keys generated and stored in the HSM, never in plaintext on the MCU-HSM bus | Open (Mohan) |
| ZT-08 | HSM register map locked after configuration; debug disabled | Open (Mohan) |
| ZT-09 | Fail closed: drop, raise a security event, no unauthenticated fallback | Verified in software simulation (drop and log); safe state not tested |
| ZT-10 | Crypto task below GNC (4) and Sensing (3), no shared lock | Pending (assumption; needs FreeRTOS trace) |
| ZT-11 | Per-message crypto compute under the message period | Evidence available: AES-GCM meets it; software ECDSA does not |
| ZT-12 | Broadcast messages use hardware or HSM-assisted ECDSA, or a documented selective-verification policy | Open decision |
| ZT-13 | Sensor inputs untrusted until plausibility-checked; defined safe state | Open |
| ZT-14 | Security events logged with a monotonic counter persisted across reboot | Verified in software simulation |
| ZT-15 | Cheap pre-checks and rate limits before expensive verification | Verified in software simulation (AES-GCM path only) |

"Verified in software simulation" means protocol logic only. It does not cover the HSM hardware, the radio or real flash behaviour.

---

## 🧪 Test Runs

### Cortex-M4 Renode run

| Check | Result |
|---|---|
| Firmware build (Arm GNU 12.2.MPACBTI-Rel1, Mbed TLS 3.6.7, `-O2`) | Completed |
| `bench_done` | 1 |
| `bench_status` | 0 |
| Markers captured | 70 |
| Operations measured | 7 operations × 5 repeats |

Renode hook used in `run_m4.resc`:

```text
$addr = `sysbus GetSymbolAddress "bench_marker"`
sysbus AddWatchpointHook $addr DoubleWord Write "import sys; sys.marks.append((value, cpu.ExecutedInstructions))"
emulation RunFor "00:00:08"
```

Firmware writes `(op_id << 8) | 1` before and `(op_id << 8) | 2` after each operation; the count for an operation is the difference between its end and start marker.

### Fault-injection tests (`fault_tests.py`, software simulation)

Result: **9 of 9 tests PASS**, and **3 of 3 negative controls** showed the expected weakness.

| Test | Fault injected | Requirement | Result |
|---|---|---|---|
| T1 | None (20 valid messages) | ZT-01 | PASS, 20 of 20 accepted |
| T2 | Flipped ciphertext, tag and nonce bits | ZT-01, ZT-09 | PASS, 3 of 3 rejected |
| T3 | Wrong key, unknown sender, forged high counter | ZT-01, ZT-02, ZT-09 | PASS, receiver state not advanced |
| T4 | Replay of newest, middle and oldest message | ZT-05 | PASS, 3 of 3 rejected without decryption |
| T5 | 200 sender power drops at random points | ZT-04 | PASS, 22,841 nonces, 0 duplicates |
| T6 | 20 lost messages, a late old message, receiver reboot | ZT-05, ZT-09 | PASS |
| T7 | Counter rolled back | ZT-04 | PASS, send blocked |
| T8 | 700 replays or unknown senders, 300 forgeries | ZT-15 | PASS, 0 decryptions for the 700; forgeries capped at 50 attempts |
| T9 | Event-log counter across reboot | ZT-14 | PASS, monotonic |
| T5c, T6c, T7c | Volatile counters and nonce reuse (controls) | ZT-04, ZT-05 | Weakness shown: 20,689 nonce reuses; replay accepted after reboot; plaintext relation leaked |

Nonce counter with write-ahead reservation:

```python
if persistent:
    self.counter = nvm.get("reserved", 0)     # resume at the reserved value
    self.limit = self.counter + BLOCK
    nvm["reserved"] = self.limit              # persist BEFORE using the block
```

After a power drop the sender resumes at the persisted reservation, skipping unused values, so a nonce is never reused.

Scope: this tests protocol logic in software, with a Python dictionary standing in for non-volatile memory.

---

## 📸 Evidence

The supporting evidence is stored in:

```text
Evidence/
```

| Evidence File | Evidence |
|---|---|
| `Phase3_01_ECDSA_Host_Runs.png` | ECDSA P-256 host benchmark runs |
| `Phase3_02_E2E_Model_Output.png` | End-to-end delay model output (host crypto times) |
| `Phase3_03_M4_Build.png` | Cortex-M4 firmware build |
| `Phase3_04_Renode_Run.png` | Renode run of the Cortex-M4 benchmark |
| `Phase3_05_M4_Counts.png` | Cortex-M4 instruction counts |
| `Phase3_06_E2E_Model_M4.png` | End-to-end model output (Cortex-M4 ESTIMATED times) |
| `Phase3_07_ZeroTrust_Spec.png` | Zero-Trust specification, Section 14 |
| `Phase3_08_Fault_Tests.png` | Fault-injection test results |

Phase 1 and Phase 2 evidence files are unchanged.

---

## ✅ Verification Status

| Check | Status |
|---|---|
| ECDSA P-256 host benchmark (3 runs, correctness check) | Completed |
| Cortex-M4 firmware rebuilt from source (Phase 1 firmware not reused) | Completed |
| Renode run: `bench_done = 1`, `bench_status = 0`, 70 markers | Completed |
| End-to-end delay model (AES-GCM, ECDSA, AES-GCM + ECDSA; session setup) | Completed |
| Zero-Trust specification ZT-01 to ZT-15 | Completed |
| Fault-injection tests (software simulation) | 9 of 9 PASS |
| Negative controls | 3 of 3 showed the expected weakness |
| Requirements verified in software simulation | ZT-01, 02, 04, 05, 09, 14, 15 |
| 6 Mbps rate and 10 Hz / 20 Hz message rates | Confirmed (Deepayan Das; Phase 3 directive) |
| FreeRTOS task periods and priorities (Rakshita Lakkanna B.) | Confirmed |
| Sensing and Communications execution times; crypto-task WCET | **Pending (not measured)** |
| K. Mohan Krishna review of Phase 3 HSM items (ZT-04, 06, 07, 08, 12) | **Pending** |

---

## ⚠️ Measurement Limits

* Cortex-M4 times are **ESTIMATED** from Renode instruction counts. Renode is instruction-accurate, not cycle-accurate, and does not model flash wait states. The 168 MHz clock and the CPI range of 1.0 to 2.0 are assumptions.
* Instruction counts depend on compiler and library version and apply to the build described above.
* The firmware uses a **non-secure test random generator**, for timing only. The real entropy source (assumption A-03) is not tested.
* The 40 µs PHY overhead is an 802.11p assumption and does not apply to C-V2X (PC5) framing. The 64 B signature and the signer-identity sizes are assumptions to verify against IEEE 1609.2.
* The 64 B telemetry payload is the author's assumption; it is not an agreed value.
* The fault-injection tests simulate protocol logic in software. They do not test the HSM hardware, the radio or real flash behaviour.
* Execution times of the Sensing and Communications tasks, and the WCET of a crypto task under load, are not available.
* The optimized or hardware-accelerated ECC case was not measured.
* Phase 1 Renode results were not re-verified and were not used.

---

## 🎯 Next-Task Recommendation

1. HSM or hardware ECDSA offload with Mohan's HSM: measure sign and verify latency including SPI / I2C / CAN transfer, and decide the broadcast authentication path (ZT-12).
2. Crypto-task WCET and jitter under FreeRTOS load in Renode with Rakshita, replacing the ESTIMATED values and closing criteria C1 and C4.
3. Optimized ECC measurement: repeat the Cortex-M4 count with an optimized P-256 implementation.
4. HSM nonce-counter persistence test across reboot and power loss (ZT-04, A-01).
5. Agree the telemetry payload size and key-rotation interval (ZT-06) with Adarsh and Mohan, and update the model.
6. Phase 4 hardware: cycle counts from the DWT counter on real STM32F4 hardware, replacing the CPI assumption.

---

## 🎯 Task Status

**SEC-01 Phase 3 deliverables: PREPARED. Technical review and executive sign-off are pending.**

The documented results are limited to measurements actually obtained, ESTIMATED values with stated assumptions, and software-simulation test results.

---

## Project / Task Information

| Field | Value |
|---|---|
| Project | SAARTHI |
| Organization | EduRankAI |
| Owner | Rutvika Ashtekar |
| Role | Cybersecurity Lead (Aerospace Security) |
| Domain | Cryptography & Threat Analysis |
| Task | SEC-01 Phase 3: End-to-End V2X Telemetry Encryption Delay Models (AES-GCM / ECC over 6 Mbps / 10 Hz) & STRIDE Zero-Trust Spec |
| Deliverable | ECDSA benchmark + Cortex-M4 instruction counts + end-to-end delay model + Zero-Trust specification + fault-injection tests + report |
| Assigned deadline (Phase 3) | 7 Days |
| Document reference | SAARTHI-SYS-P3-TASK-002 |

⚠️ **Note:** Host timings are not Cortex-M4 timings. Cortex-M4 times are ESTIMATED. Values marked MODELED depend on stated assumptions. "Verified in software simulation" covers protocol logic only. No unverified claim is presented as a confirmed result.

---

## 🏁 Concluding Note: Internship Handover (SEC-01 Phase 3)

This section closes the Phase 3 README. Everything above is unchanged. It records the final state of the SEC-01 work at the end of my internship (28 October 2026) so that the next owner can continue without guesswork.

### Final status

| Item | Status at handover |
|---|---|
| SEC-01 Phase 3 deliverables | **PREPARED** (benchmark, Cortex-M4 counts, delay model, Zero-Trust spec, fault tests, report) |
| Cortex-M4 timing | **ESTIMATED** from Renode instruction counts; not measured on hardware |
| Fault-injection tests | 9 of 9 PASS in software simulation; not tested on HSM hardware, radio or real flash |

### Main conclusion of SEC-01

- AES-GCM per-message protection fits both the 10 Hz and 20 Hz message periods on the Cortex-M4 (ESTIMATED).
- Software ECDSA P-256 per message does **not** fit either period, even at 1.0 cycles per instruction (verify ESTIMATED at 124 to 248 ms against a 100 ms period).
- Recommended design (a design recommendation, not a measured result): ECDH + AES-GCM sessions for unicast links; HSM or hardware-assisted ECDSA, or a documented selective-verification policy, for broadcast safety messages (ZT-12, open decision).

### Where to find everything

- Repository: https://github.com/rutvikaashtekar1607/SAARTHI
- Project site: https://rutvikaashtekar1607.github.io/SAARTHI/
- Complete internship handover (project involvement report, key contributions and all files): https://drive.google.com/drive/folders/1HATq1fFNpeKsob59gDgXteqF0qw_UCxV?usp=sharing

### Contributor

Rutvika Ashtekar, Cybersecurity Lead (Aerospace Security), EduRankAI. Internship concluded 28 October 2026.
