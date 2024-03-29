﻿import sys
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.symbol_table import SymbolTable

# add more commands as needed
usage = f"""
Usage: {sys.argv[0]} <command> [source_code_file]
    
Command 'typecheck':
    Runs the type checker on source code.

Common arguments:
    source_code_file        Optional. Defaults to standard input if missing.
 """.strip() + "\n"


def main() -> int:
    command: str | None = None
    input_file: str | None = None
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            print(usage)
            return 0
        elif arg.startswith('-'):
            raise Exception(f"Unknown argument: {arg}")
        elif command is None:
            command = arg
        elif input_file is None:
            input_file = arg
        else:
            raise Exception("Multiple input files not supported")

    def read_source_code() -> str:
        if input_file is not None:
            with open(input_file) as f:
                return f.read()
        else:
            return sys.stdin.read()

    if command is None:
        print(f"Error: command argument missing\n\n{usage}", file=sys.stderr)
        return 1

    if command == 'typecheck':
        source_code = read_source_code()
        typecheck(parse(tokenize(source_code)), SymbolTable())
        print("\nI approve ✓")
    else:
        print(f"Error: unknown command: {command}\n\n{usage}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
