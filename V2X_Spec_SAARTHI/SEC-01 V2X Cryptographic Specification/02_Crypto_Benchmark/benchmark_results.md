# SEC-01 Cryptographic Benchmark Results

## 1. Benchmark Scope

The SEC-01 benchmark compares:

- AES-128-GCM
- ECDH using P-256 / secp256r1

Target architecture: ARM Cortex-M4 / STM32F4  
Execution environment: Renode 1.16.0  
Cryptographic library: Mbed TLS 3.6.7

## 2. AES-128-GCM Results

**Operation:** 1024-byte authenticated encryption  
**Key size:** 128-bit  
**Nonce:** 96-bit  
**Authentication tag:** 128-bit

| Metric | Result |
|---|---:|
| Functional execution | PASS |
| Status code | 0 |
| Code (.text) | 14,020 B |
| Data (.data) | 4 B |
| BSS | 27,248 B |
| Static RAM | 27,252 B |
| Total image size | 41,272 B |

## 3. ECDH P-256 Results

**Operation:** ECDH key generation and shared-secret computation  
**Curve:** P-256 / secp256r1

| Metric | Result |
|---|---:|
| Functional execution | PASS |
| Status code | 0 |
| Code (.text) | 36,428 B |
| Data (.data) | 8 B |
| BSS | 16,416 B |
| Static RAM | 16,424 B |
| Total image size | 52,852 B |

## 4. AES-GCM vs ECDH Comparison

| Metric | AES-128-GCM | ECDH P-256 |
|---|---:|---:|
| Functional execution | PASS | PASS |
| Code size | 14,020 B | 36,428 B |
| Static RAM | 27,252 B | 16,424 B |
| Primary purpose | Encryption and authentication | Key agreement |

AES-GCM and ECDH provide different security functions. AES-GCM provides authenticated encryption for V2X data, while ECDH P-256 provides key agreement for establishing shared cryptographic keys.

## 5. Verification Status

Both benchmark implementations compiled successfully and completed functional execution in the Renode STM32F4 environment.

The reported code-size, RAM, and functional results are measured results from the benchmark builds.

No unsupported performance or energy value is reported.