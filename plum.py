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
    Const = auto()
    Segment = auto()

keywords = {
    "const": TokenKind.Const,
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

class Constant(Expr):
    def __init__(self, value: object):
        self.value = value

class Module(Node):
    body: list[Stmt]

    def __init__(self):
        self.body = []

class Proc(Stmt):
    name: str
    body: list[Stmt]

    def __init__(self):
        self.body = []

class ConstAssign(Stmt):
    name: str
    expr: Expr

def dump(node: Node, level: int = 0):
    def _format(indent: int, text: str):
        return '{0}{1}'.format('  ' * indent, text)

    value = "Node"

    if isinstance(node, Module):
        value = "Module"
    elif isinstance(node, Proc):
        value = 'Proc [{0}]'.format(node.name)
    elif isinstance(node, Stmt):
        value = '{0} [{1} = {2}]'.format(node.__class__.__name__, node.name, node.expr.value)

    print(_format(level, value))
    try:
        for c in node.body:
            dump(c, level + 1)
    except AttributeError:
        pass

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = None

    def parse(self, module: Module):
        self.module = module

        while len(self.tokens) > 0:
            self.advance()
            if self.current.kind == TokenKind.Proc:
                self.parse_proc()
            else:
                self.error("Unexpected token: %s" % self.current.lexeme)

    def parse_proc(self):
        self.advance() # Skip 'proc'
        proc = Proc()
        
        if not self.check(TokenKind.Ident):
            self.error("Expected procedure name but got `%s`" % self.current.lexeme)
            return
        
        proc.name = self.current.lexeme
        self.advance() # Skip ident

        if not self.check(TokenKind.In):
            self.error("Expected `in` but got `%s`" % self.current.lexeme)
            return

        self.advance() # Skip 'in'
        while self.current.kind != TokenKind.End:
            self.parse_statement(proc)

        self.module.body.append(proc)

    def parse_statement(self, parent: Proc | Module):
        if self.current.kind == TokenKind.Const:
            self.advance()
            const = ConstAssign()

            if not self.check(TokenKind.Ident):
                self.error("Expected constant name but got `%s`" % self.current.lexeme)
                return
            
            const.name = self.current.lexeme
            self.advance()

            if not self.check(TokenKind.Equal):
                self.error("Expected `=` but got `%s`" % self.current.lexeme)
                return
            self.advance()

            if not self.check(TokenKind.Int):
                self.error("Expected expression but got `%s`" % self.current.lexeme)
                return

            const.expr = Constant(self.current.lexeme)
            parent.body.append(const)

        self.advance()

    def sync(self):
        while (
            self.current.kind != TokenKind.Proc and
            self.current.kind != TokenKind.EOF
        ):
            self.advance()

    def check(self, expected: TokenKind) -> bool:
        return self.current.kind == expected

    def error(self, message: str):
        print("Error: %s:%s:%s:" % self.current.loc, message, file=sys.stderr)
        self.sync()

    def advance(self):
        try:
            self.current = self.tokens.pop(0)
        except IndexError:
            self.current = Token(TokenKind.EOF, '', self.current.loc)

class Lexer:
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
            start = lexer.position
            while lexer.char.isdigit():
                lexer.advance()

            yield Token(TokenKind.Int, lexer.source[start:lexer.position], loc)

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

    # One module per file?
    module = Module()

    parser = Parser(tokens)
    parser.parse(module)

    print()
    dump(module)
    print()

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