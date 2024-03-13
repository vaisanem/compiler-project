import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
import compiler.ast as ast

def test_parse_raises_error_for_bad_input() -> None:
    with pytest.raises(Exception):
        parse(tokenize("if then then then"))
    with pytest.raises(Exception):
        parse(tokenize("not (not not) 1"))
    with pytest.raises(Exception):
        parse(tokenize("var false = 0"))
    with pytest.raises(Exception):
        parse(tokenize("{var true = 0; true = 2}"))
    with pytest.raises(Exception):
        parse(tokenize("or(1+2, 3)"))
    with pytest.raises(Exception):
        parse(tokenize("var if = 2; if+2)"))
        
def test_parse_unary_expression() -> None:
    parsed = parse(tokenize("- 1"))
    assert parsed == ast.UnaryOp("-", ast.Literal(1))
    parsed = parse(tokenize("not not (not 1)"))
    assert parsed == ast.UnaryOp("not", ast.UnaryOp("not", ast.UnaryOp("not", ast.Literal(1))))
    parsed = parse(tokenize("- not - not a"))
    assert parsed == ast.UnaryOp("-", ast.UnaryOp("not", ast.UnaryOp("-", ast.UnaryOp("not", ast.Identifier("a")))))
    parsed = parse(tokenize("(-1) * 2"))
    assert parsed == ast.BinaryOp(ast.UnaryOp("-", ast.Literal(1)), "*", ast.Literal(2))
    parsed = parse(tokenize("- (1 * 2)"))
    assert parsed == ast.UnaryOp("-", ast.BinaryOp(ast.Literal(1), "*", ast.Literal(2)))
    parsed = parse(tokenize("- if not true then false"))
    assert parsed == ast.UnaryOp("-", ast.If(ast.UnaryOp("not", ast.Literal(True)), ast.Literal(False)))
    parsed = parse(tokenize("-f()"))
    assert parsed == ast.UnaryOp("-", ast.FunctionCall(ast.Identifier("f"), []))
    parsed = parse(tokenize("f(-1)"))
    assert parsed == ast.FunctionCall(ast.Identifier("f"), [ast.UnaryOp("-", ast.Literal(1))])
    parsed = parse(tokenize("not(1)"))
    assert parsed == ast.UnaryOp("not", ast.Literal(1))
    
def test_parse_binary_expression() -> None:
    parsed = parse(tokenize("false and(true)"))
    assert parsed == ast.BinaryOp(ast.Literal(False), "and", ast.Literal(True))
    parsed = parse(tokenize("1 or(1+3)"))
    assert parsed == ast.BinaryOp(ast.Literal(1), "or", ast.BinaryOp(ast.Literal(1), "+", ast.Literal(3)))
        
def test_parse_variable_declaration() -> None:
    parsed = parse(tokenize("var a = 1 + 19"))
    assert parsed == ast.VariableDeclaration(ast.Identifier("a"), None, ast.BinaryOp(ast.Literal(1), "+", ast.Literal(19)))
    parsed = parse(tokenize("var print_int = true"))
    assert parsed == ast.VariableDeclaration(ast.Identifier("print_int"), None, ast.Literal(True))
    
def test_block_inside_if_expression() -> None:
    parsed = parse(tokenize("if if a then {a;b} then 3"))
    assert parsed == ast.If(ast.If(ast.Identifier("a"), ast.Block([ast.Identifier("a"), ast.Identifier("b")])), ast.Literal(3))
    parsed = parse(tokenize("if {{}} then 0"))
    assert parsed == ast.If(ast.Block([ast.Block([])]), ast.Literal(0))
    
def test_parse_while_expression() -> None:
    parsed = parse(tokenize("while a do 1"))
    assert parsed == ast.While(ast.Identifier("a"), ast.Literal(1))
    parsed = parse(tokenize("while a < b do {x=9; x+3;}"))
    assert parsed == ast.While(ast.BinaryOp(ast.Identifier("a"), "<", ast.Identifier("b")), ast.Block([ast.BinaryOp(ast.Identifier("x"), "=", ast.Literal(9)), ast.BinaryOp(ast.Identifier("x"), "+", ast.Literal(3)), ast.Literal(None)]))
    parsed = parse(tokenize("while a do while b do 1"))
    assert parsed == ast.While(ast.Identifier("a"), ast.While(ast.Identifier("b"), ast.Literal(1)))
    parsed = parse(tokenize("8 + while c >= d do { c = c - 1 ; 2 } ;"))
    assert parsed == ast.Block([ast.BinaryOp(ast.Literal(8), "+", ast.While(ast.BinaryOp(ast.Identifier("c"), ">=", ast.Identifier("d")), ast.Block([ast.BinaryOp(ast.Identifier("c"), "=", ast.BinaryOp(ast.Identifier("c"), "-", ast.Literal(1))), ast.Literal(2)]))), ast.Literal(None)])
    
def test_parse_untyped_variable_declaration() -> None:
    parsed = parse(tokenize("var a = 1"))
    assert parsed == ast.VariableDeclaration(ast.Identifier("a"), None, ast.Literal(1))
    parsed = parse(tokenize("var a = 1 + 1"))
    assert parsed == ast.VariableDeclaration(ast.Identifier("a"), None, ast.BinaryOp(ast.Literal(1), "+", ast.Literal(1)))
    parsed = parse(tokenize("var a = b = c"))
    assert parsed == ast.VariableDeclaration(ast.Identifier("a"), None, ast.BinaryOp(ast.Identifier("b"), "=", ast.Identifier("c")))
    
def test_variable_declaration_is_allowed_directly_inside_block() -> None:
    parsed = parse(tokenize("{var a = 1}"))
    assert parsed == ast.Block([ast.VariableDeclaration(ast.Identifier("a"), None, ast.Literal(1))])
    parsed = parse(tokenize("{1; var b = -2}"))
    assert parsed == ast.Block([ast.Literal(1), ast.VariableDeclaration(ast.Identifier("b"), None, ast.UnaryOp("-", ast.Literal(2)))])
    parsed = parse(tokenize("{1 + 2;{var c = 3;}}"))
    assert parsed == ast.Block([ast.BinaryOp(ast.Literal(1), "+", ast.Literal(2)), ast.Block([ast.VariableDeclaration(ast.Identifier("c"), None, ast.Literal(3)), ast.Literal(None)])])
    
def test_variable_declaration_is_not_allowed_inside_other_expressions() -> None:
    with pytest.raises(Exception):
        parse(tokenize("1 = var a = 2"))
    with pytest.raises(Exception):
        parse(tokenize("if var a = 1 then 2"))
    with pytest.raises(Exception):
        parse(tokenize("while var a = 1 do 2"))
    with pytest.raises(Exception):
        parse(tokenize("(var a = 1;)"))
    with pytest.raises(Exception):
        parse(tokenize("not var a = 1"))
    with pytest.raises(Exception):
        parse(tokenize("f(1, var a = 1)"))
        
def test_parse_random() -> None:
    parsed = parse(tokenize("x = { { f(a) } { b } }"))
    assert parsed == ast.BinaryOp(ast.Identifier("x"), "=", ast.Block([ast.Block([ast.FunctionCall(ast.Identifier("f"), [ast.Identifier("a")])]), ast.Block([ast.Identifier("b")])]))
    parsed = parse(tokenize("true(1)"))
    assert parsed == ast.FunctionCall(ast.Literal(True), [ast.Literal(1)])
    parsed = parse(tokenize("1()"))
    assert parsed == ast.FunctionCall(ast.Literal(1), [])
    