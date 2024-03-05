
from dataclasses import dataclass, field
import re
from enum import Enum

whitepace = re.compile(r'\s');
punctuation = re.compile("[(){},;]")
operator = re.compile("[=!<>]=|[=<>%*/+-]|not|and|or")
int_literal = re.compile("[0-9]+")
bool_literal = re.compile("true|false")
keyword = re.compile("if|then|else|while|do|var") #unit, reserved identifiers?
identifier = re.compile("[a-zA-Z_][a-zA-Z0-9_]*")
comment = re.compile(r'(//|#).*')

invalid_tokens = re.compile("[0-9]+[a-zA-Z_]+") #REMOVE? Integer literal and boolean literal/identifier/keyword have to be separated with whitespace

class Type(Enum):
    PUNCTUATION = 1
    OPERATOR = 2
    INT_LITERAL = 3
    BOOL_LITERAL = 4
    KEYWORD = 5
    IDENTIFIER = 6
    END = 7

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
    #TODO: positioning
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
        match = punctuation.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.PUNCTUATION, token))
            source_code = source_code[match.end():]
            continue
        match = operator.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.OPERATOR, token))
            source_code = source_code[match.end():]
            continue
        match = int_literal.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.INT_LITERAL, token))
            source_code = source_code[match.end():]
            continue
        match = bool_literal.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.BOOL_LITERAL, token))
            source_code = source_code[match.end():]
            continue
        match = keyword.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.KEYWORD, token))
            source_code = source_code[match.end():]
            continue
        match = identifier.match(source_code)
        if (match):
            token = match.group();
            tokens.append(Token(Type.IDENTIFIER, token))
            source_code = source_code[match.end():]
            continue
        raise SyntaxError("Wrong syntax")
    return tokens