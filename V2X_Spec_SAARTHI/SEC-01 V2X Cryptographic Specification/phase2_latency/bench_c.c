#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include "mbedtls/gcm.h"
#include "mbedtls/ecdh.h"
#include "mbedtls/ecp.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/version.h"

#define REPEATS 15

static uint64_t now_ns(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}

static int cmp_d(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static double median(double *v, int n) {
    qsort(v, n, sizeof(double), cmp_d);
    return v[n / 2];
}

static void report(const char *op, int bytes, int inner, double *us, int n) {
    double med = median(us, n);
    printf("%s,%d,%d,%d,%.3f,%.6f,%.3f\n", op, bytes, inner, n, med, med / 1000.0, us[0]);
}

int main(void) {
    static unsigned char key[16], iv[12], in[4096], out[4096], tag[16];
    int sizes[] = {64, 256, 1024, 4096};
    const int INNER_AES = 5000, INNER_ECC = 100;
    double us[REPEATS];
    volatile unsigned char sink = 0;

    fprintf(stderr, "Mbed TLS version: %s\n", MBEDTLS_VERSION_STRING);
    fprintf(stderr, "Measurement type: HOST COMPUTER; not Cortex-M4 timing\n");
    printf("op,bytes,inner_calls,repeats,median_us,median_ms,min_us\n");

    mbedtls_gcm_context g;
    mbedtls_gcm_init(&g);
    mbedtls_gcm_setkey(&g, MBEDTLS_CIPHER_ID_AES, key, 128);

    for (int s = 0; s < 4; s++) {
        for (int i = 0; i < 2000; i++)
            mbedtls_gcm_crypt_and_tag(&g, MBEDTLS_GCM_ENCRYPT, sizes[s], iv, 12, NULL, 0, in, out, 16, tag);
        for (int r = 0; r < REPEATS; r++) {
            uint64_t t0 = now_ns();
            for (int i = 0; i < INNER_AES; i++)
                mbedtls_gcm_crypt_and_tag(&g, MBEDTLS_GCM_ENCRYPT, sizes[s], iv, 12, NULL, 0, in, out, 16, tag);
            us[r] = (now_ns() - t0) / 1000.0 / INNER_AES;
            sink ^= out[0] ^ tag[0];
        }
        report("AES-128-GCM encrypt", sizes[s], INNER_AES, us, REPEATS);
    }
    mbedtls_gcm_free(&g);

    mbedtls_entropy_context e;
    mbedtls_ctr_drbg_context d;
    mbedtls_entropy_init(&e);
    mbedtls_ctr_drbg_init(&d);
    if (mbedtls_ctr_drbg_seed(&d, mbedtls_entropy_func, &e, NULL, 0) != 0) {
        fprintf(stderr, "DRBG seed failed\n");
        return 1;
    }

    mbedtls_ecp_group grp;
    mbedtls_mpi da, dp, z;
    mbedtls_ecp_point Qa, Qp;
    mbedtls_ecp_group_init(&grp);
    mbedtls_mpi_init(&da); mbedtls_mpi_init(&dp); mbedtls_mpi_init(&z);
    mbedtls_ecp_point_init(&Qa); mbedtls_ecp_point_init(&Qp);

    if (mbedtls_ecp_group_load(&grp, MBEDTLS_ECP_DP_SECP256R1) != 0 ||
        mbedtls_ecdh_gen_public(&grp, &dp, &Qp, mbedtls_ctr_drbg_random, &d) != 0 ||
        mbedtls_ecdh_gen_public(&grp, &da, &Qa, mbedtls_ctr_drbg_random, &d) != 0) {
        fprintf(stderr, "ECC setup failed\n");
        return 1;
    }

    for (int i = 0; i < 20; i++)
        mbedtls_ecdh_gen_public(&grp, &da, &Qa, mbedtls_ctr_drbg_random, &d);
    for (int r = 0; r < REPEATS; r++) {
        uint64_t t0 = now_ns();
        for (int i = 0; i < INNER_ECC; i++)
            mbedtls_ecdh_gen_public(&grp, &da, &Qa, mbedtls_ctr_drbg_random, &d);
        us[r] = (now_ns() - t0) / 1000.0 / INNER_ECC;
    }
    report("ECDH P-256 keygen", 0, INNER_ECC, us, REPEATS);

    for (int i = 0; i < 20; i++)
        mbedtls_ecdh_compute_shared(&grp, &z, &Qp, &da, mbedtls_ctr_drbg_random, &d);
    for (int r = 0; r < REPEATS; r++) {
        uint64_t t0 = now_ns();
        for (int i = 0; i < INNER_ECC; i++)
            mbedtls_ecdh_compute_shared(&grp, &z, &Qp, &da, mbedtls_ctr_drbg_random, &d);
        us[r] = (now_ns() - t0) / 1000.0 / INNER_ECC;
    }
    report("ECDH P-256 shared secret", 0, INNER_ECC, us, REPEATS);

    return (int)(sink & 0);
}