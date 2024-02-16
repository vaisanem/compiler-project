import pytest
from compiler.tokenizer import tokenize, Token, Type

def test_tokenize_outputs_a_list() -> None:
    assert type(tokenize("")) == list
    
def test_tokenize_ignores_comments() -> None:
    tokens = tokenize(" // then \n//\n# else \n #")
    assert tokens == []
    
def test_identifiers_are_tokenized() -> None:
    tokens = tokenize("if _666 var  or AND _a6   \nasd then else a_1_B not ____")
    assert tokens == [Token(Type.IDENTIFIER, "if"), Token(Type.IDENTIFIER, "_666"), Token(Type.IDENTIFIER, "var"), Token(Type.IDENTIFIER, "or"), 
                   Token(Type.IDENTIFIER, "AND"), Token(Type.IDENTIFIER, "_a6"), Token(Type.IDENTIFIER, "asd"), Token(Type.IDENTIFIER, "then"), 
                   Token(Type.IDENTIFIER, "else"), Token(Type.IDENTIFIER, "a_1_B"), Token(Type.IDENTIFIER, "not"), Token(Type.IDENTIFIER, "____")]
    
def test_integer_literals_are_tokenized() -> None:
    tokens = tokenize("666\n00000  1 1234567890")
    assert tokens == [Token(Type.INT_LITERAL, "666"), Token(Type.INT_LITERAL, "00000"), Token(Type.INT_LITERAL, "1"), Token(Type.INT_LITERAL, "1234567890")]
    
def test_operators_are_tokenized() -> None:
    tokens = tokenize("==!= < +<=> >=/ % *- ")
    assert tokens == [Token(Type.OPERATOR, "=="), Token(Type.OPERATOR, "!="), Token(Type.OPERATOR, "<"), Token(Type.OPERATOR, "+"), 
                      Token(Type.OPERATOR, "<="), Token(Type.OPERATOR, ">"), Token(Type.OPERATOR, ">="), Token(Type.OPERATOR, "/"),
                      Token(Type.OPERATOR, "%"), Token(Type.OPERATOR, "*"), Token(Type.OPERATOR, "-")]
    
def test_punctuation_marks_are_tokenized() -> None:
    tokens = tokenize("(;}){ ,")
    assert tokens == [Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ")"),
                      Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, ",")]
    
def test_all_token_types_are_tokenized() -> None:
    tokens = tokenize("//hello world\n 1) AND==666 {\na_1_B -__ 00 +#x= _4")
    assert tokens == [Token(Type.INT_LITERAL, "1"), Token(Type.PUNCTUATION, ")"), Token(Type.IDENTIFIER, "AND"), Token(Type.OPERATOR, "=="),
                      Token(Type.INT_LITERAL, "666"), Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a_1_B"), Token(Type.OPERATOR, "-"),
                      Token(Type.IDENTIFIER, "__"), Token(Type.INT_LITERAL, "00"), Token(Type.OPERATOR, "+")]
    
def test_tokenize_raises_error_for_unsupported_characters() -> None:
    with pytest.raises(SyntaxError, match="Wrong syntax"):
        tokenize("var x = (A && b) ? TRUE : FALSE")
    with pytest.raises(SyntaxError, match="Wrong syntax"):
        tokenize("&")
    with pytest.raises(SyntaxError, match="Wrong syntax"):
        tokenize("ä")
        
def test_tokenize_raises_error_for_invalid_tokens() -> None:
    with pytest.raises(SyntaxError, match="Wrong syntax"):
        tokenize("23 else 6a")
    with pytest.raises(SyntaxError, match="Wrong syntax"):
        tokenize("23 else 6A")
    with pytest.raises(SyntaxError, match="Wrong syntax"):
        tokenize("23 else 6_")