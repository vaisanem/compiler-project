import compiler.ast as ast 
from compiler.types import Type, Unit, Int, Bool, FunctionType
from compiler.symbol_table import SymbolTable

declarable_types: list[str] = ["Unit", "Int", "Bool"]

def typecheck(node: ast.Expression, sym_table: SymbolTable) -> list[Type] | Type: # Add position to error messages
	match node:
		case ast.Literal():
			if node.value is None:
				return Unit()
			elif isinstance(node.value, bool):
				return Bool()
			elif isinstance(node.value, int):
				return Int()
			raise Exception("Can you do that again, and let's hope for a different result")
		case ast.Identifier():
			types = sym_table.lookup(node.name)
			if not types:
				raise NameError(f'Variable "{node.name}" not found')
			return types if len(types) > 1 else types[0]
		case ast.VariableDeclaration():
			var_type = node.type_exp
			assigned_type = typecheck(node.value, sym_table)
			if var_type is not None:
				if var_type.name not in declarable_types:
					raise TypeError(f'Unknown type "{var_type.name}"')
				var_type = eval(var_type.name)()
				if assigned_type != var_type:
					raise TypeError(f'Variable "{node.name.name}" expects type {var_type} instead of {assigned_type}')
			if not sym_table.insert(node.name.name, assigned_type):
				raise NameError(f'Variable "{node.name.name}" already declared in this scope')
			return Unit()
		case ast.UnaryOp(): # combine with BinaryOp general case?
			type_right = typecheck(node.right, sym_table)
			op_types = sym_table.lookup(node.op)
			if not op_types:
				raise Exception("I don't know what I'm doing honestly")
			for one in op_types: # make this work with multiple types?
				if not isinstance(one, FunctionType) or len(one.param_types) != 1:
					continue
				if type_right != one.param_types[0]:
					raise TypeError(f'Unary operator "{node.op}" expects right side to have type {one.param_types[0]} instead of {type_right}')
				return one.return_type	
		case ast.BinaryOp():
			type_left = typecheck(node.left, sym_table)
			type_right = typecheck(node.right, sym_table)
			if node.op == '=':
				if not isinstance(node.left, ast.Identifier):
					raise TypeError(f'Left side of assignment must be a variable name')
				elif type_left != type_right:
					raise TypeError(f'Assignment expects same type on both sides, instead left side was {type_left} and right side was {type_right}')
				# no need to do the assignment as the type can't change
				return type_right
			elif node.op in ['==', '!=']:
				if type_left != type_right: 
					raise TypeError(f'Binary operator "{node.op}" expects same type on both sides, instead left side was {type_left} and right side was {type_right}')
				return Bool()
			else: # combine with UnaryOp?
				op_types = sym_table.lookup(node.op)
				if not op_types:
					raise Exception("There is something fundamentally wrong with me")
				for one in op_types: # make this work with multiple types?
					if not isinstance(one, FunctionType) or len(one.param_types) != 2:
						continue
					if type_left != one.param_types[0]:
						raise TypeError(f'Binary operator "{node.op}" expects left side to have type {one.param_types[0]} instead of {type_left}')
					if type_right != one.param_types[1]:
						raise TypeError(f'Binary operator "{node.op}" expects right side to have type {one.param_types[1]} instead of {type_right}')
					return one.return_type
		case ast.FunctionCall():
			fun_type = typecheck(node.name, sym_table)
			if not isinstance(fun_type, FunctionType):
				raise TypeError(f'Expected a function instead of {fun_type}')
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
			sym_table.init_scope()
			return_type = Unit()
			for statement in node.statements:
				return_type = typecheck(statement, sym_table)
			sym_table.exit_scope()
			return return_type
	raise Exception("Alright, I think it's time for me to pack up an go")