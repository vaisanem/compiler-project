import compiler.ast as ast 
from compiler.types import Type, Unit, Int, Bool, FunctionType
from compiler.symbol_table import SymbolTable

def typecheck(node: ast.Expression, sym_table: SymbolTable) -> Type: # Built-in functions as separate type? Add position to error messages?
	match node:
		case ast.Literal():
			if node.value is None:
				return Unit()
			elif isinstance(node.value, bool):
				return Bool()
			elif isinstance(node.value, int):
				return Int()
			raise TypeError(f'Failed to resolve the type of: "{node.value}"')
		case ast.Identifier():
			types = sym_table.lookup(node.name)
			if not types:
				raise NameError(f'Variable "{node.name}" not found')
			return types[0] # We also lookup functions which could theoretically have alternative types
		case ast.VariableDeclaration(): # Allow shadowing built-in functions? How about and, or and not operators?
			var_type = node.type_exp # type_exp to type, typecheck type_exp?
			if var_type is None:
				var_type = typecheck(node.value, sym_table)
			else: # typed -> check that types match
				pass
			if not sym_table.insert(node.name, var_type):
				raise NameError(f'Variable "{node.name}" already declared in this scope')
			return Unit()
		case ast.FunctionCall():
			fun_type = typecheck(node.name, sym_table) # Expression allowed as name, add parameter that tells it's function name (no)?
			if not isinstance(fun_type, FunctionType):
				raise TypeError(f'Expected a function instead of {fun_type}') # make Type print nicely
			if len(node.arguments) != len(fun_type.param_types):
				raise TypeError(f'Function "{node.name}" expects {len(fun_type.param_types)} arguments instead of {len(node.arguments)}')
			for one in range(len(node.arguments)):
				arg_type = typecheck(node.arguments[one], sym_table)
				if arg_type != fun_type.param_types[one]:
					raise TypeError(f'Function "{node.name}" expects parameter {one} to have type {fun_type.param_types[one]} instead of {arg_type}')
			return fun_type.return_type
		case ast.If():
			cond_type = typecheck(node.condition, sym_table)
			if cond_type != Bool():
				raise TypeError(f'If expression expects type of condition to be boolean instead of {cond_type}')
			then_type = typecheck(node.then_branch, sym_table)
			if node.else_branch:
				else_type = typecheck(node.else_branch, sym_table)
				return then_type if cond_type else else_type
			else:
				return Unit()
		case ast.While():
			cond_type = typecheck(node.condition, sym_table)
			if cond_type != Bool():
				raise TypeError(f'While expression expects type of condition to be boolean instead of {cond_type}')
			typecheck(node.do, sym_table)
			return Unit()
		case ast.Block():
			sym_table = sym_table.init_scope() # Doesnt work
			return_type = Unit()
			for statement in node.statements:
				return_type = typecheck(statement, sym_table)
			return return_type
	raise TypeError("Idk whatever")