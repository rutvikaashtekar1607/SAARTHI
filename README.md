# SAARTHI — SEC-01 Crypto Benchmark

**Project:** SAARTHI
**Organization:** EduRankAI
**Owner:** Rutvika Ashtekar
**Role:** Cybersecurity Lead
**Domain:** Cryptography & Threat Analysis
**Task Reference:** SEC-01 — V2X Cryptographic Specification (per SAARTHI Phase 1 Task Allocation Matrix)

---

## 📌 What Is SAARTHI

SAARTHI is an autonomous public-mobility, public-management, and distributed infrastructure system designed as an interoperable digital coordination layer across urban infrastructure. It connects road traffic, public transit, parking hubs, emergency dispatch, and civic reporting into a single federated operational view, without replacing existing municipal applications.

## 📌 Purpose of This Folder

This folder contains the cryptographic benchmark work for the **SEC-01 V2X Cryptographic Specification**, assigned under SAARTHI Phase 1.

The assigned task is to:

- Author the SEC-01 threat model.
- Establish STRIDE vulnerability vectors for V2X telemetry.
- Run cryptographic benchmarks for **AES-GCM vs. ECC**.

For the ECC benchmark, **ECDH using P-256 / secp256r1** is used.

---

## 📁 Folder Contents

| File / Folder | Purpose |
|---|---|
| `README.md` | Benchmark documentation |
| `aes_gcm_benchmark.c` | AES-128-GCM benchmark implementation |
| `aes_gcm_benchmark.elf` | Compiled AES-GCM firmware |
| `aes_gcm_benchmark.map` | AES-GCM linker/map information |
| `aes_gcm_benchmark.o` | AES-GCM object file |
| `ecc_benchmark.c` | ECDH P-256 benchmark implementation |
| `ecc_benchmark.elf` | Compiled ECC benchmark firmware |
| `ecc_benchmark.o` | ECC object file |
| `benchmark_results.md` | Recorded benchmark results |
| `mbedtls_benchmark_config.h` | Benchmark configuration |
| `arm-none-eabi-toolchain.cmake` | ARM cross-compilation configuration |
| `platform/` | STM32F4 startup and linker files |
| `mbedtls-3.6.7/` | Mbed TLS 3.6.7 source and build files |

The main SEC-01 specification is located one level above this folder:

```text
01_SEC-01_STRIDE_Threat_Model.md
```

---

## 🛠️ Benchmark Environment

| Item                  | Used                     |
| --------------------- | ------------------------ |
| Target architecture   | ARM Cortex-M4 / STM32F4  |
| Execution environment | Renode 1.16.0            |
| Cryptographic library | Mbed TLS 3.6.7           |
| Compiler              | Arm GNU Toolchain 12.2.1 |

---

## 🔐 AES-128-GCM Benchmark

### Operation

* 1024-byte authenticated encryption
* 128-bit key
* 96-bit nonce
* 128-bit authentication tag

### Result

| Metric               |   Result |
| -------------------- | -------: |
| Functional execution |     PASS |
| Status code          |        0 |
| Code (`.text`)       | 14,020 B |
| Data (`.data`)       |      4 B |
| BSS                  | 27,248 B |
| Static RAM           | 27,252 B |
| Total image size     | 41,272 B |

---

## 🔑 ECDH P-256 Benchmark

### Operation

* ECDH key generation
* Shared-secret computation
* Curve: P-256 / secp256r1

### Result

| Metric               |   Result |
| -------------------- | -------: |
| Functional execution |     PASS |
| Status code          |        0 |
| Code (`.text`)       | 36,428 B |
| Data (`.data`)       |      8 B |
| BSS                  | 16,416 B |
| Static RAM           | 16,424 B |
| Total image size     | 52,852 B |

### ECC Functional Evidence

The ECC benchmark was executed in Renode and completed successfully.

Recorded Renode values:

```text
sysbus ReadDoubleWord 0x20004008
0x00003FF8

sysbus ReadDoubleWord 0x2000400C
0x00000000
```

Interpretation:

* `benchmark_done` was non-zero, showing that execution reached completion.
* `benchmark_status` was `0`, showing successful execution.
* `0x00003FF8` is a completion marker value and is **not a cycle count**.

Supporting screenshot:

```text
Evidence/ECC_Renode_Functional_Evidence.png
```

---

## 📊 AES-GCM vs. ECDH P-256

