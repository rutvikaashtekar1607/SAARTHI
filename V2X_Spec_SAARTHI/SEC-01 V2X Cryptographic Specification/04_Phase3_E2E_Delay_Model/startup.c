#include <stdint.h>
extern uint32_t _estack, _sidata, _sdata, _edata, _sbss, _ebss;
int main(void);
void Reset_Handler(void);
void Default_Handler(void) { while (1) { } }

__attribute__((section(".isr_vector"), used))
const void *const vector_table[16] = {
    &_estack, Reset_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, 0,
    0, 0, 0, Default_Handler, Default_Handler, 0, Default_Handler, Default_Handler};

void Reset_Handler(void)
{
    uint32_t *src = &_sidata, *dst = &_sdata;
    while (dst < &_edata) *dst++ = *src++;
    for (dst = &_sbss; dst < &_ebss; dst++) *dst = 0;
    main();
    while (1) { }
}
