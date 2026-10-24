# Phase 3 model assumptions (SEC-01)

Labels: crypto times are MEASURED (host); M4 times are ESTIMATED; everything else is an ASSUMPTION.

| ID | Assumption | Value | Basis / owner |
|----|-----------|-------|---------------|
| P3-01 | PHY rate | 6 Mbps | Confirmed (Deepayan Das; Phase 3 PDF) |
| P3-02 | Message rates | 10 Hz (100 ms), 20 Hz (50 ms) | Confirmed (Phase 3 PDF) |
| P3-03 | PHY overhead | 40 us | 802.11p; does not apply to C-V2X PC5 framing. Rutvika |
| P3-04 | Propagation | 1 us | about 300 m. Rutvika |
| P3-05 | Telemetry payload | 64 B base case (about 48 B from x_ARU with M = 4, float32, plus header); 256 B, 1024 B sensitivity | Chosen by Rutvika; Adarsh left the choice to her |
| P3-06 | AES-GCM overhead | 28 B | 12 B nonce + 16 B tag |
| P3-07 | ECDSA signature | 64 B raw r||s | Mbed TLS writes DER (70 to 71 B); raw assumed. Verify vs IEEE 1609.2 |
| P3-08 | Signer identity | 8 B digest or 130 B certificate | Assumed; verify vs IEEE 1609.2 |
| P3-09 | Decrypt time = encrypt time | equal | Assumed |
| P3-10 | NMPC budget for comms | none | Crypto runs below GNC priority (design requirement) |
| P3-11 | Task mapping | 10 Hz on Telemetry (100 ms); 20 Hz on Communications (50 ms, priority 2) | Rakshita: periods match; priority question open |
| P3-12 | Sensing and Communications execution times | not included | Unmeasured (Rakshita) |
| P3-13 | M4 clock, CPI range | 168 MHz, 1.0 to 2.0 | Assumed; ESTIMATED only |