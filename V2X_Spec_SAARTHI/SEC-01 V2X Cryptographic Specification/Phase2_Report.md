# SEC-01 Phase 2 Report: Telemetry Encryption Latency, V2X Delay Model and Threat Assumptions

**Author:** Rutvika Ashtekar, Cybersecurity Lead (Aerospace Security)
**Program:** SAARTHI Engineering Program, Phase 2 (7-day milestone)
**Date:** 14 October 2026
**Task:** Benchmark AES-GCM vs ECC latency in Python/C, model V2X radio transmission encryption delay, and co-write the STRIDE threat spec.

**Labeling rule used throughout:** every number is tagged **MEASURED (host)**, **MODELED** or **ESTIMATED**. All timings were taken on a host laptop (Intel Core i5-1135G7, Windows 11). **They are not Cortex-M4 timings. Cortex-M4 latency is pending.**

---

## 1. Deliverables and GitHub Paths

Repository: https://github.com/rutvikaashtekar1607/SAARTHI (paths below are relative to the `V2X_Spec_SAARTHI` folder)

| # | Deliverable | Exact path |
|---|---|---|
| 1 | Python benchmark, method v2 | `SEC-01 V2X Cryptographic Specification/02_Crypto_Benchmark/phase2_latency/bench_python_v2.py` |
| 2 | Python results v2 (2 runs) | `SEC-01 V2X Cryptographic Specification/02_Crypto_Benchmark/phase2_latency/results_python_v2.csv` |
| 3 | Python benchmark, method v3 (100 repeats) | `SEC-01 V2X Cryptographic Specification/02_Crypto_Benchmark/phase2_latency/bench_python_v3.py` |
| 4 | Python results v3 | `SEC-01 V2X Cryptographic Specification/02_Crypto_Benchmark/phase2_latency/results_python_v3.csv` |
| 5 | Latency method description | `SEC-01 V2X Cryptographic Specification/02_Crypto_Benchmark/phase2_latency/LATENCY_METHOD.md` |
| 6 | C benchmark (Mbed TLS 3.6.7) | `SEC-01 V2X Cryptographic Specification/02_Crypto_Benchmark/phase2_latency/bench_c.c` |
| 7 | C results, runs 1 to 3 | `SEC-01 V2X Cryptographic Specification/02_Crypto_Benchmark/phase2_latency/results_c.csv`, `results_c_run2.csv`, `results_c_run3.csv` |
| 8 | V2X delay model script | `SEC-01 V2X Cryptographic Specification/03_Phase2_Latency_Model/v2x_delay_model.py` |
| 9 | Model output | `SEC-01 V2X Cryptographic Specification/03_Phase2_Latency_Model/model_output.csv` |
| 10 | Model assumptions register | `SEC-01 V2X Cryptographic Specification/03_Phase2_Latency_Model/assumptions.md` |
| 11 | Visuals | `SEC-01 V2X Cryptographic Specification/03_Phase2_Latency_Model/delay_vs_payload.png`, `latency_bar.png`, `trust_boundaries.png` |
| 12 | STRIDE spec, new Section 12A | `SEC-01 V2X Cryptographic Specification/01_SEC-01_STRIDE_Threat_Model.md` |
| 13 | This report | `SEC-01 V2X Cryptographic Specification/Phase2_Report.md` |
| 14 | Screenshot evidence |    `Evidence/Phase2_01_...` to `Evidence/Phase2_06_...`

Notes:
- `results_python.csv` is **superseded** by `results_python_v2.csv` and is not used.
- `bench_c.exe` and the Mbed TLS build folder are build artifacts and are excluded from the repository.
- Phase 1 files (Renode builds and Sections 9 to 12 of the threat model) were not changed in Phase 2 and were **not re-verified** in Phase 2.
- The telemetry latency numbers were submitted to the ICD v1.1 data-collection sheet (cell D6) on 12 October 2026. That submission carries the Python v2 results.

---

## 2. Quantified Results

### 2.1 C benchmark, MEASURED (host)

Setup: i5-1135G7, MSYS2 gcc 16.2.0 `-O2`, Mbed TLS 3.6.7. AES-128-GCM uses 5,000 calls per repeat and 15 repeats. ECDH P-256 uses 100 calls per repeat and 15 repeats. Values are median latency per operation in µs, with three saved runs.

