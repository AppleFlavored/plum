from enum import Enum, auto

import os
import sys

class Token(Enum):
    Unknown = auto()

    Ident = auto()
    String = auto()
    Int = auto()

    Proc = auto()
    In = auto()
    Ret = auto()
    Const = auto()

    Equal = auto()
    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()
    OpenParen = auto()
    CloseParen = auto()
    Semicolon = auto()

keyword_map = {
    "proc": Token.Proc,
    "const": Token.Const,
}

def scan_tokens(source: str):
    yield None

def compile(source: str, filename: str = "<unknown>"):
    tokens = [t for t in scan_tokens(source)]

def main():
    argv = sys.argv[1:]

    if len(argv) < 1:
        print("error: No input file given", file=sys.stderr)
        sys.exit(1)

    path, *argv = argv
    if not os.path.isfile(path):
        print("error: File does not exist:", path, file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        compile(f.read(), path)

if __name__ == "__main__":
    main()