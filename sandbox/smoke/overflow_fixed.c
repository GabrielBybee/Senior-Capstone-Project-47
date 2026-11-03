#include <stdio.h>
#include <string.h>

/* Copies a name into a fixed-size buffer and greets the user. */
static void greet(const char *name)
{
    char buffer[16];
    snprintf(buffer, sizeof buffer, "%s", name); /* FIX: bounded copy */
    printf("Hello, %s!\n", buffer);
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s NAME\n", argv[0]);
        return 2;
    }
    greet(argv[1]);
    return 0;
}
