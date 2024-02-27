
from dataclasses import dataclass

@dataclass
class Expression: #TODO: change to or add Statement? Add while, functions, variable declarations, code blocks?
    """Base class for AST nodes representing expressions."""

@dataclass
class Literal(Expression):
    value: int | bool | None
    # (value=None is used when parsing the keyword `unit`)

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOp(Expression): #rename to BinaryOperation, operator?
    left: Expression
    op: str
    right: Expression
    
@dataclass
class If(Expression): #Statement?
    condition: Expression
    then_branch: Expression
    else_branch: Expression | None = None