| Operation | Run 1 | Run 2 | Run 3 | Range | Median of runs (used in model) |
|---|---|---|---|---|---|
| AES-128-GCM encrypt, 64 B | 0.534 | 0.469 | 0.235 | 0.235 to 0.534 | 0.469 |
| AES-128-GCM encrypt, 256 B | 1.413 | 1.272 | 0.751 | 0.751 to 1.413 | 1.272 |
| AES-128-GCM encrypt, 1024 B | 3.110 | 4.675 | 2.695 | 2.695 to 4.675 | 3.110 |
| AES-128-GCM encrypt, 4096 B | 11.335 | 10.994 | 11.093 | 10.994 to 11.335 | 11.093 |
| ECDH P-256 key generation | 244.242 | 224.430 | 243.612 | 224 to 244 | 243.612 |
| ECDH P-256 shared secret | 709.591 | 670.224 | 648.928 | 649 to 710 | 670.224 |

Reading the table:
- 4096 B AES-GCM and both ECDH operations agree within about 10% across runs.
- 64 B and 256 B timings vary by up to 2x. Each call takes under a microsecond, so timer resolution and system noise dominate. They are reported as ranges.
- 1024 B includes one outlier (4.675 µs). Its `min_us` value (2.5 µs) matches the other runs, so the outlier is treated as system noise. It is kept in the data and not removed.
- An earlier pair of C runs was overwritten when the CSVs were regenerated. Only the three runs above are backed by saved files.

### 2.2 Python benchmark, MEASURED (host)

Python 3.14.7, `cryptography` 50.0.2 (OpenSSL backend). Median latency per operation in µs.

| Operation | v2 run 1 | v2 run 2 | v3 (100 repeats) |
|---|---|---|---|
| AES-128-GCM encrypt, 64 B | 1.052 | 0.780 | 2.696 |
| AES-128-GCM encrypt, 256 B | 0.893 | 0.882 | 1.322 |
| AES-128-GCM encrypt, 1024 B | 0.997 | 0.920 | 1.827 |
| AES-128-GCM encrypt, 4096 B | 1.402 | 1.309 | 2.980 |
| ECDH P-256 key generation | 16.532 | 16.380 | 22.891 |
| ECDH P-256 shared secret | 51.255 | 53.298 | 60.027 |

Reading the table:
- Python AES-GCM times are about 1 to 3 µs and include Python call overhead. The 64 B value in v3 is larger than the 256 B value, which cannot be a real effect, so small-payload timings are noise-limited.
- Python ECDH is about 16 to 23 µs for key generation and 51 to 60 µs for the shared secret.
- v2 and v3 differ because of method and system load. No single cause is claimed.

### 2.3 Python vs C

The Python and C results differ because they use **different library implementations** (OpenSSL via `cryptography` vs the Mbed TLS package). The comparison is not a language comparison. Both are host timings. The delay model uses the C numbers, because Mbed TLS is the library used for the embedded target in Phase 1.

### 2.4 V2X delay model, MODELED

Inputs: radio rate 6 Mbps, PHY overhead 40 µs, propagation 1 µs, AES-GCM overhead 28 B, decrypt time equal to encrypt time, and crypto times from the C results above (median of runs).

| Payload | T_enc (MEASURED) | Airtime plain | Airtime encrypted | Added delay from encryption | Total one-way delay |
|---|---|---|---|---|---|
| 64 B | 0.469 µs | 125.333 µs | 162.667 µs | 38.271 µs | 164.605 µs |
| 256 B | 1.272 µs | 381.333 µs | 418.667 µs | 39.877 µs | 422.211 µs |
| 1024 B | 3.110 µs | 1405.333 µs | 1442.667 µs | 43.553 µs | 1449.887 µs |
| 4096 B | 11.093 µs | 5501.333 µs | 5538.667 µs | 59.519 µs | 5561.853 µs |

Share of the message period (MODELED), using the rates confirmed by Deepayan Das: 10 Hz (100 ms) for standard telemetry, health and status, and 20 Hz (50 ms) for high-priority safety, emergency or swarm-control messages.

| Payload | Added delay, % of 100 ms | Added delay, % of 50 ms | Total delay, % of 100 ms | Total delay, % of 50 ms |
|---|---|---|---|---|
| 64 B | 0.038% | 0.077% | 0.165% | 0.329% |
| 256 B | 0.040% | 0.080% | 0.422% | 0.844% |
| 1024 B | 0.044% | 0.087% | 1.450% | 2.900% |
| 4096 B | 0.060% | 0.119% | 5.562% | 11.124% |

