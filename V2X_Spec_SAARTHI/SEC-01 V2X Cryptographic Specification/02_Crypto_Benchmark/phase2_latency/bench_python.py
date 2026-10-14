
import csv
import os
import platform
import statistics
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec



def benchmark(operation, iterations, warmup=200, batch_size=20):
    """Measure host latency using batches to reduce timer overhead."""
    for _ in range(warmup):
        operation()

    batch_means_us = []
    timings_us = []

    completed = 0
    while completed < iterations:
        current_batch = min(batch_size, iterations - completed)

        start = time.perf_counter_ns()
        for _ in range(current_batch):
            operation()
        elapsed_ns = time.perf_counter_ns() - start

        # Estimate per-operation latency from the batch duration.
        per_operation_us = elapsed_ns / current_batch / 1000
        batch_means_us.append(per_operation_us)
        timings_us.append(per_operation_us)
        completed += current_batch

    timings_us.sort()

    return {
        "iterations": iterations,
        "mean_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
        "p99_us": timings_us[
            min(len(timings_us) - 1, int(len(timings_us) * 0.99))
        ],
        "max_us": timings_us[-1],
    }

def main():
    results = []

    # AES-128-GCM encryption: 12-byte nonce and 16-byte authentication tag.
    key = AESGCM.generate_key(bit_length=128)
    aes = AESGCM(key)

    
    for size in (64, 256, 1024):
        plaintext = os.urandom(size)

                # Pre-generate unique nonces outside the timed operation.
        nonces = [os.urandom(12) for _ in range(5200)]
        nonce_index = iter(nonces)

        result = benchmark(
            lambda: aes.encrypt(next(nonce_index), plaintext, None),
            iterations=5000,
        )

        results.append({
            "operation": "AES-128-GCM encryption",
            "payload_bytes": size,
            **result,
        })

    # ECDH P-256 key generation: measure generation of a new private key.
    result = benchmark(
        lambda: ec.generate_private_key(ec.SECP256R1()),
        iterations=500,
        warmup=20,
    )

    results.append({
        "operation": "ECDH P-256 key generation",
        "payload_bytes": 0,
        **result,
    })

    # ECDH P-256 shared-secret computation, measured separately.
    private_key = ec.generate_private_key(ec.SECP256R1())
    peer_private_key = ec.generate_private_key(ec.SECP256R1())
    peer_public_key = peer_private_key.public_key()

    result = benchmark(
        lambda: private_key.exchange(ec.ECDH(), peer_public_key),
        iterations=500,
        warmup=20,
    )

    results.append({
        "operation": "ECDH P-256 shared-secret computation",
        "payload_bytes": 0,
        **result,
    })

    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_python.csv")
    fields = [
        "operation",
        "payload_bytes",
        "iterations",
        "mean_us",
        "median_us",
        "p99_us",
        "max_us",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for row in results:
            formatted = {
                key: round(value, 3) if isinstance(value, float) else value
                for key, value in row.items()
            }
            writer.writerow(formatted)

    print("Measurement type: HOST COMPUTER; not Cortex-M4 timing")
    print("Python:", platform.python_version())
    print("Operating system:", platform.platform())
    print("Processor:", platform.processor() or "Not reported by operating system")
    print("Cryptography package:", __import__("cryptography").__version__)
    print("\nResults (microseconds):")

    for row in results:
        print(
            f"{row['operation']} | payload={row['payload_bytes']} B"
            f" | mean={row['mean_us']:.3f} us"
            f" | median={row['median_us']:.3f} us"
            f" | p99={row['p99_us']:.3f} us"
        )

    print(f"\nCSV saved to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    main()