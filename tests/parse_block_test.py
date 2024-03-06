import pytest
import compiler.ast as ast
from compiler.tokenizer import Token, Type
from compiler.parser import parse

def test_parse_accepts_empty_block() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([])
    
def test_block_is_allowed_inside_block() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}")]) 
    assert parsed == ast.Block([ast.Block([ast.Identifier("a")])])
    
def test_semicolon_is_not_required_for_block_inside_block() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.Block([ast.Identifier("a")]), ast.Block([ast.Identifier("b")])])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.If(ast.Literal(True), ast.Block([ast.Identifier("a")])), ast.Identifier("b")])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.KEYWORD, "else"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.If(ast.Literal(True), ast.Block([ast.Identifier("a")]), ast.Block([ast.Identifier("b")])), ast.Literal(3)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "c"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.If(ast.Literal(True), ast.Block([ast.Identifier("a")])), ast.Identifier("b"), ast.Identifier("c")])

def test_block_has_correct_return_value() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Block([ast.Literal(1), ast.Literal(None)]), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Block([ast.Literal(1), ast.Literal(2)]), ast.Literal(None)])
    
def test_curly_brackets_can_be_omitted_on_top_level() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Literal(1), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "a")])
    assert parsed == ast.Block([ast.Block([ast.Literal(1)]), ast.Identifier("a")])
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.If(ast.Literal(1), ast.Literal(1)), ast.Literal(None)])
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "a")])
    assert parsed == ast.Block([ast.If(ast.Literal(1), ast.Literal(1)), ast.Identifier("a")])
    parsed = parse([Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "a"), Token(Type.OPERATOR, "=="), Token(Type.INT_LITERAL, "3")])
    assert parsed == ast.Block([ast.Literal(2), ast.BinaryOp(ast.Identifier("a"), "==", ast.Literal(3))])
    
def test_curly_brackets_can_be_omitted_only_on_top_level() -> None:
    with pytest.raises(Exception):
        parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1")])
    with pytest.raises(Exception):
        parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "1")])

def test_semicolon_can_be_omitted_after_block() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.Literal(1)])
    
def test_random() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.If(ast.Literal(True), ast.Block([ast.Identifier("a")])), ast.Identifier("b")])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Block([ast.Block([ast.Block([])])]), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.KEYWORD, "if"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "0"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Block([ast.If(ast.If(ast.Block([ast.Identifier("a"), ast.Identifier("b")]), ast.Block([ast.Block([])])), ast.Literal(0))]), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.OPERATOR, "=="), Token(Type.INT_LITERAL, "9")])
    assert parsed == ast.BinaryOp(ast.Block([ast.Identifier("a"), ast.Identifier("b")]), "==", ast.Literal(9))
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.OPERATOR, "=="), Token(Type.INT_LITERAL, "9"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.BinaryOp(ast.Block([ast.Identifier("a"), ast.Identifier("b")]), "==", ast.Literal(9)), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "x"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "y"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.Block([ast.Identifier("x")]), ast.Block([ast.Identifier("y")]), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "x"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "y"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.Block([ast.Identifier("x"), ast.Literal(None)]), ast.Block([ast.Identifier("y")])])

def test_top_level_works_fine() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ";"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Literal(1), ast.Literal(2), ast.Literal(3), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Block([]), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.Block([ast.Literal(1)]), ast.Block([ast.Literal(1)])])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.Block([ast.Literal(1)]), ast.Block([ast.Literal(1)])])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.Block([ast.Literal(1)]), ast.Block([ast.Literal(1)]), ast.Literal(None)])
    with pytest.raises(Exception):
        parse([Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.INT_LITERAL, "2"), Token(Type.INT_LITERAL, "3")])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}")])
    assert parsed == ast.Block([ast.Block([ast.Literal(1)]), ast.Block([ast.Literal(1)]), ast.Block([ast.Literal(1)])])
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "b")])
    assert parsed == ast.Block([ast.If(ast.Literal(True), ast.Block([ast.Identifier("a")])), ast.Identifier("b")])

def test_this_should_be_a_function_call_by_recursive_definition() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "a"), Token(Type.OPERATOR, "+"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "c"), Token(Type.OPERATOR, "+"), Token(Type.IDENTIFIER, "d"), Token(Type.PUNCTUATION, ")"), Token(Type.PUNCTUATION, ";")])
    assert parsed == ast.Block([ast.FunctionCall(ast.BinaryOp(ast.Identifier("a"), "+", ast.Identifier("b")), [ast.BinaryOp(ast.Identifier("c"), "+", ast.Identifier("d"))]), ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "("), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, ")")])
    assert parsed != ast.Block([ast.Block([ast.Identifier("a")]), ast.Identifier("b")])
    assert parsed == ast.FunctionCall(ast.Block([ast.Identifier("a")]), [ast.Identifier("b")])

def test_parse_raises_error_for_bad_input() -> None:
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, ";")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "c"), Token(Type.PUNCTUATION, "}")])
    with pytest.raises(Exception):
        parse([Token(Type.KEYWORD, "if"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, ";"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "5")])    
    with pytest.raises(Exception):
        parse([Token(Type.KEYWORD, "if"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "5")])