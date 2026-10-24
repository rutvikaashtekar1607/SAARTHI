/* config_m4.h - minimal Mbed TLS config for the SEC-01 Phase 3 Cortex-M4 timing build.
 * Only AES-GCM, ECDH P-256 and ECDSA P-256 (plus SHA-256) are enabled. */
#ifndef CONFIG_M4_H
#define CONFIG_M4_H

#define MBEDTLS_HAVE_ASM
#define MBEDTLS_AES_C
#define MBEDTLS_GCM_C
#define MBEDTLS_CIPHER_C
#define MBEDTLS_BIGNUM_C
#define MBEDTLS_ECP_C
#define MBEDTLS_ECP_DP_SECP256R1_ENABLED
#define MBEDTLS_ECP_NIST_OPTIM
#define MBEDTLS_ECDH_C
#define MBEDTLS_ECDSA_C
#define MBEDTLS_ASN1_PARSE_C
#define MBEDTLS_ASN1_WRITE_C
#define MBEDTLS_SHA256_C

#endif
