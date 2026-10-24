/*
 * m4_bench.c - SEC-01 Phase 3: one-shot operation markers for Renode instruction counting.
 * Each operation is run once as warm-up, then REPEATS times between a start marker and an
 * end marker (writes to bench_marker). Renode hooks on bench_marker read the executed
 * instruction count at each marker. The RNG below is NOT secure; it is for timing only.
 */
#include <stdint.h>
#include <string.h>
#include "mbedtls/gcm.h"
#include "mbedtls/ecp.h"
#include "mbedtls/ecdh.h"
#include "mbedtls/ecdsa.h"
#include "mbedtls/sha256.h"

#define REPEATS 5
#define MARK_START(id) (bench_marker = ((uint32_t)(id) << 8) | 1u)
#define MARK_END(id)   (bench_marker = ((uint32_t)(id) << 8) | 2u)

volatile uint32_t bench_marker = 0;
volatile uint32_t bench_status = 0;   /* 0 = all checks passed */
volatile uint32_t bench_done = 0;

static uint32_t rng_state = 0x12345678u;
static int fake_rng(void *p, unsigned char *out, size_t len)
{
    (void)p;
    for (size_t i = 0; i < len; i++) {
        rng_state ^= rng_state << 13; rng_state ^= rng_state >> 17; rng_state ^= rng_state << 5;
        out[i] = (unsigned char)(rng_state & 0xFF);
    }
    return 0;
}

static void check(int ret)
{
    if (ret != 0 && bench_status == 0) bench_status = (uint32_t)(-ret);
}

static uint8_t buf_in[1024], buf_out[1024], tag[16], key[16], nonce[12];

int main(void)
{
    static const size_t sizes[3] = {64, 256, 1024};
    int ret, i, s;

    memset(buf_in, 0x41, sizeof(buf_in));

    /* ---- AES-128-GCM (ids 1..3 = 64 B, 256 B, 1024 B); key set once outside the timed region ---- */
    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    check(mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, key, 128));
    for (s = 0; s < 3; s++) {
        check(mbedtls_gcm_crypt_and_tag(&gcm, MBEDTLS_GCM_ENCRYPT, sizes[s], nonce, sizeof(nonce),
                                        NULL, 0, buf_in, buf_out, sizeof(tag), tag));   /* warm-up */
        for (i = 0; i < REPEATS; i++) {
            MARK_START(1 + s);
            ret = mbedtls_gcm_crypt_and_tag(&gcm, MBEDTLS_GCM_ENCRYPT, sizes[s], nonce, sizeof(nonce),
                                            NULL, 0, buf_in, buf_out, sizeof(tag), tag);
            MARK_END(1 + s);
            check(ret);
        }
    }
    mbedtls_gcm_free(&gcm);

    /* ---- ECDH P-256 (id 4 = keygen, id 5 = shared secret) ---- */
    mbedtls_ecp_group grp;
    mbedtls_mpi d, dp, z;
    mbedtls_ecp_point Q, Qp;
    mbedtls_ecp_group_init(&grp);
    mbedtls_mpi_init(&d); mbedtls_mpi_init(&dp); mbedtls_mpi_init(&z);
    mbedtls_ecp_point_init(&Q); mbedtls_ecp_point_init(&Qp);
    check(mbedtls_ecp_group_load(&grp, MBEDTLS_ECP_DP_SECP256R1));
    check(mbedtls_ecdh_gen_public(&grp, &dp, &Qp, fake_rng, NULL));      /* peer key, not timed */
    check(mbedtls_ecdh_gen_public(&grp, &d, &Q, fake_rng, NULL));        /* warm-up */
    for (i = 0; i < REPEATS; i++) {
        MARK_START(4);
        ret = mbedtls_ecdh_gen_public(&grp, &d, &Q, fake_rng, NULL);
        MARK_END(4);
        check(ret);
    }
    check(mbedtls_ecdh_compute_shared(&grp, &z, &Qp, &d, fake_rng, NULL)); /* warm-up */
    for (i = 0; i < REPEATS; i++) {
        MARK_START(5);
        ret = mbedtls_ecdh_compute_shared(&grp, &z, &Qp, &d, fake_rng, NULL);
        MARK_END(5);
        check(ret);
    }

    /* ---- ECDSA P-256 (id 6 = sign, id 7 = verify), digest of a fixed 64 B message ---- */
    mbedtls_ecdsa_context ctx;
    unsigned char msg[64], digest[32], sig[MBEDTLS_ECDSA_MAX_LEN];
    size_t slen = 0;
    mbedtls_ecdsa_init(&ctx);
    check(mbedtls_ecdsa_genkey(&ctx, MBEDTLS_ECP_DP_SECP256R1, fake_rng, NULL));
    memset(msg, 0xA5, sizeof(msg));
    check(mbedtls_sha256(msg, sizeof(msg), digest, 0));
    check(mbedtls_ecdsa_write_signature(&ctx, MBEDTLS_MD_SHA256, digest, sizeof(digest),
                                        sig, sizeof(sig), &slen, fake_rng, NULL));   /* warm-up */
    for (i = 0; i < REPEATS; i++) {
        MARK_START(6);
        ret = mbedtls_ecdsa_write_signature(&ctx, MBEDTLS_MD_SHA256, digest, sizeof(digest),
                                            sig, sizeof(sig), &slen, fake_rng, NULL);
        MARK_END(6);
        check(ret);
    }
    check(mbedtls_ecdsa_read_signature(&ctx, digest, sizeof(digest), sig, slen));   /* warm-up */
    for (i = 0; i < REPEATS; i++) {
        MARK_START(7);
        ret = mbedtls_ecdsa_read_signature(&ctx, digest, sizeof(digest), sig, slen);
        MARK_END(7);
        check(ret);
    }
    /* correctness: a tampered digest must be rejected */
    digest[0] ^= 0x01;
    if (mbedtls_ecdsa_read_signature(&ctx, digest, sizeof(digest), sig, slen) == 0 && bench_status == 0)
        bench_status = 0xBAD;

    bench_done = 1;
    while (1) { __asm volatile("wfi"); }
    return 0;
}
