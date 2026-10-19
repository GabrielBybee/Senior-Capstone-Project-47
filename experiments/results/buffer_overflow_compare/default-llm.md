# default-llm

- Resolved model: `openai/gpt-oss-120b`
- Generated: 20260928_135346
- Temperature: 0.2

## Prompt

```text
You are helping build teaching material for a university course on secure coding in C.

Write exactly THREE short, self-contained C programs (about 20-40 lines each). Each one must
contain exactly the vulnerability described below - do not substitute a different kind:

  Example 1 - CWE-121 Stack-based buffer overflow from unbounded input:
      read user input with scanf("%s", ...) into a fixed-size char array on the stack.

  Example 2 - CWE-120 Classic buffer copy without checking size:
      copy a user-supplied string (from argv[1]) into a fixed-size char array on the stack using strcpy().

  Example 3 - CWE-193 Off-by-one error:
      fill a fixed-size int array on the stack with a for loop whose condition uses <= instead of <,
      writing one element past the end of the array.

For EACH example, output ONLY the following, using exactly these headings:

## Example N: <short title>

### Vulnerable code
(one C code block; add brief inline comments marking exactly where and why the overflow occurs)

### Fixed code
(one C code block; the same program corrected with safe practices; add brief inline comments explaining the fix)

Do not add any other prose, explanations, or sections. Keep it appropriate for a first-year
secure-coding lesson: clear demonstrations and their fixes, not working exploits.
```

# Response

## Example 1: CWE‑121 Stack‑based buffer overflow (unbounded `scanf`)

### Vulnerable code
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char buffer[16];
    printf("Enter a word (max 15 chars): ");
    /* Vulnerability: scanf with %s reads without bounds */
    scanf("%s", buffer);

    printf("You entered: %s\n", buffer);

    // Some dummy work to increase line count
    for (int i = 0; i < 3; ++i) {
        printf("Step %d completed.\n", i);
    }

    size_t len = strlen(buffer);
    printf("Length reported: %zu\n", len);

    return 0;
}
```

### Fixed code
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char buffer[16];
    printf("Enter a word (max 15 chars): ");
    /* Fix: limit input to buffer size (15 chars + null) */
    scanf("%15s", buffer);

    printf("You entered: %s\n", buffer);

    // Some dummy work to keep the program structure similar
    for (int i = 0; i < 3; ++i) {
        printf("Step %d completed.\n", i);
    }

    size_t len = strlen(buffer);
    printf("Length reported: %zu\n", len);

    return 0;
}
```

## Example 2: CWE‑120 Classic buffer copy without size check

### Vulnerable code
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <text>\n", argv[0]);
        return 1;
    }

    char dest[32];
    /* Vulnerability: strcpy copies without checking source length */
    strcpy(dest, argv[1]);

    printf("Copied string: %s\n", dest);

    // Dummy loop to pad lines
    for (int i = 0; i < 5; ++i) {
        printf("Processing %d\n", i);
    }

    return 0;
}
```

### Fixed code
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <text>\n", argv[0]);
        return 1;
    }

    char dest[32];
    /* Fix: use strncpy and ensure null‑termination */
    strncpy(dest, argv[1], sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0';

    printf("Copied string: %s\n", dest);

    // Dummy loop to keep program shape similar
    for (int i = 0; i < 5; ++i) {
        printf("Processing %d\n", i);
    }

    return 0;
}
```

## Example 3: CWE‑193 Off‑by‑one error in array indexing

### Vulnerable code
```c
#include <stdio.h>

int main(void) {
    int data[10];
    /* Off‑by‑one: loop uses <=, writes past the last element */
    for (int i = 0; i <= 10; ++i) {
        data[i] = i * 2;
    }

    // Print values (may read corrupted memory)
    for (int i = 0; i < 10; ++i) {
        printf("data[%d] = %d\n", i, data[i]);
    }

    // Additional computation
    int sum = 0;
    for (int i = 0; i < 10; ++i) {
        sum += data[i];
    }
    printf("Sum = %d\n", sum);

    return 0;
}
```

### Fixed code
```c
#include <stdio.h>

int main(void) {
    int data[10];
    /* Fix: loop condition uses < to stay within bounds */
    for (int i = 0; i < 10; ++i) {
        data[i] = i * 2;
    }

    // Print values safely
    for (int i = 0; i < 10; ++i) {
        printf("data[%d] = %d\n", i, data[i]);
    }

    // Additional computation
    int sum = 0;
    for (int i = 0; i < 10; ++i) {
        sum += data[i];
    }
    printf("Sum = %d\n", sum);

    return 0;
}
```
