import pytest
import compiler.ast
from compiler.tokenizer import Token, Type
from compiler.parser import parse

def test_parse_accepts_empty_input() -> None:
    assert 0==1
    
def test_block_is_allowed_inside_block() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}")]) 
    assert parsed == compiler.ast.Block([compiler.ast.Block([compiler.ast.Identifier("a")])])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, "}")])
    assert parsed == compiler.ast.Block([compiler.ast.Block([compiler.ast.Identifier("a")]), compiler.ast.Block([compiler.ast.Identifier("b")])])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}")])
    assert parsed == compiler.ast.Block([compiler.ast.If(compiler.ast.Literal(True), compiler.ast.Block([compiler.ast.Identifier("a")])), compiler.ast.Identifier("b")])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.KEYWORD, "else"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}"), Token(Type.INT_LITERAL, "3"), Token(Type.PUNCTUATION, "}")])
    assert parsed == compiler.ast.Block([compiler.ast.If(compiler.ast.Literal(True), compiler.ast.Block([compiler.ast.Identifier("a")]), compiler.ast.Block([compiler.ast.Identifier("b")])), compiler.ast.Literal(3)])
    
def test_block_has_correct_return_value() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == compiler.ast.Block([compiler.ast.Block([compiler.ast.Literal(1), compiler.ast.Literal(None)]), compiler.ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ";")])
    assert parsed == compiler.ast.Block([compiler.ast.Block([compiler.ast.Literal(1), compiler.ast.Literal(2)]), compiler.ast.Literal(None)])
    
def test_curly_brackets_can_be_omitted_on_top_level() -> None:
    parsed = parse([Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";")])
    assert parsed == compiler.ast.Block([compiler.ast.Literal(1), compiler.ast.Literal(None)])
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "a")])
    assert parsed == compiler.ast.Block([compiler.ast.Block([compiler.ast.Literal(1)]), compiler.ast.Identifier("a")])
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";")])
    assert parsed == compiler.ast.Block([compiler.ast.If(compiler.ast.Literal(1), compiler.ast.Literal(1)), compiler.ast.Literal(None)])
    parsed = parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "a")])
    assert parsed == compiler.ast.Block([compiler.ast.If(compiler.ast.Literal(1), compiler.ast.Literal(1)), compiler.ast.Identifier("a")])
    parsed = parse([Token(Type.INT_LITERAL, "2"), Token(Type.PUNCTUATION, ";"), Token(Type.IDENTIFIER, "a"), Token(Type.OPERATOR, "=="), Token(Type.INT_LITERAL, "3")])
    assert parsed == compiler.ast.Block([compiler.ast.Literal(2), compiler.ast.BinaryOp(compiler.ast.Identifier("a"), "==", compiler.ast.Literal(3))])
    
def test_curly_brackets_can_be_omitted_only_on_top_level() -> None:
    with pytest.raises(Exception):
        parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1")])
    with pytest.raises(Exception):
        parse([Token(Type.KEYWORD, "if"), Token(Type.INT_LITERAL, "1"), Token(Type.KEYWORD, "then"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ";"), Token(Type.KEYWORD, "else"), Token(Type.INT_LITERAL, "1")])

def test_semicolon_can_be_omitted_after_block() -> None:
    parsed = parse([Token(Type.PUNCTUATION, "{"), Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, "}")])
    assert parsed == compiler.ast.Block([compiler.ast.Literal(1)])
    
def test_parse_raises_error_for_bad_input() -> None:
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, ";")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.IDENTIFIER, "b"), Token(Type.PUNCTUATION, "}")])
    with pytest.raises(Exception):
        parse([Token(Type.PUNCTUATION, "{"), Token(Type.KEYWORD, "if"), Token(Type.BOOL_LITERAL, "true"), Token(Type.KEYWORD, "then"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a"), Token(Type.PUNCTUATION, "}"), Token(Type.IDENTIFIER, "b"), Token(Type.IDENTIFIER, "c"), Token(Type.PUNCTUATION, "}")])
