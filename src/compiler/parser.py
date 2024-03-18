
import compiler.ast as ast
from compiler.tokenizer import Token, Type, Position

def parse(tokens: list[Token]) -> ast.Expression:

    left_associative_binary_operators = [
        ['*', '/', '%'],
        ['+', '-'],
        ['<', '<=', '>', '>='],
        ['==', '!='],
        ['and'],
        ['or']
    ]
    lowest_precedence = len(left_associative_binary_operators)
    
    index = 0
    previous = None
    
    def peek() -> Token:
        if not index < len(tokens):
            if tokens:
                return Token(Type.END, "end of input", tokens[-1].position)
            else:
                return Token(Type.END, "end of input")
        return tokens[index]
    
    # 'consume(expected)' returns the token at 'pos'
    # and moves 'pos' forward.
    #
    # If the optional parameter 'expected' is given,
    # it checks that the token being consumed has that text.
    # If 'expected' is a list, then the token must have
    # one of the texts in the list.
    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal index, previous
        token = peek()
        if isinstance(expected, str) and token.content != expected:
            raise SyntaxError(f'{token.position}: expected "{expected}" instead of "{token.content}"')
        if isinstance(expected, list) and token.content not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise SyntaxError(f'{token.position}: expected one of: {comma_separated} instead of "{token.content}"')
        index += 1
        previous = token
        return token

    def parse_int_literal() -> ast.Literal:
        if not peek().type == Type.INT_LITERAL:
            raise SyntaxError(f'{peek().position}: expected integer literal instead of "{peek().content}"')
        token = consume()
        return ast.Literal(value = int(token.content), position = token.position)
    
    def parse_bool_literal() -> ast.Literal:
        if not peek().type == Type.BOOL_LITERAL:
            raise SyntaxError(f'{peek().position}: expected boolean literal instead of "{peek().content}"')
        token = consume(["true", "false"])
        return ast.Literal(value = token.content == "true", position = token.position)
    
    def parse_identifier() -> ast.Identifier:
        if not peek().type == Type.IDENTIFIER:
            raise SyntaxError(f'{peek().position}: expected identifier instead of "{peek().content}"')
        token = consume()
        return ast.Identifier(name = token.content, position = token.position)
    
    def parse_block() -> ast.Expression:
        position = consume("{").position
        statements = []
        if peek().content != '}':
            statements.append(parse_expression(True))
            while peek().content != '}':
                if previous and previous != Token(Type.PUNCTUATION, "}"):
                    consume(";")
                    if peek().type == Type.PUNCTUATION and peek().content == '}':
                        statements.append(ast.Literal(value = None, position = previous.position))
                        break
                elif peek().type == Type.PUNCTUATION and peek().content == ';':
                    position_ = consume(";").position
                    if peek().type == Type.PUNCTUATION and peek().content == '}':
                        statements.append(ast.Literal(value = None, position = position_))
                        break
                statements.append(parse_expression(True))
        consume("}")
        return ast.Block(statements = statements, position = position)
    
    def parse_parentheses() -> ast.Expression:
        consume("(")
        exp = parse_expression(False)
        consume(")")
        return exp
    
    def parse_function_call(name: ast.Expression) -> ast.Expression:
        position = consume("(").position
        arguments = []
        if peek().content != ')':
            arguments.append(parse_expression(False))
            while peek().type == Type.PUNCTUATION and peek().content == ',':
                consume(",")
                arguments.append(parse_expression(False))
        consume(")")
        return ast.FunctionCall(name = name, arguments = arguments, position = position)
    
    def parse_term() -> ast.Expression:
        exp = None
        if peek().type == Type.PUNCTUATION and peek().content == '{':
            exp = parse_block()
        elif peek().type == Type.PUNCTUATION and peek().content == '(':
            exp = parse_parentheses()
        elif peek().type == Type.INT_LITERAL:
            exp = parse_int_literal() # do not allow in function calls?
        elif peek().type == Type.BOOL_LITERAL:
            exp = parse_bool_literal() # do not allow in function calls?
        elif peek().type == Type.IDENTIFIER:
            exp = parse_identifier()
        else:
            raise SyntaxError(f'{peek().position}: expected expression instead of "{peek().content}"')
        while peek().type == Type.PUNCTUATION and peek().content == '(':
            exp = parse_function_call(exp)
        return exp

    def parse_while_expression():
        if peek().type == Type.KEYWORD and peek().content == "while":
            position = consume("while").position
            condition = parse_expression(False)
            consume("do")
            do = parse_expression(False)
            return ast.While(condition = condition, do = do, position = position)
        else:
            return parse_term()
    
    def parse_if_expression() -> ast.Expression:
        if peek().type == Type.KEYWORD and peek().content == "if":
            position = consume("if").position
            condition = parse_expression(False)
            consume("then")
            then_branch = parse_expression(False)
            if peek().type == Type.KEYWORD and peek().content == "else":
                consume("else")
                return ast.If(condition = condition, then_branch = then_branch, else_branch = parse_expression(False), position = position)
            else:
                return ast.If(condition = condition, then_branch = then_branch, else_branch = None, position = position)
        else:
            return parse_while_expression()
    
    def parse_unary_expression() -> ast.Expression:
        if peek().type == Type.OPERATOR and peek().content in ['-', 'not']:
            token = consume()
            op = token.content
            return ast.UnaryOp(op = op, right = parse_unary_expression(), position = token.position)
        else:
            return parse_if_expression()
    
    def parse_binary_expression(precedence: int) -> ast.Expression:
        if not precedence:
            return parse_unary_expression()
        exp = parse_binary_expression(precedence - 1)
        while peek().type == Type.OPERATOR and peek().content in left_associative_binary_operators[precedence - 1]:
            token = consume()
            op = token.content
            right = parse_binary_expression(precedence - 1)
            exp = ast.BinaryOp(left = exp, op = op, right = right, position = token.position)
        return exp
    
    def parse_assignment() -> ast.Expression: # combine to parse_binary_expression
        exp = parse_binary_expression(lowest_precedence)
        if peek().type == Type.OPERATOR and peek().content == '=':
            token = consume("=")
            op = token.content
            right = parse_assignment()
            exp = ast.BinaryOp(left = exp, op = op, right = right, position = token.position)
        return exp
    
    def parse_variable_declaration() -> ast.Expression:
        position = consume("var").position
        name = parse_identifier()
        type_exp = None
        if peek().type == Type.PUNCTUATION and peek().content == ':':
            consume(":")
            type_exp = parse_identifier() # allow FunctionType
        consume("=")
        value = parse_expression(False)
        return ast.VariableDeclaration(name = name, type_exp = type_exp, value = value, position = position)
    
    def parse_expression(top_level: bool) -> ast.Expression:
        if peek().type == Type.KEYWORD and peek().content == "var":
            if not top_level:
                raise SyntaxError(f'{peek().position}: variable declaration is only allowed directly inside {{blocks}} and in top-level expressions')
            return parse_variable_declaration()
        else:
            return parse_assignment()
    
    def parse_top_level() -> ast.Expression:
        if peek().type == Type.END:
            return ast.Literal(value = None, position = peek().position) #how should empty token list be represented?
        exp = parse_expression(True)
        if peek().type == Type.END:
            return exp
        statements = [exp]
        while peek().type != Type.END:
            if previous and not previous == Token(Type.PUNCTUATION, "}"):
                consume(";")
                if peek().type == Type.END:
                    statements.append(ast.Literal(value = None, position = previous.position))
                    break
            elif peek().type == Type.PUNCTUATION and peek().content == ';':
                position_ = consume(";").position
                if peek().type == Type.END:
                    statements.append(ast.Literal(value = None, position = position_))
                    break
            statements.append(parse_expression(True))
        return ast.Block(statements = statements, position = Position(1,1))

    return parse_top_level()