from compiler.types import Type, Unit, Int, Bool, FunctionType
from typing import Dict

class SymbolTable:
    
    class Scope:
        def __init__(self, parent) -> None:
            self.parent = parent # define type to be Scope?
            self.table: Dict[str, Type] = {}

    def __init__(self) -> None: # refactor
        self.sym_table = SymbolTable.Scope(None)
        for each in ['+', '-', '*', '/', '%']:
            self.insert(each, FunctionType([Int(), Int()], Int()))
        for each in ['<', '<=', '>', '>=', '==', '!=']:
            self.insert(each, FunctionType([Int(), Int()], Bool()))
        #self.insert('-', FunctionType([Int()], Int())) PREFIX unary_ etc / MAKE ENTRY A TABLE TO ALLOW POLYMORPHISM / HARD CODE IN THE TYPECHECKER?
        #self.insert('==', FunctionType([Bool(), Bool()], Bool()))
        #self.insert('!=', FunctionType([Bool(), Bool()], Bool()))
        self.insert("and", FunctionType([Bool(), Bool()], Bool()))
        self.insert("or", FunctionType([Bool(), Bool()], Bool()))
        self.insert("not", FunctionType([Bool()], Bool()))
        self.insert("print_int", FunctionType([Int()], Unit()))
        self.insert("print_bool", FunctionType([Bool()], Unit()))
        self.insert("read_int", FunctionType([], Int()))
        
    def init_scope(self) -> None:
        self.sym_table = SymbolTable.Scope(self.sym_table)

    def insert(self, symbol, value) -> bool:
        if not self.sym_table.table.get(symbol):
            self.sym_table.table[symbol] = value
            return True
        else:
            return False

    def lookup(self, symbol) -> Type | None:
        scope = self.sym_table
        while not scope.table.get(symbol):
            if not scope.parent:
                return None
            temp = scope.parent
        return scope.table.get(symbol)