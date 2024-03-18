
from dataclasses import dataclass
from compiler.tokenizer import Position

@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    position: Position

@dataclass
class Literal(Expression):
    value: int | bool | None
    # (value=None is used when parsing the keyword `unit`)

@dataclass
class Identifier(Expression):
    name: str
    
@dataclass
class UnaryOp(Expression):
    op: str
    right: Expression

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression
    
@dataclass
class While(Expression):
    condition: Expression
    do: Expression
    
@dataclass
class If(Expression):
    condition: Expression
    then_branch: Expression
    else_branch: Expression | None
    
@dataclass
class FunctionCall(Expression):
    name: Expression
    arguments: list[Expression]
    
@dataclass
class VariableDeclaration(Expression):
    name: Identifier
    type_exp: Identifier | None
    value: Expression
    
@dataclass
class Block(Expression):
    statements: list[Expression] #Return value is defined by the last expression