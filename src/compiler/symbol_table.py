from compiler.types import Type, Unit, Int, Bool, FunctionType

class SymbolTable:
    
    class Scope:
        def __init__(self, parent) -> None:
            self.parent: SymbolTable.Scope = parent
            self.table: dict[str, list[Type]] = {}
            
        def insert(self, symbol, value) -> bool:
            if not self.table.get(symbol):
                self.table[symbol] = [value]
                return True
            else:
                return False
            
        def lookup(self, symbol) -> list[Type] | None:
            return self.table.get(symbol)

    def __init__(self) -> None: # Add '==', '!=', 'print' and 'read'?
        self.current_scope = SymbolTable.Scope(None)
        for each in ['+', '-', '*', '/', '%']:
            self.insert(each, FunctionType([Int(), Int()], Int()))
        self.current_scope.table['-'].append(FunctionType([Int()], Int())) # '-' as negation
        for each in ['<', '<=', '>', '>=']:
            self.insert(each, FunctionType([Int(), Int()], Bool()))
        self.insert("and", FunctionType([Bool(), Bool()], Bool()))
        self.insert("or", FunctionType([Bool(), Bool()], Bool()))
        self.insert("not", FunctionType([Bool()], Bool()))
        self.insert("print_int", FunctionType([Int()], Unit()))
        self.insert("print_bool", FunctionType([Bool()], Unit()))
        self.insert("read_int", FunctionType([], Int()))
        
    def init_scope(self) -> None:
        self.current_scope = SymbolTable.Scope(self.current_scope)
        
    def exit_scope(self) -> None:
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    def insert(self, symbol, value) -> bool:
        return self.current_scope.insert(symbol, value)

    def lookup(self, symbol) -> list[Type] | None:
        scope = self.current_scope
        while scope:
            current_type = scope.lookup(symbol)
            if current_type:
                return current_type
            scope = scope.parent
        return None