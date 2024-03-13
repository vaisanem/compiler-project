from compiler.types import Type, Unit, Int, Bool, FunctionType
from typing import Dict

class SymbolTable:
    
    class Scope:
        def __init__(self, parent) -> None:
            self.parent: SymbolTable.Scope = parent
            self.table: Dict[str, list[Type]] = {}

    def __init__(self) -> None: # Allow print and read?
        self.sym_table = SymbolTable.Scope(None)
        for each in ['+', '-', '*', '/', '%']:
            self.insert(each, FunctionType([Int(), Int()], Int()))
        self.sym_table.table['-'].append(FunctionType([Int()], Int())) # '-' as negation
        for each in ['<', '<=', '>', '>=', '==', '!=']:
            self.insert(each, FunctionType([Int(), Int()], Bool()))
        self.sym_table.table['=='].append(FunctionType([Bool(), Bool()], Bool())) # '==' for boolean values
        self.sym_table.table['!='].append(FunctionType([Bool(), Bool()], Bool())) # '!=' for boolean values
        self.insert("and", FunctionType([Bool(), Bool()], Bool()))
        self.insert("or", FunctionType([Bool(), Bool()], Bool()))
        self.insert("not", FunctionType([Bool()], Bool()))
        self.insert("print_int", FunctionType([Int()], Unit()))
        self.insert("print_bool", FunctionType([Bool()], Unit()))
        self.insert("read_int", FunctionType([], Int()))
        
    def init_scope(self) -> Scope:
        return SymbolTable.Scope(self.sym_table)

    def insert(self, symbol, value) -> bool:
        if not self.sym_table.table.get(symbol):
            self.sym_table.table[symbol] = [value]
            return True
        else:
            return False

    def lookup(self, symbol) -> list[Type] | None:
        scope = self.sym_table
        while not scope.table.get(symbol):
            if not scope.parent:
                return None
            scope = scope.parent
        return scope.table.get(symbol)