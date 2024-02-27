import pytest
import compiler.ast
from compiler.tokenizer import Token, Type
from compiler.parser import parse

def test_int_literal_is_parsed() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "0")])
    assert parsed == compiler.ast.Literal(0)
    parsed = parse([Token(Type.INT_LITERAL, "1234567890")])
    assert parsed == compiler.ast.Literal(1234567890)
    
def test_bool_literal_is_parsed() -> None:
    parsed = parse([Token(Type.BOOL_LITERAL, "true")])
    assert parsed == compiler.ast.Literal(True)
    parsed = parse([Token(Type.BOOL_LITERAL, "false")])
    assert parsed == compiler.ast.Literal(False)
    
def test_identifier_is_parsed() -> None:
    parsed = parse([Token(Type.IDENTIFIER, "a")])
    assert parsed == compiler.ast.Identifier("a")
    parsed = parse([Token(Type.IDENTIFIER, "_666")])
    assert parsed == compiler.ast.Identifier("_666")

def test_addition_is_parsed() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.Literal(2))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "-"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "3")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(1), "-", compiler.ast.Identifier("TRUE")), "+", compiler.ast.Literal(3))
    parsed = parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "-"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "-"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(True), "-", compiler.ast.Literal(2)), "-", compiler.ast.Literal(False))
    
def test_multiplication_is_parsed() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(1), "*", compiler.ast.Literal(2))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "/"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(1), "/", compiler.ast.Identifier("TRUE")), "*", compiler.ast.Literal(3))
    parsed = parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "/"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(True), "/", compiler.ast.Literal(2)), "/", compiler.ast.Literal(False))

def test_parentheses_are_parsed() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.Literal(2))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "+"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(True), "+", compiler.ast.BinaryOp(compiler.ast.Literal(2), "*", compiler.ast.Literal(3)))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "+"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "-"), Token(Type.INT_LITERAL, "4"), Token(Type.PUNCTUATION, ")")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(1), "*", compiler.ast.Literal(2)), "+", compiler.ast.BinaryOp(compiler.ast.Literal(3), "-", compiler.ast.Literal(4)))

def test_precedence_is_correct() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.BinaryOp(compiler.ast.Literal(2), "*", compiler.ast.Literal(3)))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "-"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.OPERATOR, "/"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "4")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(1), "-", compiler.ast.BinaryOp(compiler.ast.Identifier("TRUE"), "/", compiler.ast.Literal(3))), "+", compiler.ast.Literal(4))
    parsed = parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "-"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(True), "-", compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(2), "*", compiler.ast.Literal(3)), "/", compiler.ast.Literal(False)))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "-"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "/"), Token(Type.INT_LITERAL, "3")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(1), "-", compiler.ast.Identifier("TRUE")), "/", compiler.ast.Literal(3))

def test_if_expression_is_parsed() -> None:
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.If(compiler.ast.Literal(True), compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.Literal(2)))
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "false"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "4")])
    assert parsed == compiler.ast.If(compiler.ast.Literal(False), compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.Literal(2)), compiler.ast.BinaryOp(compiler.ast.Literal(3), "+", compiler.ast.Literal(4)))

def test_if_is_allowed_as_part_of_binary_expression() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "e"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.If(compiler.ast.Identifier("e"), compiler.ast.Literal(2)))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "e"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.If(compiler.ast.Identifier("e"), compiler.ast.Literal(2), compiler.ast.BinaryOp(compiler.ast.Literal(3), "/", compiler.ast.Literal(False))))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "e"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == compiler.ast.BinaryOp(compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.If(compiler.ast.Identifier("e"), compiler.ast.Literal(2), compiler.ast.Literal(3))), "/", compiler.ast.Literal(False))

def test_if_is_allowed_as_part_of_if_expression() -> None:
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "false"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.If(compiler.ast.Literal(True), compiler.ast.If(compiler.ast.Literal(False), compiler.ast.BinaryOp(compiler.ast.Literal(1), "+", compiler.ast.Literal(2))))
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "false"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.If(compiler.ast.If(compiler.ast.Literal(False), compiler.ast.Literal(1)), compiler.ast.Literal(2))
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "false"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.If(compiler.ast.If(compiler.ast.Literal(False), compiler.ast.Literal(1), compiler.ast.Literal(3)), compiler.ast.Literal(2))
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "else"), Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "3"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2")])
    assert parsed == compiler.ast.If(compiler.ast.Identifier("a"), compiler.ast.Literal(1), compiler.ast.If(compiler.ast.Literal(3), compiler.ast.Literal(2)))

def test_parse_raises_error_for_missing_token() -> None:
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "(")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+")])
    with pytest.raises(Exception):
        parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "+")])
    with pytest.raises(Exception):
        parse([Token(Type.IDENTIFIER, "a"), Token(Type.OPERATOR, "*")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "*")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")")])
        
def test_parse_raises_error_for_unexpected_token() -> None:
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, ")")])
    with pytest.raises(Exception):
        parse([Token(Type.OPERATOR, "+")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.INT_LITERAL, "1")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.BOOL_LITERAL, "false")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.IDENTIFIER, "a")])
    with pytest.raises(Exception):
        parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.INT_LITERAL, "1")])
    with pytest.raises(Exception):
        parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.BOOL_LITERAL, "false")])
    with pytest.raises(Exception):
        parse([Token(Type.BOOL_LITERAL, "false"), Token(Type.IDENTIFIER, "a")])
    with pytest.raises(Exception):
        parse([Token(Type.IDENTIFIER, "a"), Token(Type.IDENTIFIER, "b")])
    with pytest.raises(Exception):
        parse([Token(Type.IDENTIFIER, "a"), Token(Type.INT_LITERAL, "1")])
    with pytest.raises(Exception):
        parse([Token(Type.IDENTIFIER, "a"), Token(Type.BOOL_LITERAL, "false")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.PUNCTUATION, ")")])
    with pytest.raises(Exception, match="expected end of input"):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.INT_LITERAL, "3")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "+")])
    with pytest.raises(Exception, match="expected end of input"):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.BOOL_LITERAL, "true")])
    with pytest.raises(Exception, match="expected end of input"):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "+"), Token(Type.IDENTIFIER, "True"), Token(Type.IDENTIFIER, "asd")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ")")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.INT_LITERAL, "1")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.BOOL_LITERAL, "true")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.IDENTIFIER, "a")])
    with pytest.raises(Exception):
        parse([Token(Type.OPERATOR, "+"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")")])
    with pytest.raises(Exception):
        parse([Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3")])
        
def test_parse_accepts_empty_token_list() -> None:
    parse([])
        
def test_is_parsed_as_function_call() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, ")")])
    assert 0 == 1