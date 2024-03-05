
from dataclasses import dataclass

@dataclass
class Expression: #TODO: change to or add Statement (as base class of Expression)?
    """Base class for AST nodes representing expressions."""

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
class BinaryOp(Expression): #Separate variable declaration?
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
    else_branch: Expression | None = None
    
@dataclass
class FunctionCall(Expression):
    name: Expression
    arguments: list[Expression]
    
@dataclass
class Block(Expression):
    statements: list[Expression] #Return value is defined by the last expression