| Metric               |              AES-128-GCM |    ECDH P-256 |
| -------------------- | -----------------------: | ------------: |
| Functional execution |                     PASS |          PASS |
| Code size            |                 14,020 B |      36,428 B |
| Static RAM           |                 27,252 B |      16,424 B |
| Primary purpose      | Authenticated encryption | Key agreement |

AES-GCM and ECDH P-256 have different cryptographic purposes.

* **AES-GCM** provides authenticated encryption.
* **ECDH P-256** provides key agreement.

They are therefore used for different security functions.

---

## 📸 Evidence

The supporting evidence is stored in:

```text
V2X_Spec_SAARTHI/Evidence/
```

| Evidence File                                | Evidence                              |
| --------------------------------------------- | -------------------------------------- |
| `Evidence_01_MbedTLS_Build_Success.png`      | Mbed TLS build success                |
| `Evidence_02_ARM_GNU_Toolchain.png`          | ARM GNU Toolchain                     |
| `Evidence_03_AES_GCM_Firmware_Build.png`     | AES-GCM firmware build                |
| `Evidence_04_Renode_ELF_Load.png`            | Renode ELF loading                    |
| `Evidence_05_Renode_Data_Initialization.png` | Renode data initialization            |
| `Evidence_06_AES_GCM_Renode_Execution.png`   | AES-GCM Renode execution              |
| `AES-GCM_Functional_Verification_Renode.png` | AES-GCM functional verification       |
| `AES-GCM_Code_Size_RAM_Measurement.png`      | AES-GCM code-size and RAM measurement |
| `AES-GCM_Renode_Total_Instruction_Count.png` | Recorded total instruction count      |
| `ECC_Renode_Functional_Evidence.png`         | ECC functional execution evidence     |

---

## ✅ Verification Status

| Check                             | Status    |
| --------------------------------- | --------- |
| AES-GCM compilation               | Completed |
| AES-GCM functional execution      | PASS      |
| ECDH P-256 compilation            | Completed |
| ECDH P-256 functional execution   | PASS      |
| AES-GCM code-size measurement     | Completed |
| AES-GCM static-RAM measurement    | Completed |
| ECDH P-256 code-size measurement  | Completed |
| ECDH P-256 static-RAM measurement | Completed |
| Benchmark results documented      | Completed |
| Supporting evidence collected     | Completed |

---

## ⚠️ Measurement Limits

The completed benchmark work reports:

* Functional execution
* Code size
* Static RAM

Energy consumption was **not measured** during the completed benchmark runs, so no energy result is reported.

No unsupported cycle count or performance value is reported as a confirmed result.

The AES-GCM total instruction count screenshot is retained as supporting evidence, but it is **not presented as an AES-GCM-specific cycle measurement**.

---

## 📌 SEC-01 Deliverable

The main SEC-01 specification is:

```text
V2X_Spec_SAARTHI/
└── SEC-01 V2X Cryptographic Specification/
    ├── 01_SEC-01_STRIDE_Threat_Model.md
    └── 02_Crypto_Benchmark/
        ├── README.md
        └── benchmark_results.md
```

The main specification contains:

* V2X threat model
* STRIDE vulnerability vectors
* Security requirements
* Cryptographic security requirements
* Benchmark methodology
* AES-GCM results
* ECDH P-256 results
* AES-GCM vs. ECDH P-256 comparison
* Verification status

The `Evidence/` folder contains the supporting screenshots for the completed benchmark work.

---

## 🎯 Task Status

**SEC-01 Phase 1 cryptographic benchmark work: COMPLETED**

The documented results are limited to measurements actually obtained and verified in the benchmark environment.

---

## Project / Task Information

| Field | Value |
|---|---|
| Project | SAARTHI |
| Organization | EduRankAI *(team-used identity, not from the official PDF)* |
| Owner | Rutvika Ashtekar |
| Role | Cybersecurity Lead |
| Domain | Cryptography & Threat Analysis |
| Task | SEC-01 — V2X Cryptographic Specification |
| Deliverable | V2X Cryptographic Spec (threat model + STRIDE vectors + AES-GCM vs. ECC benchmarks) |
| Assigned deadline (Phase 1) | 4 Days |

⚠️ **Note:** All content above reflects only what was actually built, measured, and verified in this benchmark environment. No unverified claims, cycle counts, or energy figures are presented as confirmed results.
