
from dataclasses import dataclass, field
import re
from enum import Enum

whitepace = re.compile(r"\s");
identifier = re.compile("[a-zA-Z_][a-zA-Z0-9_]*")
int_literal = re.compile("[0-9]+")
operator = re.compile("[=!<>]=|[=<>%*/+-]")
punctuation = re.compile("[(){},;]")
comment = re.compile(r"(//|#).*")

invalid_tokens = re.compile("[0-9]+[a-zA-Z_]+") #int_literal and identifier have to be separated with whitespace

class Type(Enum):
    IDENTIFIER = 1
    INT_LITERAL = 2
    OPERATOR = 3
    PUNCTUATION = 4
    END = 5

@dataclass	
class Position:
    line : int
    column : int

@dataclass
class Token:
    type: Type
    content : str
    position : Position = field(default_factory=lambda: Position(0,0))

def tokenize(source_code: str) -> list[Token]:
    #TODO positioning
    tokens = []
    while source_code:
        match = whitepace.match(source_code)
        if (match):
            source_code = source_code[match.end():]
            continue
        match = comment.match(source_code)
        if (match):
            source_code = source_code[match.end():]
            continue
        match = invalid_tokens.match(source_code)
        if (match):
            raise SyntaxError("Wrong syntax")
        match = identifier.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.IDENTIFIER, token))
            source_code = source_code[match.end():]
            continue
        match = int_literal.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.INT_LITERAL, token))
            source_code = source_code[match.end():]
            continue
        match = operator.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.OPERATOR, token))
            source_code = source_code[match.end():]
            continue
        match = punctuation.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.PUNCTUATION, token))
            source_code = source_code[match.end():]
            continue
        raise SyntaxError("Wrong syntax")
    return tokens