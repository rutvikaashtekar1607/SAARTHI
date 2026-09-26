#include <stdint.h>
#include <stddef.h>

#include "mbedtls/ecdh.h"

volatile uint32_t benchmark_done = 0;
volatile int benchmark_status = 0;
volatile uint32_t ecc_start_marker = 0;
volatile uint32_t ecc_end_marker = 0;

static uint32_t rng_state = 0x13579BDFU;

static int benchmark_rng(void *ctx, unsigned char *output, size_t len)
{
    size_t i;
    (void)ctx;

    for (i = 0; i < len; i++)
    {
        rng_state = rng_state * 1664525U + 1013904223U;
        output[i] = (unsigned char)(rng_state >> 24);
    }

    return 0;
}

static const uint8_t private_a[32] = {
    0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,
    0x09,0x0A,0x0B,0x0C,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,
    0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x1F,0x20
};

static const uint8_t private_b[32] = {
    0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,
    0x29,0x2A,0x2B,0x2C,0x2D,0x2E,0x2F,0x30,
    0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,
    0x39,0x3A,0x3B,0x3C,0x3D,0x3E,0x3F,0x40
};

int main(void)
{
    int ret;

    mbedtls_ecp_group grp_a;
    mbedtls_ecp_group grp_b;
    mbedtls_mpi d_a;
    mbedtls_mpi d_b;
    mbedtls_ecp_point q_a;
    mbedtls_ecp_point q_b;
    mbedtls_mpi z_a;
    mbedtls_mpi z_b;

    mbedtls_ecp_group_init(&grp_a);
    mbedtls_ecp_group_init(&grp_b);
    mbedtls_mpi_init(&d_a);
    mbedtls_mpi_init(&d_b);
    mbedtls_ecp_point_init(&q_a);
    mbedtls_ecp_point_init(&q_b);
    mbedtls_mpi_init(&z_a);
    mbedtls_mpi_init(&z_b);

    ret = mbedtls_ecp_group_load(&grp_a, MBEDTLS_ECP_DP_SECP256R1);
    if (ret != 0)
        goto cleanup;

    ret = mbedtls_ecp_group_load(&grp_b, MBEDTLS_ECP_DP_SECP256R1);
    if (ret != 0)
        goto cleanup;

    ret = mbedtls_mpi_read_binary(&d_a, private_a, sizeof(private_a));
    if (ret != 0)
        goto cleanup;

    ret = mbedtls_mpi_read_binary(&d_b, private_b, sizeof(private_b));
    if (ret != 0)
        goto cleanup;

    ret = mbedtls_ecdh_gen_public(
        &grp_a, &d_a, &q_a, benchmark_rng, NULL
    );
    if (ret != 0)
        goto cleanup;

    ret = mbedtls_ecdh_gen_public(
        &grp_b, &d_b, &q_b, benchmark_rng, NULL
    );
    if (ret != 0)
        goto cleanup;

    ecc_start_marker = 1;

    ret = mbedtls_ecdh_compute_shared(
        &grp_a, &z_a, &q_b, &d_a, benchmark_rng, NULL
    );
    if (ret != 0)
        goto cleanup;

    ret = mbedtls_ecdh_compute_shared(
        &grp_b, &z_b, &q_a, &d_b, benchmark_rng, NULL
    );

    ecc_end_marker = 1;

    if (ret != 0)
        goto cleanup;

    if (mbedtls_mpi_cmp_mpi(&z_a, &z_b) != 0)
    {
        ret = -1;
        goto cleanup;
    }

    benchmark_status = 0;
    benchmark_done = 1;

    goto finish;

cleanup:
    benchmark_status = ret;

finish:
    mbedtls_mpi_free(&z_b);
    mbedtls_mpi_free(&z_a);
    mbedtls_ecp_point_free(&q_b);
    mbedtls_ecp_point_free(&q_a);
    mbedtls_mpi_free(&d_b);
    mbedtls_mpi_free(&d_a);
    mbedtls_ecp_group_free(&grp_b);
    mbedtls_ecp_group_free(&grp_a);

    while (1)
    {
    }

    return 0;
}