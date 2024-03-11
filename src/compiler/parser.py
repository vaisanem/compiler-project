
import compiler.ast as ast
from compiler.tokenizer import Token, Type

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
            raise Exception(f'{token.position}: expected "{expected}" instead of "{token.content}"')
        if isinstance(expected, list) and token.content not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.position}: expected one of: {comma_separated} instead of "{token.content}"')
        index += 1
        previous = token
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
    
    def parse_block() -> ast.Expression:
        consume("{")
        statements = []
        if peek().content != '}':
            statements.append(parse_expression(True))
            while peek().content != '}':
                if previous and previous != Token(Type.PUNCTUATION, "}"):
                    consume(";")
                    if peek().type == Type.PUNCTUATION and peek().content == '}':
                        statements.append(ast.Literal(None))
                        break
                elif peek().type == Type.PUNCTUATION and peek().content == ';':
                    consume(";")
                    if peek().type == Type.PUNCTUATION and peek().content == '}':
                        statements.append(ast.Literal(None))
                        break
                statements.append(parse_expression(True))
        consume("}")
        return ast.Block(statements)
    
    def parse_parentheses() -> ast.Expression:
        consume("(")
        exp = parse_expression(False)
        consume(")")
        return exp
    
    def parse_function_call(name: ast.Expression) -> ast.Expression:
        consume("(")
        arguments = []
        if peek().content != ')':
            arguments.append(parse_expression(False))
            while peek().type == Type.PUNCTUATION and peek().content == ',':
                consume(",")
                arguments.append(parse_expression(False))
        consume(")")
        return ast.FunctionCall(name, arguments)
    
    def parse_term() -> ast.Expression:
        exp = None
        if peek().type == Type.PUNCTUATION and peek().content == '{':
            exp = parse_block()
        elif peek().type == Type.PUNCTUATION and peek().content == '(':
            exp = parse_parentheses()
        elif peek().type == Type.INT_LITERAL:
            exp = parse_int_literal()
        elif peek().type == Type.BOOL_LITERAL:
            exp = parse_bool_literal()
        elif peek().type == Type.IDENTIFIER:
            exp = parse_identifier()
        else:
            raise Exception(f'{peek().position}: expected "(", literal or identifier instead of "{peek().content}"')
        while peek().type == Type.PUNCTUATION and peek().content == '(':
            exp = parse_function_call(exp)
        return exp

    def parse_while_expression():
        if peek().type == Type.KEYWORD and peek().content == "while":
            consume("while")
            condition = parse_expression(False)
            consume("do")
            do = parse_expression(False)
            return ast.While(condition, do)
        else:
            return parse_term()
    
    def parse_if_expression() -> ast.Expression:
        if peek().type == Type.KEYWORD and peek().content == "if":
            consume("if")
            condition = parse_expression(False)
            consume("then")
            then_branch = parse_expression(False)
            if peek().type == Type.KEYWORD and peek().content == "else":
                consume("else")
                return ast.If(condition, then_branch, parse_expression(False))
            else:
                return ast.If(condition, then_branch)
        else:
            return parse_while_expression()
    
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
        exp = parse_binary_expression(lowest_precedence)
        if peek().type == Type.OPERATOR and peek().content == '=':
            op = consume("=").content
            right = parse_assignment()
            exp = ast.BinaryOp(exp, op, right)
        return exp
    
    def parse_variable_declaration() -> ast.Expression:
        consume("var")
        name = parse_identifier()
        type_exp = None
        if peek().type == Type.PUNCTUATION and peek().content == ':':
            consume(":")
            #type_exp = parse_type_expression() TODO: add type expression
        consume("=")
        value = parse_expression(False)
        if isinstance(name, ast.Identifier):
            return ast.VariableDeclaration(name, type_exp, value)
        raise Exception("Alright, I think it's time for me to pack up an go.")
    
    def parse_expression(top_level: bool) -> ast.Expression:
        if peek().type == Type.KEYWORD and peek().content == "var":
            if not top_level:
                raise Exception(f'{peek().position}: variable declaration is only allowed directly inside {{blocks}} and in top-level expressions')
            return parse_variable_declaration()
        else:
            return parse_assignment()
    
    def parse_top_level() -> ast.Expression:
        if peek().type == Type.END:
            return ast.Literal(None) #how should empty token list be handled?
        exp = parse_expression(True)
        if peek().type == Type.END:
            return exp
        statements = [exp]
        while peek().type != Type.END:
            if previous and not previous == Token(Type.PUNCTUATION, "}"):
                consume(";")
                if peek().type == Type.END:
                    statements.append(ast.Literal(None))
                    break
            elif peek().type == Type.PUNCTUATION and peek().content == ';':
                consume(";")
                if peek().type == Type.END:
                    statements.append(ast.Literal(None))
                    break
            statements.append(parse_expression(True))
        return ast.Block(statements)

    return parse_top_level()