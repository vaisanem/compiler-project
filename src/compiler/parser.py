
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
    lowest_precedence = len(left_associative_binary_operators)
    
    pos = 0
    previous = None
    
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
    
    def parse_parentheses() -> ast.Expression:
        consume("(")
        exp = parse_block()
        consume(")")
        return exp
    
    def parse_function_call(name: ast.Expression) -> ast.Expression:
        consume("(")
        arguments = []
        if peek().content != ')':
            arguments.append(parse_block())
            while peek().type == Type.PUNCTUATION and peek().content == ',':
                consume(",")
                arguments.append(parse_block())
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
            raise Exception(f'{peek().content}: expected "(", literal or identifier')
        while peek().type == Type.PUNCTUATION and peek().content == '(':
            exp = parse_function_call(exp)
        if peek().type == Type.INT_LITERAL or peek().type == Type.BOOL_LITERAL or peek().type == Type.IDENTIFIER:
            raise Exception(f'{peek().position}: did not expect literal or identifier')
        return exp
    
    def parse_while_expression():
        exp = None
        if peek().type == Type.KEYWORD and peek().content == "while":
            consume("while")
            condition = parse_block()
            consume("do")
            do = parse_block()
            exp = ast.While(condition, do)
        else:
            exp = parse_term()
        return exp
    
    def parse_if_expression() -> ast.Expression:
        exp = None
        if peek().type == Type.KEYWORD and peek().content == "if":
            consume("if")
            condition = parse_block()
            consume("then")
            then_branch = parse_block()
            if peek().type == Type.KEYWORD and peek().content == "else":
                consume("else")
                exp = ast.If(condition, then_branch, parse_block())
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
        exp = parse_binary_expression(lowest_precedence)
        if peek().type == Type.OPERATOR and peek().content == '=':
            op = consume("=").content
            right = parse_assignment()
            exp = ast.BinaryOp(exp, op, right)
        return exp
    
    def parse_expression() -> ast.Expression: #check (in parse_term) that there is no rubbish (extra term) after an expression?
        exp = parse_assignment()
        return exp
    
    def parse_block2() -> ast.Expression: #make semicolon optional for blocks -> while true?
        statements = []
        if peek().type == Type.PUNCTUATION and peek().content == '{':
            consume("{")
            if peek().content != '}':
                statements.append(parse_block())
                while peek().content == ';':
                    consume(";")
                    if peek().content == '}':
                        statements.append(ast.Literal(None))
                    else:
                        statements.append(parse_block())
            consume("}")
        else:
            return parse_expression()
        return ast.Block(statements)
    
    def parse_block() -> ast.Expression:
        statements = []
        if peek().type == Type.PUNCTUATION and peek().content == '{':
            consume("{")
            if peek().content != '}':
                statements.append(parse_block())
                while True:
                    if not isinstance(statements[-1], ast.Block):
                        if peek().content != '}':
                            if previous and not previous == Token(Type.PUNCTUATION, "}"):
                                print(previous)
                                consume(";")
                                if peek().type == Type.PUNCTUATION and peek().content == '}':
                                    statements.append(ast.Literal(None))
                                    break
                            else:
                                if peek().type == Type.PUNCTUATION and peek().content == ';':
                                    consume(";")
                                    if peek().type == Type.PUNCTUATION and peek().content == '}':
                                        statements.append(ast.Literal(None))
                                        break
                                statements.append(parse_block())
                                continue
                        else:
                            break;
                    elif peek().type == Type.PUNCTUATION and peek().content == ';':
                        consume(";")
                        if peek().type == Type.PUNCTUATION and peek().content == '}':
                            statements.append(ast.Literal(None))
                            break
                    elif peek().content == '}':
                        break;
                    statements.append(parse_block())
            consume("}")
        else:
            return parse_expression()
        return ast.Block(statements)
    
    def parse_top_level() -> ast.Expression:
        if peek().type == Type.END:
            return ast.Literal(None) #how should empty token list be handled?
        exp = parse_block()
        if peek().type == Type.END:
            return exp
        statements = [exp]
        while True:
            if not isinstance(statements[-1], ast.Block):
                if peek().type != Type.END:
                    if previous and not previous == Token(Type.PUNCTUATION, "}"):
                        consume(";")
                        if peek().type == Type.END:
                            statements.append(ast.Literal(None))
                            break
                    else:
                        if peek().type == Type.PUNCTUATION and peek().content == ';':
                            consume(";")
                            if peek().type == Type.END:
                                statements.append(ast.Literal(None))
                                break
                        statements.append(parse_block())
                        continue
                else:
                    break;
            elif peek().type == Type.PUNCTUATION and peek().content == ';':
                consume(";")
                if peek().type == Type.END:
                    statements.append(ast.Literal(None))
                    break
            elif peek().type == Type.END:
                break
            statements.append(parse_block())
        return ast.Block(statements)
    
    def parse_top_level2() -> ast.Expression: #make semicolon optional for blocks -> while true?
        if peek().type == Type.END:
            return ast.Literal(None) #how should empty token list be handled?
        exp = parse_block()
        if peek().type == Type.END:
            return exp
        statements = [exp]
        if peek().content != ';':
            statements.append(parse_block())
        while peek().type == Type.PUNCTUATION and peek().content == ';':
            consume(";")
            if peek().type == Type.END:
                statements.append(ast.Literal(None))
            else:
                statements.append(parse_block()) 
        return ast.Block(statements)

    return parse_top_level()