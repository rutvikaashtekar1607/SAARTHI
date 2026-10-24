"""
parse_m4_counts.py - turn Renode marker captures into per-operation instruction counts.
Input : C:/SAARTHI_M4/m4_counts_raw.csv   (written by run_m4.resc)
Output: m4_estimates.csv (median instruction count per operation, read by e2e_delay_model.py)
        m4_counts_detail.csv (every repeat)
Instruction counts are MEASURED in Renode (instruction-accurate, not cycle-accurate).
Times derived from them are ESTIMATED (assumed 168 MHz clock and a cycles-per-instruction range).
"""
import csv, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = r"C:\SAARTHI_M4\m4_counts_raw.csv"
CLOCK_MHZ, CPI_LOW, CPI_HIGH = 168.0, 1.0, 2.0
OPS = {1: ("AES-128-GCM encrypt", 64), 2: ("AES-128-GCM encrypt", 256), 3: ("AES-128-GCM encrypt", 1024),
       4: ("ECDH P-256 keygen", 0), 5: ("ECDH P-256 shared secret", 0),
       6: ("ECDSA P-256 sign", 32), 7: ("ECDSA P-256 verify", 32)}

marks = []
with open(RAW) as f:
    for r in csv.DictReader(f):
        v, n = int(r["value"]), int(r["instr"])
        if v != 0:                      # skip the zero-initialisation write at start-up
            marks.append((v, n))

counts = {i: [] for i in OPS}
pending = {}
for v, n in marks:
    op, kind = v >> 8, v & 0xFF
    if op not in OPS:
        raise SystemExit(f"Unexpected marker value {v}")
    if kind == 1:
        pending[op] = n
    elif kind == 2:
        if op not in pending:
            raise SystemExit(f"End marker without start for op {op}")
        counts[op].append(n - pending.pop(op))

with open(os.path.join(HERE, "m4_counts_detail.csv"), "w", newline="") as fd, \
     open(os.path.join(HERE, "m4_estimates.csv"), "w", newline="") as fe:
    wd, we = csv.writer(fd), csv.writer(fe)
    wd.writerow(["op", "bytes", "repeat", "instr_count"])
    we.writerow(["op", "bytes", "instr_count"])
    print(f"{'operation':<28}{'bytes':>6}{'n':>3}{'min':>12}{'median':>12}{'max':>12}"
          f"{'ms@CPI1.0':>11}{'ms@CPI2.0':>11}")
    for i, (name, b) in OPS.items():
        c = counts[i]
        if not c:
            raise SystemExit(f"No measurements for {name} {b} B")
        for k, x in enumerate(c, 1):
            wd.writerow([name, b, k, x])
        med = statistics.median(c)
        we.writerow([name, b, int(med)])
        lo = med * CPI_LOW / CLOCK_MHZ / 1000.0
        hi = med * CPI_HIGH / CLOCK_MHZ / 1000.0
        print(f"{name:<28}{b:>6}{len(c):>3}{min(c):>12}{int(med):>12}{max(c):>12}{lo:>11.3f}{hi:>11.3f}")
print("\nWrote m4_estimates.csv and m4_counts_detail.csv")
