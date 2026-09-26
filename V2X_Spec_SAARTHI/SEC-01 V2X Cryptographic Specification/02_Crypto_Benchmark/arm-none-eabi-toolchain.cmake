set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR cortex-m4)

set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
set(CMAKE_AR arm-none-eabi-ar)
set(CMAKE_RANLIB arm-none-eabi-ranlib)

set(CMAKE_C_FLAGS_INIT "-mcpu=cortex-m4 -mthumb -mfloat-abi=soft")
set(CMAKE_ASM_FLAGS_INIT "-mcpu=cortex-m4 -mthumb -mfloat-abi=soft")

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)