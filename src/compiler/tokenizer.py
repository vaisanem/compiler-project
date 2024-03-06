
from dataclasses import dataclass, field
import re
from enum import Enum

whitepace = re.compile(r'\s');
punctuation = re.compile("[(){},;]")
operator = re.compile("[=!<>]=|[=<>%*/+-]|not|and|or") #prohibit "====" etc? Reserved all of these as "not" couldnt be used as identifier in sandbox anyway
int_literal = re.compile("[0-9]+")
bool_literal = re.compile("true|false")
keyword = re.compile("if|then|else|while|do|var") #unit, reserved identifiers? Reserved all of these as if, while and var couldnt be used as identfiers in sandbox anyway
identifier = re.compile("[a-zA-Z_][a-zA-Z0-9_]*")
comment = re.compile(r'(//|#).*')

invalid_tokens = re.compile("[0-9]+[a-zA-Z_]+") #Integer literal and boolean literal/identifier/keyword have to be separated with whitespace

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
    #TODO: add location to tokens
    tokens = []
    location = {"line": 1, "column": 1}
    match = None
    
    def handle_match(type: Type) -> None:
        if not match:
            return
        nonlocal source_code
        token = match.group();
        tokens.append(Token(type, token))
        source_code = source_code[match.end():]
        location["column"] += match.end()

    while source_code:
        match = whitepace.match(source_code)
        if match:
            source_code = source_code[match.end():]
            if (match.group() in ["\n", "\r", "\v", "\f"]):
                location["line"] += 1
                location["column"] = 1
            else:
                location["column"] += match.end()
            continue
        match = comment.match(source_code)
        if match:
            source_code = source_code[match.end():]
            location["column"] += match.end()
            continue
        match = invalid_tokens.match(source_code)
        if match:
            raise SyntaxError(f'Invalid identifier "{match.group()}" at: line {location["line"]}, column {location["column"]}')
        match = punctuation.match(source_code)
        if match:
            handle_match(Type.PUNCTUATION)
            continue
        match = int_literal.match(source_code)
        if match:
            handle_match(Type.INT_LITERAL)
            continue
        match = identifier.match(source_code)
        if match:
            alt = operator.fullmatch(match.group())
            if alt:
                match = alt
                handle_match(Type.OPERATOR)
                continue
            alt = bool_literal.fullmatch(match.group())
            if alt:
                match = alt
                handle_match(Type.BOOL_LITERAL)
                continue
            alt = keyword.fullmatch(match.group())
            if alt:
                match = alt
                handle_match(Type.KEYWORD)
                continue
            handle_match(Type.IDENTIFIER)
            continue
        match = operator.match(source_code)
        if match:
            handle_match(Type.OPERATOR)
            continue
        raise SyntaxError(f'Invalid character sequence at: line {location["line"]}, column {location["column"]}')
    return tokens