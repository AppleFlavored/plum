# Plum Specification
**Note:** This is a draft! Everything in this file is subject to change.

Plum is intended to be a simpler alternative to writing x86 assembly.

While Plum is not designed to *replace* assembly, it is designed to allow
users to use high level syntax and concepts whilst maintaining low level
control over the system.

## 1. Basic Concepts

### 1.1 Segments
Segments are a core feature of Plum. Plum allows users to reserve chunks
of memory for intermediate data, data structures, and the code itself.
Plum has two types of segments: dynamic and static.

**Static segments** [TODO]

**Dynamic segments** [TODO]

### 1.2 Types
[TODO]

## 2. Lexical Structure

### 2.1 Whitespace
Whitespace and comments are ignored between tokens.

### 2.2 Identifiers
Identifiers are a sequence of latin letters. Identifiers can also
contain underscores (`_`).

### 2.3 Keywords
Keywords are reserved names that cannot be used as identifiers.
**NOTE:** Keywords are bound to change as the language is developed.

```
const     end          in          let
proc      restrict     segment     struct
```

### 2.4 Comments
