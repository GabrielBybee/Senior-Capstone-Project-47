# default-coder

## Prompt

You are helping build teaching material for a university course on secure coding in C/C++.

Write THREE different short, self-contained C programs (about 20-40 lines each), each
containing a different kind of buffer overflow suitable as an introductory teaching example:

  Example 1: stack-based buffer overflow from unbounded input (e.g. gets/scanf("%s")) - CWE-121
  Example 2: overflow from an unsafe string function (e.g. strcpy/strcat/sprintf) - CWE-120
  Example 3: off-by-one or incorrect loop bound writing past an array (or heap buffer) - CWE-193 / CWE-122

For EACH example:
1. Give the vulnerable program with brief inline comments marking exactly where and why the overflow occurs.
2. Explain in 3-5 sentences what makes the code unsafe and what could go wrong.
3. Provide a corrected, safe version of the same program that avoids the overflow.

Keep it appropriate for a first-year secure-coding lesson: clear demonstrations and their
fixes, not working exploits against any real system. Use a heading for each example.

## Response

# Secure Coding in C/C++: Buffer Overflow Examples

## Example 1: Stack-Based Buffer Overflow from Unbounded Input (CWE-121)

### Vulnerable Program

```c
#include <stdio.h>
#include <string.h>

int main() {
    char buffer[16]; // Small buffer on the stack

    printf("Enter a string: ");
    // VULNERABILITY: gets() does not check buffer size.
    // If input exceeds 15 chars + null terminator, it overwrites adjacent stack memory.
    gets(buffer); 

    printf("You entered: %s\n", buffer);
    return 0;
}
```

### Explanation
The function `gets()` reads a line from standard input into a buffer without any limit on the number of characters it will write. If a user inputs more than 15 characters (plus the null terminator), the excess data overflows the `buffer` array and corrupts adjacent stack memory, such as the saved return address. This can lead to program crashes or, in more advanced scenarios, arbitrary code execution. Modern C standards have removed `gets()` entirely due to its inherent unsafety.

### Corrected Version

```c
#include <stdio.h>
#include <string.h>

int main() {
    char buffer[16];

    printf("Enter a string: ");
    // SAFE: fgets() limits input to sizeof(buffer) - 1 characters,
    // ensuring the null terminator fits within the buffer.
    if (fgets(buffer, sizeof(buffer), stdin) != NULL) {
        // Remove trailing newline if present
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len - 1] == '\n') {
            buffer[len - 1] = '\0';
        }
        printf("You entered: %s\n", buffer);
    }
    return 0;
}
```

---

## Example 2: Overflow from Unsafe String Function (CWE-120)

### Vulnerable Program

```c
#include <stdio.h>
#include <string.h>

int main() {
    char dest[10];
    char source[] = "This string is definitely longer than 10 characters";

    printf("Copying string...\n");
    // VULNERABILITY: strcpy() copies source into dest without checking
    // if dest is large enough to hold the entire string + null terminator.
    strcpy(dest, source);

    printf("Result: %s\n", dest);
    return 0;
}
```

### Explanation
The `strcpy()` function blindly copies the source string into the destination buffer, assuming the destination is large enough. In this case, `source` is much longer than the 10-byte `dest` buffer, causing `strcpy` to write past the end of `dest` into adjacent memory. This corrupts the stack or heap, potentially overwriting other variables or control data. Even if the source is trusted, relying on `strcpy` is unsafe because it provides no bounds checking.

### Corrected Version

```c
#include <stdio.h>
#include <string.h>

int main() {
    char dest[10];
    char source[] = "This string is definitely longer than 10 characters";

    printf("Copying string...\n");
    // SAFE: strncpy() limits the number of characters copied to sizeof(dest).
    // Note: strncpy does not guarantee null-termination if source is longer,
    // so we explicitly null-terminate the destination.
    strncpy(dest, source, sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0'; // Ensure null termination

    printf("Result: %s\n", dest);
    return 0;
}
```

---

## Example 3: Off-by-One Error Writing Past Array Bounds (CWE-193 / CWE-122)

### Vulnerable Program

```c
#include <stdio.h>

int main() {
    int arr[5]; // Array of 5 integers, valid indices 0-4

    printf("Filling array...\n");
    // VULNERABILITY: Loop runs from i=0 to i=5 (inclusive), writing to arr[5].
    // arr[5] is out of bounds; valid indices are 0 to 4.
    for (int i = 0; i <= 5; i++) {
        arr[i] = i * 10;
    }

    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }
    return 0;
}
```

### Explanation
The loop condition `i <= 5` causes the loop to execute one extra time, writing to `arr[5]`, which is outside the allocated memory for the array. This is a classic off-by-one error. Writing to `arr[5]` corrupts adjacent memory, which could be another variable, a return address, or other critical data. Even though the program may appear to work, it exhibits undefined behavior and can cause subtle bugs or crashes.

### Corrected Version

```c
#include <stdio.h>

int main() {
    int arr[5]; // Array of 5 integers, valid indices 0-4

    printf("Filling array...\n");
    // SAFE: Loop runs from i=0 to i=4 (inclusive), staying within bounds.
    for (int i = 0; i < 5; i++) {
        arr[i] = i * 10;
    }

    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }
    return 0;
}
```
