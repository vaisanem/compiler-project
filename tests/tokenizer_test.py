import pytest
from compiler.tokenizer import tokenize, Token, Type

def test_tokenize_outputs_a_list() -> None:
    assert type(tokenize("")) == list
    
def test_tokenize_ignores_comments() -> None:
    tokens = tokenize(" // then \n//\n# else \n #")
    assert tokens == []
    
def test_punctuation_marks_are_tokenized() -> None:
    tokens = tokenize("(;}){ ,")
    assert tokens == [Token(Type.PUNCTUATION, "("), Token(Type.PUNCTUATION, ";"), Token(Type.PUNCTUATION, "}"), Token(Type.PUNCTUATION, ")"),
                      Token(Type.PUNCTUATION, "{"), Token(Type.PUNCTUATION, ",")]
    
def test_operators_are_tokenized() -> None:
    tokens = tokenize("==!= <not +<=> >=/ % *and-or ")
    assert tokens == [Token(Type.OPERATOR, "=="), Token(Type.OPERATOR, "!="), Token(Type.OPERATOR, "<"), Token(Type.OPERATOR, "not"),
                      Token(Type.OPERATOR, "+"), Token(Type.OPERATOR, "<="), Token(Type.OPERATOR, ">"), Token(Type.OPERATOR, ">="), 
                      Token(Type.OPERATOR, "/"), Token(Type.OPERATOR, "%"), Token(Type.OPERATOR, "*"), Token(Type.OPERATOR, "and"), 
                      Token(Type.OPERATOR, "-"), Token(Type.OPERATOR, "or")]
        
def test_integer_literals_are_tokenized() -> None:
    tokens = tokenize("666\n00000  1 1234567890")
    assert tokens == [Token(Type.INT_LITERAL, "666"), Token(Type.INT_LITERAL, "00000"), Token(Type.INT_LITERAL, "1"), Token(Type.INT_LITERAL, "1234567890")]
    
def test_boolean_literals_are_tokenized() -> None:
    tokens = tokenize("true false false true true")
    assert tokens == [Token(Type.BOOL_LITERAL, "true"), Token(Type.BOOL_LITERAL, "false"), Token(Type.BOOL_LITERAL, "false"), Token(Type.BOOL_LITERAL, "true"), 
                      Token(Type.BOOL_LITERAL, "true")]
    
def test_keywords_are_tokenized() -> None:
    tokens = tokenize("if then else while do return var")
    assert tokens == [Token(Type.KEYWORD, "if"), Token(Type.KEYWORD, "then"), Token(Type.KEYWORD, "else"), Token(Type.KEYWORD, "while"), 
                      Token(Type.KEYWORD, "do"), Token(Type.KEYWORD, "return"), Token(Type.KEYWORD, "var")]
    
def test_identifiers_are_tokenized() -> None:
    tokens = tokenize(" _666 AND _a6   \nasd  a_1_B ____")
    assert tokens == [Token(Type.IDENTIFIER, "_666"), Token(Type.IDENTIFIER, "AND"), Token(Type.IDENTIFIER, "_a6"), Token(Type.IDENTIFIER, "asd"), 
                      Token(Type.IDENTIFIER, "a_1_B"), Token(Type.IDENTIFIER, "____")]
    
def test_all_token_types_are_tokenized() -> None:
    tokens = tokenize("//hello world\n 1 false) if AND==666 do{\na_1_B -__ 00 +not true#x= _4")
    assert tokens == [Token(Type.INT_LITERAL, "1"), Token(Type.BOOL_LITERAL, "false"), Token(Type.PUNCTUATION, ")"), Token(Type.KEYWORD, "if"),
                      Token(Type.IDENTIFIER, "AND"), Token(Type.OPERATOR, "=="), Token(Type.INT_LITERAL, "666"), Token(Type.KEYWORD, "do"),
                      Token(Type.PUNCTUATION, "{"), Token(Type.IDENTIFIER, "a_1_B"), Token(Type.OPERATOR, "-"), Token(Type.IDENTIFIER, "__"),
                      Token(Type.INT_LITERAL, "00"), Token(Type.OPERATOR, "+"), Token(Type.OPERATOR, "not"), Token(Type.BOOL_LITERAL, "true")]
                      
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