from dataclasses import dataclass

@dataclass
class Type:
    """Base class for AST node types."""
    
@dataclass
class Unit(Type):
    def __repr__(self) -> str:
        return Unit.__name__
    
@dataclass
class Int(Type):
    def __repr__(self) -> str:
        return Int.__name__
    
@dataclass
class Bool(Type):
    def __repr__(self) -> str:
        return Bool.__name__
    
@dataclass
class FunctionType(Type):
    param_types: list[Type]
    return_type: Type
    
    def __repr__(self) -> str:
        return f'({", ".join(map(str, self.param_types))}) => {self.return_type}'