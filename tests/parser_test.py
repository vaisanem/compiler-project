import pytest
import compiler.ast as ast
from compiler.tokenizer import Token, Type, tokenize
from compiler.parser import parse

def test_int_literal_is_parsed() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "0")])
    assert parsed == ast.Literal(0)
    parsed = parse([Token(Type.INT_LITERAL, "1234567890")])
    assert parsed == ast.Literal(1234567890)
    
def test_bool_literal_is_parsed() -> None:
    parsed = parse([Token(Type.BOOL_LITERAL, "true")])
    assert parsed == ast.Literal(True)
    parsed = parse([Token(Type.BOOL_LITERAL, "false")])
    assert parsed == ast.Literal(False)
    
def test_identifier_is_parsed() -> None:
    parsed = parse([Token(Type.IDENTIFIER, "a")])
    assert parsed == ast.Identifier("a")
    parsed = parse([Token(Type.IDENTIFIER, "_666")])
    assert parsed == ast.Identifier("_666")
    
def test_unary_operator_is_parsed() -> None:
    parsed = parse([Token(Type.OPERATOR, "-"), Token(Type.INT_LITERAL, "1")])
    assert parsed == ast.UnaryOp("-", ast.Literal(1))
    parsed = parse([Token(Type.OPERATOR, "not"), Token(Type.BOOL_LITERAL, "true")])
    assert parsed == ast.UnaryOp("not", ast.Literal(True))
    parsed = parse([Token(Type.OPERATOR, "not"), Token(Type.OPERATOR, "not"), Token(Type.IDENTIFIER, "a")])
    assert parsed == ast.UnaryOp("not", ast.UnaryOp("not", ast.Identifier("a")))
    parsed = parse([Token(Type.OPERATOR, "-"), Token(Type.OPERATOR, "-"), Token(Type.BOOL_LITERAL, "true")])
    assert parsed == ast.UnaryOp("-", ast.UnaryOp("-", ast.Literal(True)))
    parsed = parse([Token(Type.OPERATOR, "-"), Token(Type.OPERATOR, "not"), Token(Type.OPERATOR, "-"), Token(Type.OPERATOR, "not"), Token(Type.INT_LITERAL, "2")])
    assert parsed == ast.UnaryOp("-", ast.UnaryOp("not", ast.UnaryOp("-", ast.UnaryOp("not", ast.Literal(2)))))
    
def test_addition_is_parsed() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "-"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "3")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "-", ast.Identifier("TRUE")), "+", ast.Literal(3))
    parsed = parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "-"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "-"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(True), "-", ast.Literal(2)), "-", ast.Literal(False))
    
def test_multiplication_is_parsed() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "2")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "*", ast.Literal(2))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "/"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "/", ast.Identifier("TRUE")), "*", ast.Literal(3))
    parsed = parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "/"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(True), "/", ast.Literal(2)), "/", ast.Literal(False))
    
def test_assignment_is_parsed() -> None:
    parsed = parse([Token(Type.IDENTIFIER, "a"), Token(Type.OPERATOR, "="), Token(Type.INT_LITERAL, "1")])
    assert parsed == ast.BinaryOp(ast.Identifier("a"), "=", ast.Literal(1))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "="), Token(Type.IDENTIFIER, "b"), Token(Type.OPERATOR, "="), Token(Type.IDENTIFIER, "c")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "=", ast.BinaryOp(ast.Identifier("b"), "=", ast.Identifier("c")))
    parsed = parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "="), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "/"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "="), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == ast.BinaryOp(ast.Literal(True), "=", ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "/", ast.Literal(2)), "=", ast.Literal(False)))
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.KEYWORD, "then"), Token(Type.IDENTIFIER, "b"), Token(Type.KEYWORD, "else"), Token(Type.IDENTIFIER, "c"), Token(Type.OPERATOR, "="), Token(Type.INT_LITERAL, "9"), Token(Type.OPERATOR, "="), Token(Type.INT_LITERAL, "8")])
    assert parsed == ast.If(ast.Identifier("a"), ast.Identifier("b"), ast.BinaryOp(ast.Identifier("c"), "=", ast.BinaryOp(ast.Literal(9), "=", ast.Literal(8))))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.KEYWORD, "then"), Token(Type.IDENTIFIER, "b"), Token(Type.KEYWORD, "else"), Token(Type.IDENTIFIER, "c"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "="), Token(Type.IDENTIFIER, "d")])
    assert parsed == ast.BinaryOp(ast.If(ast.Identifier("a"), ast.Identifier("b"), ast.Identifier("c")), "=", ast.Identifier("d"))
    
