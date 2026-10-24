/*
 * bench_ecdsa.c - SEC-01 Phase 3: ECDSA P-256 sign / verify latency (HOST COMPUTER).
 * Same method as bench_c.c: per-operation time = batch time / inner_calls,
 * reported as the median and minimum over repeats. Mbed TLS 3.6.x.
 * Build (MSYS2 UCRT64):  gcc -O2 bench_ecdsa.c -lmbedcrypto -o bench_ecdsa.exe
 * The SHA-256 digest of a fixed 64-byte message is computed once, outside the
 * timed loops. Only sign and verify are timed. Version line and measurement
 * label go to stderr, so the CSV stays clean.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "mbedtls/build_info.h"
#include "mbedtls/version.h"
#include "mbedtls/ecdsa.h"
#include "mbedtls/ecp.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/sha256.h"

#ifdef _WIN32
#include <windows.h>
static double now_us(void)
{
    static LARGE_INTEGER freq;
    LARGE_INTEGER t;
    if (freq.QuadPart == 0) QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&t);
    return (double)t.QuadPart * 1e6 / (double)freq.QuadPart;
}
#else
#include <time.h>
static double now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec / 1e3;
}
#endif

#define INNER_CALLS 100
#define REPEATS     15
#define WARMUP      20

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static void report(const char *op, int bytes, double *v, int n)
{
    qsort(v, n, sizeof(double), cmp_double);
    double median = (n % 2) ? v[n / 2] : 0.5 * (v[n / 2 - 1] + v[n / 2]);
    printf("%s,%d,%d,%d,%.3f,%.6f,%.3f\n", op, bytes, INNER_CALLS, REPEATS,
           median, median / 1000.0, v[0]);
}

int main(void)
{
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context drbg;
    mbedtls_ecdsa_context ctx;
    const char *pers = "sec01_phase3_ecdsa";
    unsigned char msg[64], digest[32], sig[MBEDTLS_ECDSA_MAX_LEN];
    size_t slen = 0;
    int ret, i, r;
    double times[REPEATS];

    fprintf(stderr, "Mbed TLS version: %s\n", MBEDTLS_VERSION_STRING);
    fprintf(stderr, "Measurement type: HOST COMPUTER; not Cortex-M4 timing\n");

    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&drbg);
    mbedtls_ecdsa_init(&ctx);

    ret = mbedtls_ctr_drbg_seed(&drbg, mbedtls_entropy_func, &entropy,
                                (const unsigned char *)pers, strlen(pers));
    if (ret != 0) { fprintf(stderr, "DRBG seed failed: -0x%04x\n", (unsigned)-ret); return 1; }

    ret = mbedtls_ecdsa_genkey(&ctx, MBEDTLS_ECP_DP_SECP256R1, mbedtls_ctr_drbg_random, &drbg);
    if (ret != 0) { fprintf(stderr, "ECDSA keygen failed: -0x%04x\n", (unsigned)-ret); return 1; }

    memset(msg, 0xA5, sizeof(msg));
    ret = mbedtls_sha256(msg, sizeof(msg), digest, 0);
    if (ret != 0) { fprintf(stderr, "SHA-256 failed: -0x%04x\n", (unsigned)-ret); return 1; }

    /* Correctness check before timing */
    ret = mbedtls_ecdsa_write_signature(&ctx, MBEDTLS_MD_SHA256, digest, sizeof(digest),
                                        sig, sizeof(sig), &slen,
                                        mbedtls_ctr_drbg_random, &drbg);
    if (ret != 0) { fprintf(stderr, "sign failed: -0x%04x\n", (unsigned)-ret); return 1; }
    if (mbedtls_ecdsa_read_signature(&ctx, digest, sizeof(digest), sig, slen) != 0) {
        fprintf(stderr, "CHECK FAILED: valid signature did not verify\n"); return 1;
    }
    digest[0] ^= 0x01;
    if (mbedtls_ecdsa_read_signature(&ctx, digest, sizeof(digest), sig, slen) == 0) {
        fprintf(stderr, "CHECK FAILED: tampered digest was accepted\n"); return 1;
    }
    digest[0] ^= 0x01;
    fprintf(stderr, "Correctness check: PASS (valid verifies, tampered rejected). DER signature length: %u B\n",
            (unsigned)slen);

    printf("op,bytes,inner_calls,repeats,median_us,median_ms,min_us\n");

    /* sign */
    for (i = 0; i < WARMUP; i++)
        mbedtls_ecdsa_write_signature(&ctx, MBEDTLS_MD_SHA256, digest, sizeof(digest),
                                      sig, sizeof(sig), &slen, mbedtls_ctr_drbg_random, &drbg);
    for (r = 0; r < REPEATS; r++) {
        double t0 = now_us();
        for (i = 0; i < INNER_CALLS; i++)
            mbedtls_ecdsa_write_signature(&ctx, MBEDTLS_MD_SHA256, digest, sizeof(digest),
                                          sig, sizeof(sig), &slen, mbedtls_ctr_drbg_random, &drbg);
        times[r] = (now_us() - t0) / INNER_CALLS;
    }
    report("ECDSA P-256 sign", 32, times, REPEATS);

    /* verify */
    for (i = 0; i < WARMUP; i++)
        mbedtls_ecdsa_read_signature(&ctx, digest, sizeof(digest), sig, slen);
    for (r = 0; r < REPEATS; r++) {
        double t0 = now_us();
        for (i = 0; i < INNER_CALLS; i++)
            mbedtls_ecdsa_read_signature(&ctx, digest, sizeof(digest), sig, slen);
        times[r] = (now_us() - t0) / INNER_CALLS;
    }
    report("ECDSA P-256 verify", 32, times, REPEATS);

    mbedtls_ecdsa_free(&ctx);
    mbedtls_ctr_drbg_free(&drbg);
    mbedtls_entropy_free(&entropy);
    return 0;
}