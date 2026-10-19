# default-llm-large

- Resolved model: `qwen/qwen3.5-122b`
- Generated: 20260928_135318
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

## Example 1: Unbounded Input with scanf

### Vulnerable code
```c
#include <stdio.h>

int main() {
    char buffer[16]; // Fixed size stack buffer
    printf("Enter a name: ");
    // VULNERABILITY: %s reads until whitespace without checking buffer size
    // If input > 15 chars, it overwrites stack memory (CWE-121)
    scanf("%s", buffer); 
    printf("Hello, %s!\n", buffer);
    return 0;
}
```

### Fixed code
```c
#include <stdio.h>

int main() {
    char buffer[16]; // Fixed size stack buffer
    printf("Enter a name: ");
    // FIX: Use width specifier %15s to limit input to buffer size - 1
    // This ensures space for the null terminator and prevents overflow
    if (scanf("%15s", buffer) == 1) {
        printf("Hello, %s!\n", buffer);
    }
    return 0;
}
```

## Example 2: Classic Buffer Copy with strcpy

### Vulnerable code
```c
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc < 2) return 1;
    char dest[10]; // Fixed size stack buffer
    // VULNERABILITY: strcpy copies until null byte, ignoring dest size
    // If argv[1] is longer than 9 chars, it overwrites stack (CWE-120)
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
    if (argc < 2) return 1;
    char dest[10]; // Fixed size stack buffer
    // FIX: Use strncpy with explicit size limit (sizeof(dest) - 1)
    // Ensure null termination manually to prevent truncation issues
    strncpy(dest, argv[1], sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0'; 
    printf("Copied: %s\n", dest);
    return 0;
}
```

## Example 3: Off-by-one Error in Loop

### Vulnerable code
```c
#include <stdio.h>

int main() {
    int arr[5]; // Fixed size array on stack
    int i;
    // VULNERABILITY: Loop condition uses <= instead of <
    // When i is 5, it writes to arr[5], which is out of bounds (CWE-193)
    for (i = 0; i <= 5; i++) { 
        arr[i] = i * 10;
    }
    printf("Array filled.\n");
    return 0;
}
```

### Fixed code
```c
#include <stdio.h>

int main() {
    int arr[5]; // Fixed size array on stack
    int i;
    // FIX: Change loop condition to < to stop at index 4
    // This ensures we only access valid indices 0 through 4
    for (i = 0; i < 5; i++) { 
        arr[i] = i * 10;
    }
    printf("Array filled.\n");
    return 0;
}
```
