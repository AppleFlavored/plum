from dataclasses import dataclass
from email.policy import default
from enum import Enum, auto

import os
import sys

# TODO: We are keeping track of token positions, but we are not doing anything with it.
Location = tuple[str, int, int] # [filename, line, col]

class TokenKind(Enum):
    Unknown = auto()

    # Multi-character tokens
    Identifier = auto()

    # Keywords
    Proc = auto()

    # Single-character tokens
    OpenParen = auto()
    CloseParen = auto()

@dataclass
class Token:
    kind: TokenKind
    lexeme: str

keyword_map = {
    "proc": TokenKind.Proc,
}

def keyword_lookup(lit: str) -> TokenKind:
    return keyword_map.get(lit, TokenKind.Identifier)

# Class for iterating through chars within a string.
# Also allows for peeking ahead in the string.
class Chars:
    def __init__(self, string: str):
        self.string = string
        self.position = 0
        self.line = 1
        self.col = 0

    def has_next(self) -> bool:
        return self.position < len(self.string)

    def next(self) -> str:
        ch = self.string[self.position]
        self.col += 1

        if ch == '\n':
            self.line += 1
            self.col = 0

        self.position += 1
        return ch

    def peek(self, offset: int = 1) -> str:
        return self.string[self.position + offset]

# lex_file is responsible for scanning the input file
# for tokens. This function does not do error checking.
# Error checking is done when parsing tokens.
def lex_file(filename: str, contents: str) -> list[Token]:
    tokens: list[Token] = []
    chars = Chars(contents)

    while chars.has_next():
        ch = chars.next()

        # Skip whitespace
        while ch.isspace():
            ch = chars.next()

        token = Token(None, None)

        # Scan identifier or a keyword.
        if ch.isalnum():
            start = chars.position - 1
            while ch.isalnum() or ch == '_':
                ch = chars.next()
            
            token.lexeme = contents[start:chars.position - 1]
            token.kind = keyword_lookup(token.lexeme)
        
        # Handle single-character tokens
        else:
            token.lexeme = ch

            if ch == '{':
                token.kind = TokenKind.OpenParen
            elif ch == '}':
                token.kind = TokenKind.CloseParen
            else:
                # If we cannot match a character with a
                # token kind, just store it as an unknown token.
                token.kind = TokenKind.Unknown

        tokens.append(token)

    return tokens

def process_file(path: str):
    with open(path, "r", encoding="utf-8") as file:
        contents = file.read()

    tokens = lex_file(path, contents)
    print(tokens)

def main():
    argv = sys.argv[1:]

    if len(argv) == 0:
        print("error: no input file given")
        exit(1)

    process_file(argv[0])

if __name__ == "__main__":
    main()