def test_parentheses_are_parsed() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "+"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.BinaryOp(ast.Literal(True), "+", ast.BinaryOp(ast.Literal(2), "*", ast.Literal(3)))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "+"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "-"), Token(Type.INT_LITERAL, "4"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "*", ast.Literal(2)), "+", ast.BinaryOp(ast.Literal(3), "-", ast.Literal(4)))

def test_precedence_is_correct() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "3")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "*", ast.Literal(2)), "+", ast.Literal(3))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "-"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.OPERATOR, "/"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "4")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "-", ast.BinaryOp(ast.Identifier("TRUE"), "/", ast.Literal(3))), "+", ast.Literal(4))
    parsed = parse([Token(Type.BOOL_LITERAL, "true"), Token(Type.OPERATOR, "-"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "*"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == ast.BinaryOp(ast.Literal(True), "-", ast.BinaryOp(ast.BinaryOp(ast.Literal(2), "*", ast.Literal(3)), "/", ast.Literal(False)))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "-"), Token(Type.IDENTIFIER, "TRUE"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "/"), Token(Type.INT_LITERAL, "3")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "-", ast.Identifier("TRUE")), "/", ast.Literal(3))

def test_if_expression_is_parsed() -> None:
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "then"), Token(Type.BOOL_LITERAL, "true")])
    assert parsed == ast.If(ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2)), ast.Literal(True), None)
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "4")])
    assert parsed == ast.If(ast.Identifier("a"), ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2)), ast.BinaryOp(ast.Literal(3), "+", ast.Literal(4)))

def test_function_call_is_parsed() -> None:
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2))])
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ","), Token(Type.BOOL_LITERAL, "true"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.BinaryOp(ast.Literal(1), "+", ast.Identifier("a")), ast.Literal(True)])
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [])
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.Identifier("a")])
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("a"), [ast.Identifier("b")])
    parsed = parse([Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "c"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.FunctionCall(ast.Identifier("a"), [ast.Identifier("b")]), [ast.Identifier("c")])
    parsed = parse([Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "c"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("a"), [ast.FunctionCall(ast.Identifier("b"), [ast.Identifier("c")])])
    parsed = parse([Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "c"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ","), Token(Type.IDENTIFIER, "d"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("a"), [ast.FunctionCall(ast.Identifier("b"), [ast.Identifier("c")]), ast.Identifier("d")])
    parsed = parse([Token(Type.IDENTIFIER, "g"), Token(Type.PUNCTUATION, "("), Token(Type.BOOL_LITERAL, "false"), Token(Type.OPERATOR, "or"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ","), Token(Type.INT_LITERAL, "0"), Token(Type.OPERATOR, "<"), Token(Type.INT_LITERAL, "0"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("g"), [ast.BinaryOp(ast.Literal(False), "or", ast.Identifier("a")), ast.BinaryOp(ast.Literal(0), "<", ast.Literal(0))])
    parsed = parse([Token(Type.IDENTIFIER, "g"), Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("g"), [ast.Identifier("a")])
    parsed = parse([Token(Type.IDENTIFIER, "g"), Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("g"), [ast.FunctionCall(ast.Identifier("a"), [ast.Identifier("b")])])
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.Identifier("a")])

def test_if_is_allowed_as_part_of_binary_expression() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "e"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "+", ast.If(ast.Identifier("e"), ast.Literal(2), None))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "e"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "+", ast.If(ast.Identifier("e"), ast.Literal(2), ast.BinaryOp(ast.Literal(3), "/", ast.Literal(False))))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "e"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "/"), Token(Type.BOOL_LITERAL, "false")])
    assert parsed == ast.BinaryOp(ast.BinaryOp(ast.Literal(1), "+", ast.If(ast.Identifier("e"), ast.Literal(2), ast.Literal(3))), "/", ast.Literal(False))
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "4")])
    assert parsed == ast.BinaryOp(ast.If(ast.Identifier("a"), ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2)), ast.Literal(3)), "+", ast.Literal(4))

