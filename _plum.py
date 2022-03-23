# This file is getting removed soon. See `plum.py` for rewrite.

from dataclasses import dataclass
from enum import Enum, auto
from typing import Generator

import os
import sys

Location = tuple[str, int, int] # [filename, line, col]

class TokenKind(Enum):
    Unknown = auto()
    EOF = auto()

    # Multi-character tokens
    Identifier = auto()
    String = auto()
    Integer = auto()

    # Keywords
    Proc = auto()
    In = auto()
    End = auto()
    Const = auto()

    # Single-character tokens
    Equal = auto()
    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()
    OpenParen = auto()
    CloseParen = auto()
    Semicolon = auto()

@dataclass
class Token:
    kind: TokenKind
    lexeme: str
    loc: Location

keyword_map = {
    "proc": TokenKind.Proc,
    "in": TokenKind.In,
    "end": TokenKind.End,
    "const": TokenKind.Const,
}

class Node:
    pass

class StmtList(Node):
    def __init__(self):
        self.children: list[Node] = []

class Proc(StmtList):
    def __init__(self, name):
        super().__init__()
        self.name = name

def syntax_error(loc: Location, msg: str):
    file, line, col = loc
    print("%s:%d:%d: error: %s" % (file, line, col, msg))

def parse_file(tokens: list[Token]) -> StmtList:
    root = StmtList()

    while len(tokens) > 0:
        tok = tokens.pop(0)

    return root

def char(line: str, index: int) -> str:
    if index >= len(line):
        return '\n'
    return line[index]

def lex_file(path: str) -> Generator[Token, None, None]:
    with open(path, "r", encoding="utf-8") as f:
        contents = f.read()

    lines = contents.splitlines()
    for offs, line in enumerate(lines, 1):
        col = 0
        while col < len(line):
            if char(line, col).isspace():
                col += 1
                continue

            ch = char(line, col)
            loc: Location = [path, offs, col + 1]
        
            if ch.isalpha() or ch == '_':
                start = col
                while char(line, col).isalnum() or char(line, col) == '_':
                    col += 1
                
                lit = line[start:col]
                yield Token(keyword_map.get(lit, TokenKind.Identifier), lit, loc)
            elif ch.isdigit():
                start = col
                while char(line, col).isdigit():
                    col += 1

                yield Token(TokenKind.Integer, line[start:col], loc)
            else:
                col += 1
                if ch == '\"':
                    start = col
                    while char(line, col) != '\"':
                        if char(line, col) == '\\':
                            col += 2
                        else:
                            col += 1
                    
                    yield Token(TokenKind.String, line[start:col], loc)
                    col += 1 # consume quote
                elif ch == '=':
                    yield Token(TokenKind.Equal, ch, loc)
                elif ch == '+':
                    yield Token(TokenKind.Plus, ch, loc)
                elif ch == '-':
                    yield Token(TokenKind.Minus, ch, loc)
                elif ch == '*':
                    yield Token(TokenKind.Star, ch, loc)
                elif ch == '/':
                    if char(line, col) == '/':
                        col = len(line)
                        continue
                    else:
                        yield Token(TokenKind.Slash, ch, loc)
                elif ch == ';':
                    yield Token(TokenKind.Semicolon, ch, loc)
                elif ch == '(':
                    yield Token(TokenKind.OpenParen, ch, loc)
                elif ch == ')':
                    yield Token(TokenKind.CloseParen, ch, loc)
                else:
                    syntax_error(loc, "Illegal character: `%s`" % ch)
                    yield Token(TokenKind.Unknown, ch, loc)
    
def process_file(path: str):
    if not os.path.isfile(path):
        print("error: File does not exist: %s" % path)
        sys.exit(1)

    tokens = [token for token in lex_file(path)]
    ast = parse_file(tokens)

def main():
    argv = sys.argv[1:]

    if len(argv) == 0:
        print("error: No input file given")
        exit(1)

    process_file(argv[0])

if __name__ == "__main__":
    main()