import pytest
from compiler.tokenizer import tokenize, Token, Type

def test_tokenize_outputs_a_list() -> None:
	assert type(tokenize("")) == list
	
def test_identifiers_are_tokenized() -> None:
	tokens = tokenize("if _666 var  or AND _a6   \nasd then else a_1_B ____")
	assert tokens == [Token(Type.IDENTIFIER, "if"), Token(Type.IDENTIFIER, "_666"), Token(Type.IDENTIFIER, "var"), Token(Type.IDENTIFIER, "or"), 
				   Token(Type.IDENTIFIER, "AND"), Token(Type.IDENTIFIER, "_a6"), Token(Type.IDENTIFIER, "asd"), Token(Type.IDENTIFIER, "then"), 
				   Token(Type.IDENTIFIER, "else"), Token(Type.IDENTIFIER, "a_1_B"), Token(Type.IDENTIFIER, "____")]
	
def test_integer_literals_are_tokenized() -> None:
	tokens = tokenize("666\n00000  1 1234567890")
	assert tokens == [Token(Type.INT_LITERAL, "666"), Token(Type.INT_LITERAL, "00000"), Token(Type.INT_LITERAL, "1"), Token(Type.INT_LITERAL, "1234567890")]
	
def test_identifiers_and_integer_literals_are_tokenized() -> None:
	tokens = tokenize("1 AND _a6   666\nasd a_1_B ____ 00000")
	assert tokens == [Token(Type.INT_LITERAL, "1"), Token(Type.IDENTIFIER, "AND"), Token(Type.IDENTIFIER, "_a6"), Token(Type.INT_LITERAL, "666"), 
				   Token(Type.IDENTIFIER, "asd"), Token(Type.IDENTIFIER, "a_1_B"), Token(Type.IDENTIFIER, "____"), Token(Type.INT_LITERAL, "00000")]
	
def test_tokenize_raises_error_for_unsupported_characters() -> None:
	with pytest.raises(SyntaxError, match="Wrong syntax"):
		tokenize("if p == 0")
	with pytest.raises(SyntaxError, match="Wrong syntax"):
		tokenize("&")
	with pytest.raises(SyntaxError, match="Wrong syntax"):
		tokenize("ä")
		
def test_tokenize_raises_error_for_invalid_token() -> None:
	with pytest.raises(SyntaxError, match="Wrong syntax"):
		tokenize("23 else 6a")
	
def test_tokens_that_are_not_separated_by_whitespace_are_tokenized() -> None:
	#operators or parenthesis etc
	assert 0 == 1