### 2.5 Key findings

1. Encryption adds **38 to 60 µs** per message in the model (MODELED, at 6 Mbps), which is **under 0.12%** of the message period even at 20 Hz.
2. About **37.3 µs** of the added delay is airtime for the extra 28 B (nonce and tag). At 1024 B that is **86%** of the added delay. The host-measured cipher time (encrypt plus decrypt) is only about 6.2 µs.
3. ECDH P-256 is a key-agreement step, not a per-message cost, so it is excluded from the per-message delay. On the host (C) it takes about 0.22 to 0.24 ms for key generation and 0.65 to 0.71 ms for the shared secret (MEASURED).
4. AES-GCM (authenticated encryption) and ECDH P-256 (key agreement) perform different functions and are not substitutes.
5. The 4096 B row is larger than a typical V2X frame, so it is an extrapolation.

### 2.6 Limitations

- All crypto timings are host-laptop timings. **A Cortex-M4 will be slower.** Cortex-M4 latency is **pending**, and the model is not an embedded timing budget.
- The PHY overhead (40 µs) and decrypt-equals-encrypt assumption are mine and have not been confirmed by a reviewer. The 6 Mbps rate and the message rates are confirmed by Deepayan Das.
- The model ignores the MAC header, SERVICE and tail bits, and OFDM symbol rounding (assumption M-07).
- The telemetry payload size is not yet defined, so results are given for four payload sizes.
- Energy consumption was not measured.

---

## 3. Code and Math

### 3.1 Benchmark method (summary)

Each reported value is the **median over repeats** of the per-operation time, where per-operation time = batch time / calls per batch.

| Benchmark | Calls per repeat | Repeats | Timer / notes |
|---|---|---|---|
| C, AES-128-GCM | 5,000 | 15 | Mbed TLS 3.6.7, gcc -O2 (`bench_c.c`) |
| C, ECDH P-256 | 100 | 15 | keygen and shared secret timed separately |
| Python v2 | 5,000 (AES), 500 (ECDH) | 30 | `time.perf_counter_ns()`, 2,000-call warm-up |
| Python v3 | see `LATENCY_METHOD.md` | 100 | mean, median, p99, max; nonce-reuse check |

Full code: `bench_c.c`, `bench_python_v2.py`, `bench_python_v3.py`.

### 3.2 V2X delay equation

$$T_{total} = T_{enc} + T_{air} + T_{prop} + T_{dec}$$

$$T_{air} = T_{phy} + \frac{8\,(L + O)}{R}$$

Added delay caused by encryption:

$$\Delta T = T_{enc} + T_{dec} + \frac{8\,O}{R}$$

where $L$ is the payload in bytes, $O = 28$ B (12 B nonce + 16 B tag), $R = 6$ Mbps, $T_{phy} = 40\ \mu s$, and $T_{prop} = 1\ \mu s$.

Worked example, $L = 1024$ B, with $T_{enc} = T_{dec} = 3.110\ \mu s$:

- Plain airtime: $40 + 8 \cdot 1024 / 6 = 1405.333\ \mu s$
- Encrypted airtime: $40 + 8 \cdot 1052 / 6 = 1442.667\ \mu s$
- $\Delta T = 3.110 + 3.110 + 37.333 = 43.553\ \mu s$
- $T_{total} = 3.110 + 1442.667 + 1 + 3.110 = 1449.887\ \mu s$

### 3.3 Model code (excerpt from `v2x_delay_model.py`)

```python
RATE_MBPS = 6.0    # confirmed by Deepayan Das
T_PHY_US = 40.0    # 32 us preamble + 8 us SIGNAL (assumption M-02)
T_PROP_US = 1.0    # about 300 m (assumption M-03)
OVERHEAD_B = 28    # 12 B nonce + 16 B tag
T_DEC = t_enc      # decrypt time assumed equal to encrypt time (M-05)

for L, te in sorted(t_enc.items()):
    plain = T_PHY_US + 8 * L / RATE_MBPS
    enc = T_PHY_US + 8 * (L + OVERHEAD_B) / RATE_MBPS
    delta = te + T_DEC[L] + (enc - plain)
    total = te + enc + T_PROP_US + T_DEC[L]
```

### 3.4 Why nonce reuse matters (security math)

AES-GCM encrypts by XOR with a keystream $KS$ derived from the key and nonce. If two messages use the same key and nonce:

