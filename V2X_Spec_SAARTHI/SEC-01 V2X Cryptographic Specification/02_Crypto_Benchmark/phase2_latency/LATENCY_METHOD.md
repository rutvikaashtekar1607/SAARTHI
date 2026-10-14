# Phase 2 Latency Benchmark — Measurement Method

## 1. Purpose

Measure preliminary host-computer execution times for AES-128-GCM encryption and ECDH P-256 operations using Python.

## 2. Environment

* Operating system: Windows 11
* Python: 3.14.7
* Cryptography package: 50.0.2
* Timer: `time.perf_counter_ns()`

## 3. Operations Measured

* AES-128-GCM encryption for 64-byte, 256-byte, and 1024-byte plaintexts.
* ECDH P-256 private-key generation.
* ECDH P-256 shared-secret computation.

AES-GCM uses a 128-bit key, a 12-byte nonce, and the library's default 16-byte authentication tag. Unique nonces are generated for each encryption operation.

## 4. Measurement Procedure

The script performs warm-up operations before measurement. It then times batches of operations and divides each batch duration by the number of operations in that batch to estimate average time per operation.

The CSV reports the mean, median, p99, and maximum of the resulting batch-average timings. These are not individual-call latency percentiles.

## 5. Results Location

`results_python.csv`

## 6. Limitations

* These are host-computer Python-library measurements, not Cortex-M4 measurements.
* Results include Python and library-call overhead.
* AES-GCM encryption timings do not represent complete V2X message-processing or radio-transmission delay.
* ECDH key generation and shared-secret computation are measured separately.
* Results are preliminary and should not be used as embedded-target performance claims.

## 7. Next Validation

Implement and measure the corresponding operations in C using the project's Mbed TLS 3.6.7 environment. Record the compiler, build configuration, target or emulator, and timing method. Do not present host timings as Cortex-M4 cycle counts.
Note: results_python.csv comes from bench_python.py (single-call timing, noisy at small payloads) and is superseded by results_python_v2.csv from bench_python_v2.py (batched timing). Cite only the v2 results.