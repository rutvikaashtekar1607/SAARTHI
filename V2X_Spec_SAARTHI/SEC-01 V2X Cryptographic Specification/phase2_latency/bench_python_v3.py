
import csv
import math
import os
import platform
import statistics
import time

import cryptography
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec


REPEATS = 100
AES_BATCH = 5000
ECDH_BATCH = 500
AES_WARMUP = 2000
ECDH_WARMUP = 20


def percentile_nearest_rank(values, percentile):
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def summarize(batch_means):
    return {
        "mean_us": statistics.mean(batch_means),
        "median_us": statistics.median(batch_means),
        "p99_us": percentile_nearest_rank(batch_means, 0.99),
        "max_us": max(batch_means),
    }


def benchmark(operation, warmup, repeats, batch_size):
    for _ in range(warmup):
        operation()

    batch_means = []

    for _ in range(repeats):
        start = time.perf_counter_ns()

        for _ in range(batch_size):
            operation()

        elapsed_ns = time.perf_counter_ns() - start
        batch_means.append(elapsed_ns / batch_size / 1000.0)

    return summarize(batch_means)


def main():
    results = []

    print("Measurement type: HOST COMPUTER; not Cortex-M4 timing")
    print("Python:", platform.python_version())
    print("OS:", platform.platform())
    print("Processor:", platform.processor() or "Not reported")
    print("cryptography:", cryptography.__version__)
    print("Repeats:", REPEATS)
    print("Statistics describe per-operation batch averages.")

    # Use one AES key and a unique 96-bit counter nonce for every call,
    # including warm-up calls and all payload sizes.
    aes = AESGCM(AESGCM.generate_key(bit_length=128))
    nonce_counter = 0

    def next_nonce():
        nonlocal nonce_counter
        if nonce_counter >= 2**96:
            raise RuntimeError("AES-GCM nonce counter exhausted")
        nonce = nonce_counter.to_bytes(12, "big")
        nonce_counter += 1
        return nonce

    for size in (64, 256, 1024, 4096):
        plaintext = os.urandom(size)

        def encrypt():
            nonce = next_nonce()
            aes.encrypt(nonce, plaintext, None)

        stats = benchmark(
            encrypt, AES_WARMUP, REPEATS, AES_BATCH
        )

        results.append({
            "operation": "AES-128-GCM encryption",
            "payload_bytes": size,
            "batch_calls": AES_BATCH,
            "repeats": REPEATS,
            **stats,
        })

    # ECDH key generation measured separately.
    def generate_key():
        ec.generate_private_key(ec.SECP256R1())

    stats = benchmark(
        generate_key, ECDH_WARMUP, REPEATS, ECDH_BATCH
    )
    results.append({
        "operation": "ECDH P-256 key generation",
        "payload_bytes": 0,
        "batch_calls": ECDH_BATCH,
        "repeats": REPEATS,
        **stats,
    })

    # Shared-secret calculation uses a fixed local key pair.
    private_key = ec.generate_private_key(ec.SECP256R1())
    peer_private_key = ec.generate_private_key(ec.SECP256R1())
    peer_public_key = peer_private_key.public_key()

    def derive_secret():
        private_key.exchange(ec.ECDH(), peer_public_key)

    stats = benchmark(
        derive_secret, ECDH_WARMUP, REPEATS, ECDH_BATCH
    )
    results.append({
        "operation": "ECDH P-256 shared-secret computation",
        "payload_bytes": 0,
        "batch_calls": ECDH_BATCH,
        "repeats": REPEATS,
        **stats,
    })

    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "results_python_v3.csv",
    )

    fields = [
        "operation", "payload_bytes", "batch_calls", "repeats",
        "mean_us", "median_us", "p99_us", "max_us",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for row in results:
            writer.writerow({
                key: round(value, 3) if isinstance(value, float) else value
                for key, value in row.items()
            })

    print("\nResults (microseconds):")
    for row in results:
        print(
            f"{row['operation']} | payload={row['payload_bytes']} B"
            f" | mean={row['mean_us']:.3f}"
            f" | median={row['median_us']:.3f}"
            f" | p99={row['p99_us']:.3f}"
            f" | max={row['max_us']:.3f}"
        )

    print("\nCSV saved to:", output_file)
    print("AES-GCM nonce reuse within this run: avoided.")
    print("These are host timings, not embedded-device measurements.")


if __name__ == "__main__":
    main()