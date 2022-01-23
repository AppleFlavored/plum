from curses.ascii import isalpha
from dataclasses import dataclass
from email.policy import default
from enum import Enum, auto

import os
import sys

# TODO: We are keeping track of token positions, but we are not doing anything with it.
Location = tuple[str, int, int] # [filename, line, col]

class TokenKind(Enum):
    Unknown = auto()
    EOF = auto()

    # Multi-character tokens
    Identifier = auto()
    String = auto()
    Number = auto()

    # Keywords
    Proc = auto()

    # Single-character tokens
    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()
    OpenParen = auto()
    CloseParen = auto()

@dataclass
class Token:
    kind: TokenKind
    lexeme: str
    loc: Location

keyword_map = {
    "proc": TokenKind.Proc,
}

def expect_token(token: Token, expected: TokenKind) -> bool:
    return token.kind == expected

def syntax_error(token: Token, msg: str):
    (file, line, col) = token.loc
    print("%s:%d:%d: error: %s" % (file, line, col, msg))

def parse_file(tokens: list[Token]):
    while len(tokens) > 0:
        tok = tokens.pop(0)
        match tok.kind:
            case TokenKind.Proc:
                name = tokens.pop(0)
                if not expect_token(name, TokenKind.Identifier):
                    syntax_error(tok, "Expected procedure name but got `%s`" % name.lexeme)
                    continue
            case _:
                syntax_error(tok, "Unexpected top-level token: `%s`" % tok.lexeme)

# Class for iterating through chars within a string.
# Also allows for peeking ahead in the string.
class Chars:
    def __init__(self, string: str):
        self.string = string
        self.ch_offset = 0
        self.position = 0
        self.ch = ' '

        # Keep track of which line/column we are on.
        self.line = 1
        self.col = 0

    def peek(self) -> str:
        if self.position < len(self.string):
            return self.string[self.position]
        return '\0'

    def next(self):
        if self.position >= len(self.string):
            self.position = len(self.string)
            self.ch = '\0'
            return

        self.ch_offset = self.position
        self.ch = self.string[self.ch_offset]
        self.position += 1

        if self.ch == "\n":
            self.line += 1
            self.col = 0
        else:
            self.col += 1

# Returns the next token in a sequence of characters.
def next_token(chars: Chars) -> Token:
    # Skip whitespace
    while chars.ch.isspace():
        chars.next()

    ch = chars.ch
    loc: Location = [chars.file, chars.line, chars.col]

    if ch.isalpha() or ch == '_':
        start = chars.ch_offset
        while chars.ch.isalnum() or chars.ch == '_':
            chars.next()

        lit = chars.string[start:chars.ch_offset]
        return Token(keyword_map.get(lit, TokenKind.Identifier), lit, loc)
    elif ch.isdigit():
        start = chars.ch_offset
        while chars.ch.isdigit():
            chars.next()

        if chars.ch == '.' and chars.peek().isdigit():
            chars.next()

        while chars.ch.isdigit():
            chars.next()
        
        return Token(TokenKind.Number, chars.string[start:chars.ch_offset], loc)
    else:
        chars.next()
        match ch:
            case '\0':
                token_kind = TokenKind.EOF
            case '{':
                token_kind = TokenKind.OpenParen
            case '}':
                token_kind = TokenKind.CloseParen
            case _:
                token_kind = TokenKind.Unknown

        return Token(token_kind, ch, loc)

# lex_file is responsible for scanning the input file
# for tokens. This function does not do error checking.
# Error checking is done when parsing tokens.
def lex_file(file: str, contents: str) -> list[Token]:
    chars = Chars(contents)
    chars.file = file

    tokens: list[Token] = []

    tok = Token(None, None, None)
    while tok.kind != TokenKind.EOF:
        tok = next_token(chars)
        tokens.append(tok)

    return tokens
    
def process_file(path: str):
    if not os.path.isfile(path):
        print("error: file does not exist: %s" % path)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as file:
        contents = file.read()

    tokens = lex_file(path, contents)
    [print(t) for t in tokens]
    parse_file(tokens)

def main():
    argv = sys.argv[1:]

    if len(argv) == 0:
        print("error: no input file given")
        exit(1)

    process_file(argv[0])

if __name__ == "__main__":
    main()