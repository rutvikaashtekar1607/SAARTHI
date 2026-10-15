# SAARTHI — SEC-01 Phase 2: Latency Benchmark, V2X Delay Model and Threat Assumptions

**Project:** SAARTHI
**Organization:** EduRankAI
**Owner:** Rutvika Ashtekar
**Role:** Cybersecurity Lead (Aerospace Security)
**Domain:** Cryptography & Threat Analysis
**Task Reference:** SEC-01 Phase 2 (per the SAARTHI Phase 2 1-Week Task Allocation Matrix, 7-day milestone)
**Repository:** https://github.com/rutvikaashtekar1607/SAARTHI

---

## 📌 What Is SAARTHI

SAARTHI is an autonomous public-mobility, public-management, and distributed infrastructure system designed as an interoperable digital coordination layer across urban infrastructure. It connects road traffic, public transit, parking hubs, emergency dispatch, and civic reporting into a single federated operational view, without replacing existing municipal applications.

## 📌 Purpose of This Phase

Phase 1 produced the SEC-01 threat model, STRIDE vectors, and Renode functional builds (code size and static RAM). It did not establish validated latency.

The official Phase 2 task is:

> Benchmark AES-GCM vs ECC latency in Python/C, model V2X radio transmission encryption delay, and co-write STRIDE threat spec.

This phase therefore delivers:

- AES-GCM vs ECC (ECDH P-256) latency benchmarks in **Python and C**.
- A **V2X radio-transmission encryption-delay model**.
- A **STRIDE threat-assumption and trust-boundary update** (Section 12A), prepared for joint review with K. Mohan Krishna.
- Telemetry encryption latency numbers for the **ICD v1.1 (IF-DATA)** interface audit.

For the ECC benchmark, **ECDH using P-256 / secp256r1** is used.

---

## 🏷️ Labeling Rule

Every number in Phase 2 is tagged:

| Tag | Meaning |
|---|---|
| **MEASURED (host)** | Timed on the host laptop with a high-resolution clock |
| **MODELED** | Calculated from the delay equation and stated assumptions |
| **ESTIMATED** | Derived from an assumption (none are used as results in this phase) |

⚠️ **All timings are host-laptop timings. They are not Cortex-M4 timings. Cortex-M4 latency is pending.**

---

## 📁 Folder Contents

Paths are relative to the `V2X_Spec_SAARTHI` folder.

