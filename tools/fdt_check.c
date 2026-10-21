/* SPDX-License-Identifier: MIT
 * Host-only file harness for the same original parser used by entry preflight.
 * No device access or MMIO. Compile on POSIX with -D_POSIX_C_SOURCE=200809L.
 */
#include <atlantic/fdt.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    FILE *file = fopen(argv[1], "rb");
    if (!file) return 2;
    struct stat st;
    if (fstat(fileno(file), &st) || !S_ISREG(st.st_mode) || st.st_size < 40 ||
        st.st_size > ATL_FDT_MAX_BYTES) {
        fclose(file);
        return 2;
    }
    size_t bytes = (size_t)st.st_size;
    unsigned char *data = malloc(bytes);
    if (!data) { fclose(file); return 2; }
    size_t read_bytes = fread(data, 1, bytes, file);
    fclose(file);
    if (read_bytes != bytes) { free(data); return 2; }
    struct AtlanticFdtView view;
    int status = atl_fdt_open(data, bytes, &view);
    if (status == ATL_FDT_OK) status = atl_fdt_validate_structure(&view);
    printf("{\"parser_status\":%d,\"input_bytes\":%zu,\"scope\":\"HOST_FILE_ONLY\"}\n",
           status, bytes);
    free(data);
    return status == ATL_FDT_OK ? 0 : 1;
}
