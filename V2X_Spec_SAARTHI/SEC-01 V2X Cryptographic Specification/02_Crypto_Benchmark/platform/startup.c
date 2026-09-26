#include <stdint.h>
#include <stddef.h>

extern int main(void);

extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

void *memset(void *s, int c, size_t n)
{
    unsigned char *p = (unsigned char *)s;

    while (n--)
    {
        *p++ = (unsigned char)c;
    }

    return s;
}

void *memcpy(void *dest, const void *src, size_t n)
{
    unsigned char *d = (unsigned char *)dest;
    const unsigned char *s = (const unsigned char *)src;

    while (n--)
    {
        *d++ = *s++;
    }

    return dest;
}

void *memmove(void *dest, const void *src, size_t n)
{
    unsigned char *d = (unsigned char *)dest;
    const unsigned char *s = (const unsigned char *)src;

    if (d < s)
    {
        while (n--)
        {
            *d++ = *s++;
        }
    }
    else if (d > s)
    {
        d += n;
        s += n;

        while (n--)
        {
            *--d = *--s;
        }
    }

    return dest;
}

int memcmp(const void *s1, const void *s2, size_t n)
{
    const unsigned char *p1 = (const unsigned char *)s1;
    const unsigned char *p2 = (const unsigned char *)s2;

    while (n--)
    {
        if (*p1 != *p2)
        {
            return (*p1 < *p2) ? -1 : 1;
        }

        p1++;
        p2++;
    }

    return 0;
}

static unsigned char heap_area[16384];
static size_t heap_used = 0;

void *malloc(size_t size)
{
    size_t aligned_size;

    if (size == 0)
    {
        return 0;
    }

    aligned_size = (size + 7U) & ~7U;

    if (heap_used + aligned_size > sizeof(heap_area))
    {
        return 0;
    }

    void *ptr = &heap_area[heap_used];

    heap_used += aligned_size;

    return ptr;
}

void *calloc(size_t nmemb, size_t size)
{
    size_t total = nmemb * size;
    unsigned char *p = (unsigned char *)malloc(total);

    if (p == 0)
    {
        return 0;
    }

    for (size_t i = 0; i < total; i++)
    {
        p[i] = 0;
    }

    return p;
}

void free(void *ptr)
{
    (void)ptr;
}

size_t strlen(const char *s)
{
    size_t n = 0;

    while (s[n] != '\0')
    {
        n++;
    }

    return n;
}

int strcmp(const char *a, const char *b)
{
    while (*a && (*a == *b))
    {
        a++;
        b++;
    }

    return (unsigned char)*a - (unsigned char)*b;
}

void Reset_Handler(void)
{
    uint8_t *src = (uint8_t *)&_sidata;
    uint8_t *dst = (uint8_t *)&_sdata;

    while (dst < (uint8_t *)&_edata)
    {
        *dst++ = *src++;
    }

    dst = (uint8_t *)&_sbss;

    while (dst < (uint8_t *)&_ebss)
    {
        *dst++ = 0;
    }

    main();

    while (1)
    {
    }
}

void Default_Handler(void)
{
    while (1)
    {
    }
}

__attribute__((section(".isr_vector")))
const uintptr_t vector_table[] =
{
    0x20010000,
    (uintptr_t)Reset_Handler
};