| File / Folder | Purpose |
|---|---|
| `SEC-01 V2X Cryptographic Specification/Phase2_Report.md` | Phase 2 report (Sir's 5-section structure + next-task recommendation) |
| `SEC-01 V2X Cryptographic Specification/Phase2_README.md` | This file |
| `SEC-01 V2X Cryptographic Specification/01_SEC-01_STRIDE_Threat_Model.md` | Threat model; new Section 12A (Phase 2) |
| `.../02_Crypto_Benchmark/phase2_latency/bench_c.c` | C benchmark (Mbed TLS 3.6.7) |
| `.../phase2_latency/results_c.csv`, `results_c_run2.csv`, `results_c_run3.csv` | C results, three runs |
| `.../phase2_latency/bench_python_v2.py`, `results_python_v2.csv` | Python benchmark, method v2 |
| `.../phase2_latency/bench_python_v3.py`, `results_python_v3.csv` | Python benchmark, method v3 (100 repeats) |
| `.../phase2_latency/LATENCY_METHOD.md` | Measurement method |
| `.../03_Phase2_Latency_Model/v2x_delay_model.py` | V2X delay model script |
| `.../03_Phase2_Latency_Model/model_output.csv` | Model output |
| `.../03_Phase2_Latency_Model/assumptions.md` | Model assumptions register |
| `.../03_Phase2_Latency_Model/delay_vs_payload.png` | Figure: modeled added delay vs payload |
| `.../03_Phase2_Latency_Model/latency_bar.png` | Figure: AES-GCM vs ECDH latency (log scale) |
| `.../03_Phase2_Latency_Model/trust_boundaries.png` | Figure: trust boundaries TB-04 to TB-07 |
| `Evidence/Phase2_*.png` | Phase 2 screenshots |

`results_python.csv` / `bench_python.py` (first Python attempt) are **superseded** by v2 and are not used.

---

## 🛠️ Benchmark Environment

| Item | Used |
|---|---|
| Execution environment | Host laptop (not Cortex-M4) |
| CPU | 11th Gen Intel Core i5-1135G7 @ 2.40 GHz |
| OS | Windows 11 |
| C compiler | MSYS2 gcc 16.2.0, `-O2` |
| C cryptographic library | Mbed TLS 3.6.7 |
| Python | 3.14.7 |
| Python cryptographic library | `cryptography` 50.0.2 (OpenSSL backend) |

---

## 🔐 AES-128-GCM Latency (C, Mbed TLS 3.6.7) — MEASURED (host)

### Operation

* AES-128-GCM authenticated encryption
* 128-bit key, 96-bit nonce, 128-bit tag (28 B overhead per message)
* 5,000 calls per repeat, 15 repeats, 3 saved runs

### Result (median latency per operation, µs)

| Payload | Run 1 | Run 2 | Run 3 | Used in model |
|---|---:|---:|---:|---:|
| 64 B | 0.534 | 0.469 | 0.235 | 0.469 |
| 256 B | 1.413 | 1.272 | 0.751 | 1.272 |
| 1024 B | 3.110 | 4.675 | 2.695 | 3.110 |
| 4096 B | 11.335 | 10.994 | 11.093 | 11.093 |

Small payloads (64 B, 256 B) vary by up to 2x between runs because each call takes under a microsecond, so timer resolution and system noise dominate. They are reported as ranges.

---

## 🔑 ECDH P-256 Latency (C, Mbed TLS 3.6.7) — MEASURED (host)

### Operation

* ECDH key generation and shared-secret computation, timed separately
* Curve: P-256 / secp256r1
* 100 calls per repeat, 15 repeats, 3 saved runs

### Result (median latency per operation, µs)

| Operation | Run 1 | Run 2 | Run 3 | Range |
|---|---:|---:|---:|---|
| Key generation | 244.242 | 224.430 | 243.612 | 224 to 244 |
| Shared secret | 709.591 | 670.224 | 648.928 | 649 to 710 |

---

## 🐍 Python Latency (OpenSSL backend) — MEASURED (host)

| Operation | v2 run 1 | v2 run 2 | v3 (100 repeats) |
|---|---:|---:|---:|
| AES-128-GCM, 64 B | 1.052 | 0.780 | 2.696 |
| AES-128-GCM, 256 B | 0.893 | 0.882 | 1.322 |
| AES-128-GCM, 1024 B | 0.997 | 0.920 | 1.827 |
| AES-128-GCM, 4096 B | 1.402 | 1.309 | 2.980 |
| ECDH P-256 key generation | 16.532 | 16.380 | 22.891 |
| ECDH P-256 shared secret | 51.255 | 53.298 | 60.027 |

Python and C results differ because they use **different library implementations** (OpenSSL vs Mbed TLS). This is not a language comparison. The delay model uses the C numbers.

---

## 📡 V2X Encryption-Delay Model — MODELED

### Equation

```text
T_total = T_enc + T_air + T_prop + T_dec
T_air   = T_phy + 8 (L + O) / R
ΔT      = T_enc + T_dec + 8 O / R
```

### Inputs

| Parameter | Value | Source |
|---|---|---|
| Radio rate R | 6 Mbps | Confirmed by Deepayan Das (baseline V2X PHY/MAC rate) |
| Message rate | 10 Hz (100 ms) standard; 20 Hz (50 ms) high-priority | Confirmed by Deepayan Das |
| PHY overhead T_phy | 40 µs | Assumption M-02 (unconfirmed) |
| Propagation T_prop | 1 µs | Assumption M-03 (about 300 m) |
| AES-GCM overhead O | 28 B | 12 B nonce + 16 B tag |
| Decrypt time T_dec | equal to T_enc | Assumption M-05 (unconfirmed) |
| T_enc | C results above (median of runs) | MEASURED (host) |

### Result

| Payload | T_enc (MEASURED) | Added delay from encryption | Total one-way delay | Added delay, % of 100 ms | Added delay, % of 50 ms |
|---|---:|---:|---:|---:|---:|
| 64 B | 0.469 µs | 38.271 µs | 164.605 µs | 0.038% | 0.077% |
| 256 B | 1.272 µs | 39.877 µs | 422.211 µs | 0.040% | 0.080% |
| 1024 B | 3.110 µs | 43.553 µs | 1449.887 µs | 0.044% | 0.087% |
| 4096 B | 11.093 µs | 59.519 µs | 5561.853 µs | 0.060% | 0.119% |

### Key findings

* Encryption adds **38 to 60 µs** per message (MODELED, 6 Mbps), under **0.12%** of the message period even at 20 Hz.
* About **37.3 µs** of the added delay is airtime for the extra 28 B. At 1024 B that is **86%** of the added delay.
* ECDH P-256 is a key-agreement step, not a per-message cost, so it is excluded from the per-message delay.
* The 4096 B row is larger than a typical V2X frame, so it is an extrapolation.

---

## 🧪 Test Run: Delay Model Output

Command run in `03_Phase2_Latency_Model`:

```text
PS ...\03_Phase2_Latency_Model> python .\v2x_delay_model.py
payload_B,t_enc_us_MEASURED,airtime_plain_us_MODEL,airtime_enc_us_MODEL,delta_us_MODEL,total_us_MODEL
64,0.469,125.333,162.667,38.271,164.605
256,1.272,381.333,418.667,39.877,422.211
1024,3.11,1405.333,1442.667,43.553,1449.887
4096,11.093,5501.333,5538.667,59.519,5561.853

Saved delay_vs_payload.png and latency_bar.png
```

Result: **PASS** (script ran without errors, reproduced `model_output.csv`, and regenerated both charts). The output matches the model table above.

Supporting screenshot:

```text
Evidence/Phase2_06_Model_Output.png
```

---

## 🛡️ STRIDE Threat Specification Update (Section 12A)

Section 12A of `01_SEC-01_STRIDE_Threat_Model.md` adds component-level trust boundaries, threat assumptions, and new threats. Earlier threat IDs are unchanged.

### Trust boundaries

| ID | Boundary | Trust level | Owner |
|---|---|---|---|
| TB-04 | Sensors → ARU MCU | Semi-trusted | Sensor interface owner (to be confirmed) |
| TB-05 | ARU MCU → HSM (SPI / I2C / CAN) | Trusted endpoints, untrusted bus | K. Mohan Krishna |
| TB-06 | ARU → V2X radio / air interface | Untrusted | Rutvika Ashtekar |
| TB-07 | ARU → Command Centre | Authenticated link assumed (A-08) | Rutvika Ashtekar / Deepayan Das |

### Assumptions and threats

* Assumptions **A-01 to A-10**, each with an owner and a way to validate it (for example nonce never reused per key, HSM register map write-protected, RNG validated, replay rejection, key rotation).
* New threats: **V2X-T-02** (AES-GCM nonce reuse), **V2X-S-02** (replay), **V2X-T-03**, **V2X-I-02**, **V2X-E-02** (HSM bus and register threats), **V2X-D-02** (jamming), **V2X-T-04** (spoofed or faulty sensor data).
* Nonce reuse under one key is treated as a critical failure: it reveals the XOR of two plaintexts and can enable forgery.

---

## 📸 Evidence

The supporting evidence is stored in:

```text
Evidence/
```

| Evidence File | Evidence |
|---|---|
| `Phase2_01_Python_Latency_Runs1-2.png` | Python benchmark, two runs (v2) |
| `Phase2_02_Host_CPU_Info.png` | Host CPU identification |
| `Phase2_02b_Python_Method_And_Scripts.png` | Python method and scripts |
| `Phase2_03_ICD_Sheet_Submission.png` | Submission to the ICD v1.1 data-collection sheet |
| `Phase2_03b_Python_Benchmark_V3.png` | Python benchmark v3 |
| `Phase2_04_C_Latency_Runs.png` | C benchmark run |
| `Phase2_05_C_Latency_Runs_2.png` | C benchmark run (continued) |
| `Phase2_06_Model_Output.png` | V2X delay model output |

Phase 1 evidence files (`Evidence_01` to `Evidence_06`, `AES-GCM_*`, `ECC_*`) are unchanged.

---

## ✅ Verification Status

| Check | Status |
|---|---|
| Python AES-GCM and ECDH latency (v2, 2 runs; v3) | Completed |
| C AES-GCM and ECDH latency (3 runs, Mbed TLS 3.6.7) | Completed |
| V2X delay model script run | PASS |
| Model charts regenerated | Completed |
| STRIDE Section 12A written | Completed |
| Telemetry latency submitted to ICD v1.1 sheet | Completed |
| Latency numbers posted in the IF-DATA group | Completed |
| Radio rate and message rates confirmed by Deepayan Das | Confirmed |
| K. Mohan Krishna review of Section 12A | **Pending** |
| Cortex-M4 latency | **Pending** |

---

## ⚠️ Measurement Limits

* All crypto timings are **host-laptop timings**. A Cortex-M4 will be slower. Do not use them as embedded timing budgets.
* The PHY overhead (40 µs) and the decrypt-equals-encrypt assumption are mine and have not been confirmed by a reviewer.
* The model ignores the MAC header, SERVICE and tail bits, and OFDM symbol rounding (assumption M-07).
* The telemetry payload size is not yet defined, so results are given for four payload sizes.
* One 1024 B run shows an outlier (4.675 µs); its minimum matches the other runs, so it is treated as system noise and kept in the data.
* An earlier pair of C runs was overwritten; only the three runs above are backed by saved files.
* Energy consumption was **not measured**.
* Phase 1 Renode functional results were **not re-verified** in Phase 2.
* AES-GCM (authenticated encryption) and ECDH P-256 (key agreement) perform different functions and are not substitutes.

---

## 🎯 Next-Task Recommendation

1. Cortex-M4 timing in Renode (cycle counts for AES-GCM and ECDH P-256), then replace the host values in the model.
2. ECDSA P-256 sign/verify benchmark (host in C, then Cortex-M4).
3. HSM-offloaded AES-GCM with Mohan's HSM state machine.
4. Nonce-management and key-rotation test with Mohan's HSM FSM.
5. Validate the model once the telemetry payload size is defined in ICD v1.1.

---

## 🎯 Task Status

**SEC-01 Phase 2 deliverables: COMPLETED, with two items pending (Mohan's review of Section 12A and Cortex-M4 timing).**

The documented results are limited to measurements actually obtained and modeled values with stated assumptions.

---

## Project / Task Information

| Field | Value |
|---|---|
| Project | SAARTHI |
| Organization | EduRankAI |
| Owner | Rutvika Ashtekar |
| Role | Cybersecurity Lead (Aerospace Security) |
| Domain | Cryptography & Threat Analysis |
| Task | SEC-01 Phase 2: AES-GCM vs ECC latency (Python/C), V2X encryption-delay model, STRIDE threat spec |
| Deliverable | Latency benchmarks + delay model + threat assumptions and trust boundaries + report |
| Assigned deadline (Phase 2) | 7 Days |

⚠️ **Note:** Host timings are not Cortex-M4 timings. Values marked MODELED depend on stated assumptions. No unverified claim is presented as a confirmed result.