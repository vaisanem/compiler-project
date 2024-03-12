from dataclasses import dataclass

@dataclass
class Type:
    """Base class for AST node types."""
    
@dataclass
class Unit(Type):
    pass
    
@dataclass
class Int(Type):
    pass
    
@dataclass
class Bool(Type):
    pass
    
@dataclass
class FunctionType(Type):
    param_types: list[Type]
    return_type: Type