import time, os, csv, platform, statistics
import cryptography
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec

def bench(fn, inner, repeats=30, warmup=2000):
    for _ in range(warmup): fn()
    per_call = []
    for _ in range(repeats):
        t0 = time.perf_counter_ns()
        for _ in range(inner): fn()
        per_call.append((time.perf_counter_ns() - t0) / inner / 1000.0)  # us
    per_call.sort()
    return dict(median=statistics.median(per_call), min=per_call[0],
                p95=per_call[int(0.95*(repeats-1))], inner=inner, repeats=repeats)

print("Measurement type: HOST COMPUTER; not Cortex-M4 timing")
print("Python:", platform.python_version(), "|", platform.platform())
print("Processor:", platform.processor(), "| cryptography:", cryptography.__version__)

rows = []
aes = AESGCM(AESGCM.generate_key(128)); nonce = os.urandom(12)
for size in (64, 256, 1024, 4096):
    pt = os.urandom(size)
    rows.append(("AES-128-GCM encrypt", size, bench(lambda: aes.encrypt(nonce, pt, None), 5000)))

peer = ec.generate_private_key(ec.SECP256R1()).public_key()
me = ec.generate_private_key(ec.SECP256R1())
rows.append(("ECDH P-256 keygen", 0, bench(lambda: ec.generate_private_key(ec.SECP256R1()), 500)))
rows.append(("ECDH P-256 shared secret", 0, bench(lambda: me.exchange(ec.ECDH(), peer), 500)))

with open("results_python_v2.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["op", "bytes", "inner_calls", "repeats", "median_us", "min_us", "p95_us"])
    for op, sz, r in rows:
        w.writerow([op, sz, r["inner"], r["repeats"], round(r["median"], 3), round(r["min"], 3), round(r["p95"], 3)])
        print(f"{op:26s} | {sz:5d} B | median={r['median']:.3f} us | min={r['min']:.3f} | p95={r['p95']:.3f}")