def test_if_is_allowed_as_part_of_if_expression() -> None:
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "false"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2")])
    assert parsed == ast.If(ast.Literal(True), ast.If(ast.Literal(False), ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2)), None), None)
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "false"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "3"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2")])
    assert parsed == ast.If(ast.If(ast.Literal(False), ast.Literal(1), ast.Literal(3)), ast.Literal(2), None)
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "else"), Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "3"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "2")])
    assert parsed == ast.If(ast.Identifier("a"), ast.Literal(1), ast.If(ast.Literal(3), ast.Literal(2), None))
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.OPERATOR, "and"), Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "7"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "6")])
    assert parsed == ast.If(ast.BinaryOp(ast.Identifier("a"), "and", ast.If(ast.Identifier("a"), ast.Literal(7), None)), ast.Literal(6), None)

def test_function_call_is_allowed_as_part_of_binary_expressions() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "+", ast.FunctionCall(ast.Identifier("f"), [ast.Literal(2)]))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "*"), Token(Type.IDENTIFIER, "a")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "+", ast.BinaryOp(ast.FunctionCall(ast.Identifier("f"), [ast.Literal(2)]), "*", ast.Identifier("a")))
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "*"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.BinaryOp(ast.Literal(1), "+", ast.BinaryOp(ast.FunctionCall(ast.Identifier("f"), [ast.Literal(2)]), "*", ast.FunctionCall(ast.Identifier("a"), [ast.Literal(3)])))
    parsed = parse([Token(Type.IDENTIFIER, "g"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "=="), Token(Type.IDENTIFIER, "g"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.BinaryOp(ast.FunctionCall(ast.Identifier("g"), [ast.Literal(1)]), "==", ast.FunctionCall(ast.Identifier("g"), [ast.Literal(2)]))

def test_function_call_is_allowed_as_part_of_if_expression() -> None:
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.If(ast.Literal(True), ast.FunctionCall(ast.Identifier("f"), [ast.Literal(1)]), None)
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ")"), Token(Type.KEYWORD, "then"), Token(Type.BOOL_LITERAL, "true")])
    assert parsed == ast.If(ast.FunctionCall(ast.Identifier("f"), [ast.Literal(1)]), ast.Literal(True), None)
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "i"), Token(Type.PUNCTUATION, ")"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.KEYWORD, "else"), Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.If(ast.Literal(True), ast.BinaryOp(ast.FunctionCall(ast.Identifier("f"), [ast.Identifier("i")]), "+", ast.Literal(2)), ast.FunctionCall(ast.Identifier("f"), [ast.Literal(3)]))
    
def test_if_expression_is_allowed_as_part_of_function_call() -> None:
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.If(ast.Literal(True), ast.Literal(1), ast.Literal(2))])
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ","), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "3"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "4"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2)), ast.If(ast.Literal(True), ast.Literal(3), ast.Literal(4))])
    parsed = parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ","), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "false"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ")")])
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.If(ast.Literal(True), ast.Literal(1), None), ast.If(ast.Literal(False), ast.Literal(1), ast.Literal(1))])

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
        parse([Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, ")")])
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
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.INT_LITERAL, "3")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.OPERATOR, "+")])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.OPERATOR, "+"), Token(Type.INT_LITERAL, "2"), Token(Type.BOOL_LITERAL, "true")])
    with pytest.raises(Exception):
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
    with pytest.raises(Exception):
        parse([Token(Type.IDENTIFIER, "f"), Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, "("), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ","), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ","), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ")")])

def test_parse_accepts_empty_token_list() -> None:
    parse([])