$$C_1 \oplus C_2 = (P_1 \oplus KS) \oplus (P_2 \oplus KS) = P_1 \oplus P_2$$

This leaks the relationship between the plaintexts and also allows recovery of the GCM authentication key, so an attacker can forge messages. It is recorded as threat V2X-T-02 in Section 12A of the STRIDE spec, with assumptions A-01 and A-09.

---

## 4. Visual Assets

**Figure 1: Added delay from encryption vs payload (MODELED, 6 Mbps)**
![Added delay vs payload](SEC-01%20V2X%20Cryptographic%20Specification/03_Phase2_Latency_Model/delay_vs_payload.png)

**Figure 2: AES-GCM vs ECDH P-256 latency, log scale (MEASURED, host, C, Mbed TLS 3.6.7)**
![Latency bar chart](SEC-01%20V2X%20Cryptographic%20Specification/03_Phase2_Latency_Model/latency_bar.png)

**Figure 3: Trust boundaries TB-04 to TB-07 (STRIDE spec Section 12A)**
![Trust boundaries](SEC-01%20V2X%20Cryptographic%20Specification/03_Phase2_Latency_Model/trust_boundaries.png)

Terminal evidence: `Evidence/Phase2_04_C_Latency_Runs.png`, `Evidence/Phase2_05_C_Latency_Runs_2.png`, `Evidence/Phase2_06_Model_Output.png`.

---

## 5. References and Cross-Lead Collaboration

### 5.1 References

- [Ref: 1-Week Online Task Allocation, SAARTHI Program Phase 2 Milestone]: task definition and 7-day deadline.
- [Ref: Technical Leadership & Subsystem Progress Report, SAARTHI Engineering Program]: Phase 2 scope.
- [Ref: SEC-01 STRIDE Threat Model, `01_SEC-01_STRIDE_Threat_Model.md`]: baseline threats V2X-S-01 to V2X-E-01 and trust boundaries TB-01 to TB-03.
- [Ref: `LATENCY_METHOD.md`]: benchmark method.
- [Ref: `assumptions.md`, 03_Phase2_Latency_Model]: model assumptions M-01 to M-09.
- [Ref: NIST SP 800-38D, Recommendation for GCM and GMAC]: GCM nonce and tag requirements.
- [Ref: IEEE 802.11p, 10 MHz OFDM PHY]: basis for the 6 Mbps rate and the PHY overhead.

### 5.2 Cross-lead collaboration

| Lead | Collaboration | Status |
|---|---|---|
| Deepayan Das (Systems Integration) | Confirmed 6 Mbps as the baseline V2X PHY/MAC rate, 10 Hz (100 ms) for standard telemetry, and 20 Hz (50 ms) for high-priority messages | **Confirmed in the team chat, 13 Oct 2026** |
| K. Mohan Krishna (Hardware Security) | Joint threat assumptions and boundaries: TB-05 (MCU to HSM), A-01 to A-04 and A-09, HSM threats V2X-T-02, T-03, I-02, E-02 | Pending Mohan's review (confirmation to be added) |
| Smrithi (APM) | Telemetry latency submitted to ICD v1.1 sheet, cell D6 | **Submitted 12 Oct 2026** |

---

## 6. Next-Task Recommendation

1. **Cortex-M4 timing in Renode.** Measure AES-GCM and ECDH P-256 latency on the STM32F4 target (cycle counts) and replace the host values in the delay model. This closes the main limitation of this report.
2. **ECDSA P-256 sign/verify benchmark** (host in C, then Cortex-M4). V2X messages need sender authentication, which AES-GCM does not provide on its own.
3. **HSM-offloaded AES-GCM** with Mohan's HSM state machine. Compare latency and bus overhead of HSM calls over SPI, I2C or CAN with software AES-GCM.
4. **Nonce-management and key-rotation test** with Mohan's HSM FSM. Verify a persistent nonce counter across reboot and power loss (A-01, A-09), and test replay rejection (A-07).
5. **Validate the model** with the telemetry payload size once it is defined in ICD v1.1, and confirm the PHY overhead and decrypt-time assumptions.

---

## Status of Open Items

| Item | Status |
|---|---|
| Cortex-M4 timing | Pending (not part of this milestone) |
| Mohan review of Section 12A | Pending |
| Telemetry payload size | To be defined with ICD v1.1 |
| PHY overhead and decrypt-time assumptions | Unconfirmed assumptions |