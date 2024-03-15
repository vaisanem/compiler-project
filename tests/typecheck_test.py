import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.symbol_table import SymbolTable

def test_typecheck_raises_error_for_bad_input() -> None:
    with pytest.raises(Exception):
        typecheck(parse(tokenize("{false}()")), SymbolTable())
    with pytest.raises(Exception):
        typecheck(parse(tokenize("(1)(1, 1+3)")), SymbolTable())
    with pytest.raises(Exception):
        typecheck(parse(tokenize("print_int == print_bool")), SymbolTable())
    with pytest.raises(Exception):
        typecheck(parse(tokenize("var x = 1; var y: Bool = x = 2")), SymbolTable())
    with pytest.raises(Exception):
        typecheck(parse(tokenize("{var true = print_int; true(1)}")), SymbolTable())
    with pytest.raises(Exception):
        typecheck(parse(tokenize("{and = 1; and + 2}")), SymbolTable())
        
def test_valid_program_typechecks() -> None:
    typecheck(parse(tokenize("1")), SymbolTable())
    typecheck(parse(tokenize("true")), SymbolTable())
    typecheck(parse(tokenize("{print_int}(1)")), SymbolTable())
    typecheck(parse(tokenize("var x = print_int; x(1)")), SymbolTable())
    typecheck(parse(tokenize("{var print_bool = 1; print_int(1 + print_bool)}")), SymbolTable())
    typecheck(parse(tokenize("var x = 1; x = 2")), SymbolTable())
    typecheck(parse(tokenize("var x: Int = 1; x = 2")), SymbolTable())
    typecheck(parse(tokenize("var x: Bool = true; x = not x")), SymbolTable())
    typecheck(parse(tokenize("var Bool: Bool = true")), SymbolTable())
    typecheck(parse(tokenize("var x = 1; var y = x + 2")), SymbolTable())
    typecheck(parse(tokenize("var x = print_int; x = print_int;")), SymbolTable())