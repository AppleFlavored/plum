# Plum Specification

**NOTE:** The design of this language is still in the works.
The specification is likely to change as Plum is developed.

Plum is a language that is designed to be compiled into x86_64 assembly.
Because of this, Plum allows programmers to directly access registers and
perform operations on them.

## Comments
Plum uses C-like comments. Comments are treated like whitespace by the
compiler and ignored.

```
// This is a single line comment

/* This is a multi
line comment */
```

## Procedures
Procedures in Plum work a lot differently from functions in other
language. First, procedures do not have parameters. The programmer is
expected to use a stack or registers to set arguments for procedures.

Also, procedures will not return when the end of the
procedure is reached. Execution will continue to the next
procedure.

```
proc foo in
    /* ... */
end

proc bar in
    /* Execution will continue here since there was no return statement
       in the previous proc */
end
```

Therefore, it is import to include a `ret` (return) statement at 
the end of your procedures (if you want them to return):

```
proc foo in
    ret
    /* Execution will return back to the caller procedure */
end
```

The `in` keyword must follow the procedure name, and the procedure must
end with the `end` keyword.

### Main Procedure
A main procedure is required in Plum. With the exception of `const` statments, you cannot write statements in the global scope.

Since, procedures do not return by default, you must handle returning
from the main procedure manually.

The main procedure must have the name `main`.
```
proc main in
end
```

## Constants / Enums
Plum does not have variables (kind of). Instead, there are `const` 
expressions that are evaluated at compile-time. Just like the name suggests,
constants are immutable.

```
const myString = "Hello, world!"
```

Enums are planned to be included in Plum. Just like `const`, their values
are evaluated at compile-time.

**NOTE**: Their design is still uncertain.

```
const MyEnum in
    APPLES,
    ORANGES,
    PEARS,

    STRAWBERRY = 5,
    BLUEBERRY = 7
end
```

## Strings
By default, strings is plum are not null-terminated. Character escaping
in strings can be done with the backslash.

```
"I'm a string!"
"I have a new line\n"
"Hello, world\0" // null-terminated
```