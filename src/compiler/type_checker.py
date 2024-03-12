import compiler.ast as ast 
from compiler import types 

def typecheck(node: ast.Expression) -> types.Type: # Symbol table as parameter?
	match node:
		case ast.Literal():
			if node.value is None:
				return types.Unit()
			elif isinstance(node.value, bool):
				return types.Bool()
			elif isinstance(node.value, int):
				return types.Int()
			raise TypeError(f"Unknown literal type: {node.value}")
		case ast.Identifier(): # lookup in symbol table
			return types.Type()
	raise TypeError(f"Idk whatever")