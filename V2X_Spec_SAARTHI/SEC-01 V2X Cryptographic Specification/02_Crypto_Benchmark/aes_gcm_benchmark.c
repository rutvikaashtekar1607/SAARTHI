#include <stdint.h>
#include <string.h>

#include "mbedtls/gcm.h"

#define TEST_SIZE 1024

volatile uint32_t benchmark_done = 0;
volatile int benchmark_status = 0;

volatile uint32_t aes_gcm_start_marker = 0;
volatile uint32_t aes_gcm_end_marker = 0;

static uint8_t plaintext[TEST_SIZE];
static uint8_t ciphertext[TEST_SIZE];
static uint8_t key[16];
static uint8_t nonce[12];
static uint8_t tag[16];

int main(void)
{
    int ret;
    mbedtls_gcm_context gcm;

    memset(plaintext, 0x41, sizeof(plaintext));
    memset(ciphertext, 0x00, sizeof(ciphertext));
    memset(key, 0x00, sizeof(key));
    memset(nonce, 0x00, sizeof(nonce));
    memset(tag, 0x00, sizeof(tag));

    mbedtls_gcm_init(&gcm);

    ret = mbedtls_gcm_setkey(
        &gcm,
        MBEDTLS_CIPHER_ID_AES,
        key,
        128
    );

    if (ret != 0)
    {
        benchmark_status = ret;
        mbedtls_gcm_free(&gcm);
        return 1;
    }

    aes_gcm_start_marker = 1;

    ret = mbedtls_gcm_crypt_and_tag(
        &gcm,
        MBEDTLS_GCM_ENCRYPT,
        TEST_SIZE,
        nonce,
        sizeof(nonce),
        NULL,
        0,
        plaintext,
        ciphertext,
        sizeof(tag),
        tag
    );

    aes_gcm_end_marker = 1;

    benchmark_status = ret;

    mbedtls_gcm_free(&gcm);

    if (ret == 0)
    {
        benchmark_done = 1;
    }

    while (1)
    {
    }

    return 0;
}