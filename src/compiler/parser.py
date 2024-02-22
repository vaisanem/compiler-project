
import compiler.ast as ast
from compiler.tokenizer import Token, Type

def parse(tokens: list[Token]) -> ast.Expression: #rename pos to index etc?
    #TODO: refactor and add tests
    pos = 0
    
    def peek() -> Token:
        if not pos < len(tokens):
            if tokens:
                return Token(Type.END, "", tokens[-1].position)
            else:
                return Token(Type.END, "")
        return tokens[pos]
    
    # 'consume(expected)' returns the token at 'pos'
    # and moves 'pos' forward.
    #
    # If the optional parameter 'expected' is given,
    # it checks that the token being consumed has that text.
    # If 'expected' is a list, then the token must have
    # one of the texts in the list.
    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.content != expected:
            raise Exception(f'{token.position}: expected "{expected}"')
        if isinstance(expected, list) and token.content not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.position}: expected one of: {comma_separated}')
        pos += 1
        return token

    def parse_int_literal() -> ast.Expression:
        if not peek().type == Type.INT_LITERAL:
            raise Exception(f'{peek().position}: expected integer literal')
        return ast.Literal(int(consume().content))
    
    def parse_bool_literal() -> ast.Expression:
        if not peek().type == Type.BOOL_LITERAL:
            raise Exception(f'{peek().position}: expected boolean literal')
        return ast.Literal(consume().content == "true")
    
    def parse_identifier() -> ast.Expression:
        if not peek().type == Type.IDENTIFIER:
            raise Exception(f'{peek().position}: expected identifier')
        return ast.Identifier(consume().content)
    
    def parse_parentheses() -> ast.Expression:
        consume("(")
        exp = parse_expression()
        consume(")")
        return exp
    
    def parse_factor() -> ast.Expression:
        if peek().content == '(':
            return parse_parentheses()
        if peek().type == Type.INT_LITERAL:
            return parse_int_literal()
        if peek().type == Type.IDENTIFIER:
            return parse_identifier()
        raise Exception(f'{peek().position}: expected "(", integer literal or identifier')
    
    def parse_term() -> ast.Expression:
        exp = parse_factor()
        while peek().type == Type.OPERATOR:
            if peek().content in ['*', '/']:
                op = consume().content
                right = parse_factor()
                exp = ast.BinaryOp(exp, op, right)
        return exp
    
    def parse_expression() -> ast.Expression:
        exp = parse_term()
        while peek().type == Type.OPERATOR:
            if peek().content in ['+', '-']:
                op = consume().content
                right = parse_term()
                exp = ast.BinaryOp(exp, op, right)
        if peek().type != Type.END: 
            raise Exception(f'{peek().position}: unexpected token')
        return exp
    
    return parse_expression()