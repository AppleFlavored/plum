from dataclasses import dataclass
from enum import Enum, auto

import os
import sys

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
    file, line, col = token.loc
    print("%s:%d:%d: error: %s" % (file, line, col, msg))

def parse_file(tokens: list[Token]):
    while len(tokens) > 0:
        tok = tokens.pop(0)
        if tok.kind == TokenKind.Proc:
            name = tokens.pop(0)
            if not expect_token(name, TokenKind.Identifier):
                syntax_error(tok, "Expected procedure name but got `%s`" % name.lexeme)
                continue
        else:
            syntax_error(tok, "Unexpected top-level token: `%s`" % tok.lexeme)

def char(line: str, index: int) -> str:
    if index >= len(line):
        return '\n'
    return line[index]

# lex_file is responsible for scanning the input file
# for tokens. This function does not do error checking.
# Error checking is done when parsing tokens.
def lex_file(path: str) -> list[Token]:
    with open(path, "r", encoding="utf-8") as f:
        contents = f.read()

    tokens: list[Token] = []
    lines = contents.splitlines()
    for offs, line in enumerate(lines, 1):
        col = 0
        while col < len(line):
            while line[col].isspace():
                col += 1

            ch = char(line, col)
            loc: Location = [path, offs, col + 1]
            tok = Token(None, ch, loc)
        
            if ch.isalpha() or ch == '_':
                start = col
                while char(line, col).isalnum() or char(line, col) == '_':
                    col += 1
                
                lit = line[start:col]

                tok.kind = keyword_map.get(lit, TokenKind.Identifier)
                tok.lexeme = lit
            elif ch.isdigit():
                start = col
                while char(line, col).isdigit():
                    col += 1
                
                if char(line, col) == '.' and char(line, col + 1).isdigit():
                    col += 1

                while char(line, col).isdigit():
                    col += 1

                tok.kind = TokenKind.Number
                tok.lexeme = line[start:col]
            else:
                col += 1
                if ch == '/':
                    if char(line, col) == '/':
                        col = len(line)
                        continue
                    else:
                        tok.kind = TokenKind.Slash
                elif ch == '{':
                    tok.kind = TokenKind.OpenParen
                elif ch == '}':
                    tok.kind = TokenKind.CloseParen
                else:
                    tok.kind = TokenKind.Unknown

            tokens.append(tok)
    
    return tokens
    
def process_file(path: str):
    if not os.path.isfile(path):
        print("error: File does not exist: %s" % path)
        sys.exit(1)

    tokens = lex_file(path)
    # debug: [print(t) for t in tokens]
    parse_file(tokens)

def main():
    argv = sys.argv[1:]

    if len(argv) == 0:
        print("error: No input file given")
        exit(1)

    process_file(argv[0])

if __name__ == "__main__":
    main()