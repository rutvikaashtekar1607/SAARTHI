# V2X delay model assumptions (Phase 2, SEC-01)

Model: T_total = T_enc + T_air + T_prop + T_dec, with T_air = T_phy + 8(L+O)/R

Labels: crypto times are MEASURED (host laptop). Everything else in the model is an ASSUMPTION, so all delay outputs are MODELED.

| ID | Assumption | Value | Basis | Owner | Status |
|----|-----------|-------|-------|-------|--------|
| M-01 | Radio data rate (R) | 6 Mbps | Baseline for V2X PHY/MAC direct communication | Deepayan |
| M-02 | PHY overhead (T_phy) | 40 us | 32 us preamble + 8 us SIGNAL field (10 MHz OFDM) | Rutvika | To be verified against the standard |
| M-03 | Propagation delay (T_prop) | 1 us | about 300 m range | Rutvika | Assumed |
| M-04 | AES-GCM overhead (O) | 28 B | 12 B nonce + 16 B tag | Rutvika | Per AES-GCM spec |
| M-05 | Decrypt time (T_dec) | equal to encrypt time | GCM encrypt and decrypt have similar cost | Rutvika | Assumed, not measured |
| M-06 | Crypto time source (T_enc) | median of 3 host runs | MEASURED: C, Mbed TLS 3.6.7, gcc 16.2.0 -O2, i5-1135G7. NOT Cortex-M4 timing | Rutvika | Cortex-M4 timing pending |
| M-07 | MAC header, SERVICE and tail bits, OFDM symbol rounding | ignored | simplification | Rutvika | Assumed |
| M-08 | Telemetry message rate | 10 Hz (100 ms) standard telemetry, health, status; 20 Hz (50 ms) high-priority safety/emergency or swarm control | Used to express delay as a % of message period | Deepayan |
| M-09 | ECDH P-256 | excluded from per-message delay | one-time key setup, not a per-message cost | Rutvika | Design decision |