from dataclasses import dataclass
from enum import Enum, auto

import os
import sys

class TokenKind(Enum):
    EOF = auto() # used in parser
    Unknown = auto()

    Ident = auto()
    String = auto()
    Int = auto()

    Equal = auto()
    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()

    Proc = auto()
    In = auto()
    End = auto()
    Segment = auto()

keywords = {
    "proc": TokenKind.Proc,
    "in": TokenKind.In,
    "end": TokenKind.End,
    "segment": TokenKind.Segment,
}

Location = tuple[str, int, int]

@dataclass
class Token:
    kind: TokenKind
    lexeme: str
    loc: Location

class Node(object): pass
class Stmt(Node): pass
class Expr(Node): pass

class Proc(Stmt):
    name: str
    body: list[Stmt]

def match()

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = None

    def parse(self):
        while len(self.tokens) > 0:
            self.advance()
            if self.current.kind == TokenKind.Proc:
                self.advance()
                if self.current.kind == TokenKind.Ident:
                    self.advance() # expect `in`
                    while self.current.kind != TokenKind.End:
                        self.advance()
                else:
                    (filename, line, col) = self.current.loc
                    print("%s:%i:%i: Expected procedure name but got `%s`" % (filename, line, col, self.current.lexeme))
            else:
                pass
       
    def advance(self):
        try:
            self.current = self.tokens.pop(0)
        except IndexError:
            self.current = Token(TokenKind.EOF, '')

class Lexer:
    def __init__(self):
        pass

    def init_lexer(self, filename: str, source: str):
        self.source = source
        self.position = 0
        self.char = self.source[self.position]

        self.filename = filename
        self.line = 1
        self.col = 1

    def advance(self):
        try:
            self.position += 1
            self.col += 1
            self.char = self.source[self.position]
            
            if self.char == '\n':
                self.line += 1
        except IndexError:
            self.position = len(self.source)
            self.char = ''

def scan_tokens(lexer: Lexer):

    while len(lexer.source) > lexer.position:
        while lexer.char.isspace():
            lexer.advance()
        
        ch = lexer.char
        loc: Location = (lexer.filename, lexer.line, lexer.col)

        # Identifier
        if ch.isalpha() or ch == '_':
            start = lexer.position
            while lexer.char.isalnum() or lexer.char == '_':
                lexer.advance()

            ident = lexer.source[start:lexer.position]
            yield Token(keywords.get(ident, TokenKind.Ident), ident, loc)

        # Integer
        elif ch.isdigit():
            pass

        else:
            lexer.advance()
            
            if ch == '=':
                yield Token(TokenKind.Equal, ch, loc)
            elif ch == '+':
                yield Token(TokenKind.Plus, ch, loc)
            elif ch == '-':
                yield Token(TokenKind.Minus, ch, loc)
            elif ch == '*':
                yield Token(TokenKind.Star, ch, loc)
            elif ch == '/':
                # TODO: Multi-line comments
                if lexer.char == '/':
                    while lexer.char != '\n':
                        lexer.advance()
                    continue
                else:
                    yield Token(TokenKind.Slash, ch, loc)
            else:
                yield Token(TokenKind.Unknown, ch, loc)

def compile_file(input_file, output):
    if not os.path.isfile(input_file):
        print("Error: Provided file does not exist:", input_file)
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    lexer = Lexer()
    lexer.init_lexer(input_file, content)

    tokens = [t for t in scan_tokens(lexer)]

    parser = Parser(tokens)
    parser.parse()

def usage(name):
    print("Usage: %s [OPTIONS...] input\n" % name)
    print("Options:")
    print("    -o <path>  output file")
    print()

def get_opt(name, args: list[str]) -> str:
    if len(args) == 0:
        usage(name)
        sys.exit(1)
    return args.pop(0)

def main():
    name, *args = sys.argv
    if len(args) < 1:
        usage(name)
        sys.exit(1)

    input_file = None
    output_name = "out.bin"
    
    while len(args) > 0:
        opt = args.pop(0)
        if opt == '-o':
            output_name = get_opt(name, args)
        else:
            # take the first as input; ignore the rest
            if input_file is None:
                input_file = opt

    if input_file == None:
        print("Error: Input file was not provided.")
        usage(name)
        sys.exit(0)
    
    compile_file(input_file, output_name)

if __name__ == "__main__":
    main()