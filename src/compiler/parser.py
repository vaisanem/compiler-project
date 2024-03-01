
import compiler.ast as ast
from compiler.tokenizer import Token, Type

def parse(tokens: list[Token]) -> ast.Expression: #rename pos to index etc?

    left_associative_binary_operators = [
        ['*', '/', '%'],
        ['+', '-'],
        ['<', '<=', '>', '>='],
        ['==', '!='],
        ['and'],
        ['or']
    ]
    lowest_precendence = len(left_associative_binary_operators)
    
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
        return ast.Literal(consume(["true", "false"]).content == "true")
    
    def parse_identifier() -> ast.Expression:
        if not peek().type == Type.IDENTIFIER:
            raise Exception(f'{peek().position}: expected identifier')
        return ast.Identifier(consume().content)
    
    def parse_parentheses() -> ast.Expression:
        consume("(")
        exp = parse_expression(True)
        consume(")")
        return exp
    
    def parse_function_call(name: ast.Expression) -> ast.Expression:
        consume("(")
        arguments = []
        if peek().content != ')':
            arguments.append(parse_expression(True))
            while peek().type == Type.PUNCTUATION and peek().content == ',':
                consume(",")
                arguments.append(parse_expression(True))
        consume(")")
        return ast.FunctionCall(name, arguments)
    
    def parse_term() -> ast.Expression:
        exp = None
        if peek().type == Type.PUNCTUATION and peek().content == '(':
            exp = parse_parentheses()
        elif peek().type == Type.INT_LITERAL:
            exp = parse_int_literal()
        elif peek().type == Type.BOOL_LITERAL:
            exp = parse_bool_literal()
        elif peek().type == Type.IDENTIFIER:
            exp = parse_identifier()
        else:
            raise Exception(f'{peek().position}: expected "(", literal or identifier')
        while peek().type == Type.PUNCTUATION and peek().content == '(':
            exp = parse_function_call(exp)
        return exp
    
    def parse_if_expression() -> ast.Expression:
        exp = None
        if peek().type == Type.KEYWORD and peek().content == "if":
            consume("if")
            condition = parse_expression(True)
            consume("then")
            then_branch = parse_expression(True)
            if peek().type == Type.KEYWORD and peek().content == "else":
                consume("else")
                exp = ast.If(condition, then_branch, parse_expression(True))
            else:
                exp = ast.If(condition, then_branch)
        else:
            exp = parse_term()
        return exp
    
    def parse_unary_expression() -> ast.Expression:
        if peek().type == Type.OPERATOR and peek().content in ["-", "not"]:
            op = consume().content
            return ast.UnaryOp(op, parse_unary_expression())
        else:
            return parse_if_expression()
    
    def parse_binary_expression(precedence: int) -> ast.Expression:
        if not precedence:
            return parse_unary_expression()
        exp = parse_binary_expression(precedence - 1)
        while peek().type == Type.OPERATOR and peek().content in left_associative_binary_operators[precedence - 1]:
            op = consume().content
            right = parse_binary_expression(precedence - 1)
            exp = ast.BinaryOp(exp, op, right)
        return exp
    
    def parse_assignment() -> ast.Expression:
        exp = parse_binary_expression(lowest_precendence)
        if peek().type == Type.OPERATOR and peek().content == '=':
            op = consume("=").content
            right = parse_assignment()
            exp = ast.BinaryOp(exp, op, right)
        return exp
    
    def parse_expression(subroutine: bool) -> ast.Expression:
        exp = parse_assignment()
        if not subroutine and peek().type != Type.END:
            raise Exception(f'{peek().position}: expected end of input')
        return exp
    
    return parse_expression(False)