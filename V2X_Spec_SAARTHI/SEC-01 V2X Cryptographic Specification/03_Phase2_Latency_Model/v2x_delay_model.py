import csv, os, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "02_Crypto_Benchmark", "phase2_latency")
FILES = ["results_c.csv", "results_c_run2.csv", "results_c_run3.csv"]

# MEASURED (host laptop, C, Mbed TLS 3.6.7, gcc -O2): median of the 3 run medians
vals = {}
for fn in FILES:
    with open(os.path.join(SRC, fn)) as f:
        for r in csv.DictReader(f):
            vals.setdefault((r["op"], int(r["bytes"])), []).append(float(r["median_us"]))
meas = {k: statistics.median(v) for k, v in vals.items()}
t_enc = {b: v for (op, b), v in meas.items() if op.startswith("AES-128-GCM")}

# ASSUMPTIONS (see assumptions.md; to be confirmed with Deepayan)
RATE_MBPS = 6.0    # 802.11p-style 10 MHz data rate
T_PHY_US = 40.0    # 32 us preamble + 8 us SIGNAL (10 MHz OFDM)
T_PROP_US = 1.0    # about 300 m range
OVERHEAD_B = 28    # 12 B nonce + 16 B tag
T_DEC = t_enc      # decrypt time assumed equal to encrypt time

rows = []
for L, te in sorted(t_enc.items()):
    plain = T_PHY_US + 8 * L / RATE_MBPS
    enc = T_PHY_US + 8 * (L + OVERHEAD_B) / RATE_MBPS
    delta = te + T_DEC[L] + (enc - plain)
    total = te + enc + T_PROP_US + T_DEC[L]
    rows.append((L, te, plain, enc, delta, total))

out = os.path.join(HERE, "model_output.csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["payload_B", "t_enc_us_MEASURED", "airtime_plain_us_MODEL",
                "airtime_enc_us_MODEL", "delta_us_MODEL", "total_us_MODEL"])
    for r in rows:
        w.writerow([r[0]] + [round(x, 3) for x in r[1:]])
print(open(out).read())

# Visual 1: added delay vs payload (MODELED)
plt.figure()
plt.plot([r[0] for r in rows], [r[4] for r in rows], marker="o")
plt.xlabel("Payload (B)")
plt.ylabel("Added delay from encryption (us)")
plt.title(f"V2X encryption-added delay at {RATE_MBPS} Mbps (MODELED)")
plt.grid(True)
plt.savefig(os.path.join(HERE, "delay_vs_payload.png"), dpi=150)

# Visual 2: latency bar chart (MEASURED, host)
labels = ["AES-128-GCM\n1024 B", "ECDH P-256\nkeygen", "ECDH P-256\nshared secret"]
data = [meas[("AES-128-GCM encrypt", 1024)],
        meas[("ECDH P-256 keygen", 0)],
        meas[("ECDH P-256 shared secret", 0)]]
plt.figure()
bars = plt.bar(labels, data)
plt.yscale("log")
plt.ylabel("Median latency (us, log scale)")
plt.title("C / Mbed TLS 3.6.7 latency (MEASURED, host laptop)")
for b, v in zip(bars, data):
    plt.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}", ha="center", va="bottom")
plt.savefig(os.path.join(HERE, "latency_bar.png"), dpi=150)
print("Saved delay_vs_payload.png and latency_bar.png")