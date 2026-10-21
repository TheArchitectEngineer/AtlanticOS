/* SPDX-License-Identifier: MIT - board-selected physical placement. */
ENTRY(_image_start)
SECTIONS {
    . = ATL_LINK_BASE;
    __image_start = .;
    .entry : { KEEP(*(.entry)) }
    .text : ALIGN(16) { *(.text .text.*) }
    .vectors : ALIGN(2048) { KEEP(*(.vectors)) }
    .rodata : ALIGN(16) { *(.rodata .rodata.*) }
    .data : ALIGN(16) { *(.data .data.*) }
    __image_file_end = .;
    .bss (NOLOAD) : ALIGN(16) {
        __bss_start = .;
        *(.bss .bss.* COMMON)
        . = ALIGN(16);
        __bss_end = .;
    }
    .stack (NOLOAD) : ALIGN(16) {
        __stack_bottom = .;
        . += 0x10000;
        __stack_top = .;
    }
    __image_memory_end = .;
    /DISCARD/ : { *(.comment .note* .eh_frame*) }
}
ASSERT((_image_start == ATL_LINK_BASE), "entry must be at image start")
ASSERT((__image_memory_end - __image_start < 0x200000), "preflight exceeds 2 MiB")
