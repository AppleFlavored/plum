from dataclasses import dataclass
from enum import Enum, auto

import os
import sys

class TokenKind(Enum):
    EOF = auto()
    Unknown = auto()

    # Multi-character tokens
    Ident = auto()
    Number = auto()

    # Single character tokens
    Semicolon = ";"
    Equal = "="
    Plus = "+"
    Minus = "-"
    OpenParen = "("
    CloseParen = ")"
    OpenBrace = "{"
    CloseBrace = "}"

    # Keywords
    Proc = auto()
    Const = auto()
    Macro = auto()
    Syscall = auto()

    def __str__(self) -> str:
        return self.value

keyword_map = {
    "proc": TokenKind.Proc,
    "const": TokenKind.Const,
    "macro": TokenKind.Macro,
    "syscall": TokenKind.Syscall,
}

@dataclass
class Token:
    # TODO: token position
    kind: TokenKind
    lexeme: str

    def expect(self, expected_token: TokenKind):
        if self.kind != expected_token:
            PlumCompiler.error("expected '%s'" % expected_token)
        return self

class Lexer:
    def __init__(self, source: str):
        self.src = source
        self.ch = ' '
        self.offset = 0
        self.rd_offset = 0

    def next_char(self):
        if self.rd_offset >= len(self.src):
            self.offset = len(self.src)
            self.ch = "\0"
            return

        self.offset =  self.rd_offset
        self.ch = self.src[self.offset]
        self.rd_offset += 1

    def lex_identifier(self) -> str:
        start = self.offset

        while str.isalnum(self.ch) or self.ch == '_':
            self.next_char()
        
        return self.src[start:self.offset]

    # This can only lex integers.
    # TODO: lex decimal numbers...
    def lex_number(self) -> str:
        start = self.offset

        while str.isdigit(self.ch):
            self.next_char()

        return self.src[start:self.offset]

    def next(self) -> Token:
        # Skip whitespace
        while self.ch == ' ' or self.ch == '\n' or self.ch == '\r' or self.ch == '\t':
            self.next_char()

        ch = self.ch
        if str.isalpha(ch) or ch == '_':
            lit = self.lex_identifier()
            return Token(keyword_map.get(lit, TokenKind.Ident), lit)
        elif str.isdigit(ch):
            lit = self.lex_number()
            return Token(TokenKind.Number, lit)
        else:
            self.next_char()

            if ch == '\0':
                return Token(TokenKind.EOF, ch)
            elif ch == '{':
                return Token(TokenKind.OpenBrace, "{")
            elif ch == '}':
                return Token(TokenKind.CloseBrace, "}")
            elif ch == '=':
                return Token(TokenKind.Equal, "=")
            elif ch == ';':
                return Token(TokenKind.Semicolon, ";")

        return Token(TokenKind.Unknown, ch)

class SyntaxNode:
    parent = None
    children = []

class MethodDeclarationNode(SyntaxNode):
    def __init__(self, name: str):
        self.name = name

class Parser:
    def __init__(self, source: str):
        self.lexer = Lexer(source)

    def generate_ast(self) -> SyntaxNode:
        """ Parse tokens and returns the root node of the AST. """
        root = SyntaxNode()

        tok = self.lexer.next()
        while tok.kind != TokenKind.EOF:
            if tok.kind == TokenKind.Proc:
                self.lexer.next() # consume identifier
                self.parse_block()
            else:
                PlumCompiler.error("unexpected token: %s" % tok.lexeme)
                
            tok = self.lexer.next()

        return root

    def parse_block(self):
        self.lexer.next().expect(TokenKind.OpenBrace) # consume '{'
        
        current = self.lexer.next()
        while current.kind != TokenKind.CloseBrace:
            self.parse_statement(current)
            current = self.lexer.next()

    def parse_statement(self, initial: Token):
        if initial.kind == TokenKind.Ident:
            if self.lexer.next().kind == TokenKind.Equal:
                value = self.lexer.next().expect(TokenKind.Number)
                print("mov %s, %s" % (initial.lexeme, value.lexeme))

class PlumCompiler:
    def __init__(self, contents: str):
        self.parser = Parser(contents)

    def compile(self):
        self.parser.generate_ast()

    @staticmethod
    def error(message):
        """ Print an error message to standard error. """
        print("\033[91merror: \033[0m%s" % message, file=sys.stderr)

    @staticmethod
    def fatal(message):
        """
        Print an error message to standand error, then
        exit the program.
        """
        PlumCompiler.error(message)
        sys.exit(1)

def main():
    input_file = "examples/test.plum"

    if not os.path.isfile(input_file):
        PlumCompiler.fatal("no such file: %s" % input_file)

    with open(input_file, 'r') as file:
        contents = file.read()

    compiler = PlumCompiler(contents)
    compiler.compile()

if __name__ == "__main__":
    main()