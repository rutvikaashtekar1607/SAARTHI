#ifndef MBEDTLS_BENCHMARK_CONFIG_H
#define MBEDTLS_BENCHMARK_CONFIG_H

/* Bare-metal Cortex-M4 */
#define MBEDTLS_NO_PLATFORM_ENTROPY

/* Do not use host timing facilities */
#undef MBEDTLS_TIMING_C
#undef MBEDTLS_HAVE_TIME
#undef MBEDTLS_HAVE_TIME_DATE

/* AES-GCM */
#define MBEDTLS_AES_C
#define MBEDTLS_GCM_C

/* ECC */
#define MBEDTLS_ECP_C
#define MBEDTLS_ECDH_C
#define MBEDTLS_ECDSA_C

/* ECC curve */
#define MBEDTLS_ECP_DP_SECP256R1_ENABLED

/* Required ECC support */
#define MBEDTLS_BIGNUM_C
#define MBEDTLS_ASN1_PARSE_C
#define MBEDTLS_ASN1_WRITE_C

#endif