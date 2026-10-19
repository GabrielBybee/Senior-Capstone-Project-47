# default-coder

- Resolved model: `qwen/qwen3.8-27b`
- Generated: 20260928_135328
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

## Example 1: Unbounded Input via scanf

### Vulnerable code
```c
#include <stdio.h>

int main() {
    char buffer[16]; // Fixed size buffer on the stack
    printf("Enter a string: ");
    
    // VULNERABILITY: scanf("%s") does not limit the number of characters read.
    // If input exceeds 15 chars, it overflows the 16-byte buffer.
    scanf("%s", buffer); 

    printf("You entered: %s\n", buffer);
    return 0;
}
```

### Fixed code
```c
#include <stdio.h>

int main() {
    char buffer[16]; // Fixed size buffer on the stack
    printf("Enter a string: ");
    
    // FIX: Use width specifier %15s to ensure at most 15 chars are read,
    // leaving room for the null terminator in the 16-byte buffer.
    scanf("%15s", buffer); 

    printf("You entered: %s\n", buffer);
    return 0;
}
```

## Example 2: Unsafe String Copy from argv

### Vulnerable code
```c
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    char dest[32]; // Fixed size destination buffer

    if (argc < 2) {
        printf("Usage: %s <string>\n", argv[0]);
        return 1;
    }

    // VULNERABILITY: strcpy() copies the source string without checking
    // if it fits in the destination. If argv[1] is longer than 31 chars,
    // it overflows the 32-byte buffer.
    strcpy(dest, argv[1]); 

    printf("Copied: %s\n", dest);
    return 0;
}
```

### Fixed code
```c
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    char dest[32]; // Fixed size destination buffer

    if (argc < 2) {
        printf("Usage: %s <string>\n", argv[0]);
        return 1;
    }

    // FIX: Use strncpy() to limit the copy to 31 characters, ensuring
    // the buffer is not exceeded. We manually null-terminate to be safe.
    strncpy(dest, argv[1], sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0'; 

    printf("Copied: %s\n", dest);
    return 0;
}
```

## Example 3: Off-by-One Array Write

### Vulnerable code
```c
#include <stdio.h>

int main() {
    int arr[5]; // Array of 5 integers (indices 0 to 4)
    int i;

    // VULNERABILITY: The loop condition i <= 5 causes the loop to run
    // for i=0,1,2,3,4,5. When i=5, it writes to arr[5], which is one
    // element past the end of the array (out-of-bounds write).
    for (i = 0; i <= 5; i++) {
        arr[i] = i * 10;
    }

    for (i = 0; i < 5; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    return 0;
}
```

### Fixed code
```c
#include <stdio.h>

int main() {
    int arr[5]; // Array of 5 integers (indices 0 to 4)
    int i;

    // FIX: Change condition to i < 5 to ensure we only write to valid
    // indices 0 through 4.
    for (i = 0; i < 5; i++) {
        arr[i] = i * 10;
    }

    for (i = 0; i < 5; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    return 0;
}
```
