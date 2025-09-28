import re
import json
from bytecode import OPCODES

compare_operator_map = {
    '<': 'COMPARE_LT',
    '>': 'COMPARE_GT',
    '=': 'COMPARE_EQ',
    '<=': 'COMPARE_LE',
    '>=': 'COMPARE_GE',
    '<>': 'COMPARE_NE',
}

class Compiler:
    def __init__(self):
        self.labels = {}
        self.bytecode = []
        self.for_stack = []
        self.data_table = []

    def tokenize(self, line):
        line = line.strip()
        if not line:
            return None
        parts = line.split(' ', 1)
        try:
            number = int(parts[0])
        except ValueError:
            raise SyntaxError(f"Неверный номер строки: {parts[0]}")
        content = parts[1] if len(parts) > 1 else ''
        return number, content

    def is_number(self, token):
        try:
            int(token)
            return True
        except ValueError:
            return False

    def compile_line(self, number, content):
        tokens = re.findall(r'\".*?\"|\S+', content)
        if not tokens:
            return
        cmd = tokens[0].upper()

        if cmd == 'LET':
            if len(tokens) < 4 or tokens[2] != '=':
                raise SyntaxError("LET var = value")
            var = tokens[1]
            val_token = tokens[3]
            if self.is_number(val_token):
                self.bytecode.append([OPCODES['LOAD_CONST'], int(val_token)])
            else:
                self.bytecode.append([OPCODES['LOAD_VAR'], val_token])
            self.bytecode.append([OPCODES['STORE_VAR'], var])

        elif cmd == 'PRINT':
            expr = content[6:].strip()
            if expr.startswith('"') and expr.endswith('"'):
                self.bytecode.append([OPCODES['LOAD_CONST'], expr.strip('"')])
            else:
                self.bytecode.append([OPCODES['LOAD_VAR'], expr])
            self.bytecode.append([OPCODES['PRINT']])

        elif cmd == 'INPUT':
            if len(tokens) < 2:
                raise SyntaxError("INPUT var")
            self.bytecode.append([OPCODES['INPUT'], tokens[1]])
            
        elif cmd == 'IF':
            if len(tokens) < 5:
                raise SyntaxError("IF <var> <op> <var/num> THEN ...")
            var1, op, var2 = tokens[1], tokens[2], tokens[3]
            if tokens[4] != 'THEN':
                raise SyntaxError("IF ... THEN")

            self.bytecode.append([OPCODES['LOAD_CONST'], int(var1)] if self.is_number(var1) else [OPCODES['LOAD_VAR'], var1])
            self.bytecode.append([OPCODES['LOAD_CONST'], int(var2)] if self.is_number(var2) else [OPCODES['LOAD_VAR'], var2])
            self.bytecode.append([OPCODES[compare_operator_map[op]]])

            if len(tokens) == 6 and tokens[5].upper() == 'RETURN':
                self.bytecode.append([OPCODES['JUMP_IF_TRUE_RETURN']])
            elif len(tokens) == 7 and tokens[5].upper() == 'GOTO':
                self.bytecode.append([OPCODES['JUMP_IF_TRUE'], int(tokens[6])])
            else:
                raise SyntaxError("THEN должно быть RETURN или GOTO")

        elif cmd == 'GOTO':
            if len(tokens) < 2:
                raise SyntaxError("GOTO <line>")
            self.bytecode.append([OPCODES['JUMP'], int(tokens[1])])

        elif cmd == 'FOR':
            if len(tokens) < 6 or tokens[2] != '=' or tokens[4].upper() != 'TO':
                raise SyntaxError("FOR var = start TO end [STEP step]")
            var = tokens[1]
            start_val = int(tokens[3]) if self.is_number(tokens[3]) else tokens[3]
            end_val = int(tokens[5]) if self.is_number(tokens[5]) else tokens[5]
            step_val = int(tokens[7]) if len(tokens) > 7 and tokens[6].upper() == 'STEP' else 1
            self.bytecode.append([OPCODES['LOAD_CONST'], start_val])
            self.bytecode.append([OPCODES['STORE_VAR'], var])
            self.for_stack.append({'var': var, 'end': end_val, 'step': step_val, 'start_line': number})

        elif cmd == 'NEXT':
            if not self.for_stack:
                raise SyntaxError("NEXT без FOR")
            loop = self.for_stack.pop()
            var, end_val, step_val, start_line = loop['var'], loop['end'], loop['step'], loop['start_line']
            self.bytecode.append([OPCODES['LOAD_VAR'], var])
            self.bytecode.append([OPCODES['LOAD_CONST'], step_val])
            self.bytecode.append([OPCODES['ADD']])
            self.bytecode.append([OPCODES['STORE_VAR'], var])
            self.bytecode.append([OPCODES['LOAD_VAR'], var])
            self.bytecode.append([OPCODES['LOAD_CONST'], end_val])
            self.bytecode.append([OPCODES['COMPARE_LE']])
            self.bytecode.append([OPCODES['JUMP_IF_TRUE'], start_line])

        elif cmd == 'GOSUB':
            self.bytecode.append([OPCODES['GOSUB'], int(tokens[1])])

        elif cmd == 'RETURN':
            self.bytecode.append([OPCODES['RETURN']])

        elif cmd == 'END':
            self.bytecode.append([OPCODES['END']])

        elif cmd == 'DATA':
            items = [int(x) if x.isdigit() else x.strip('"') for x in content[5:].split(',')]
            self.data_table.extend(items)

        elif cmd == 'READ':
            for var in tokens[1:]:
                self.bytecode.append([OPCODES['READ_VAR'], var])

        elif cmd == 'REM':
            self.bytecode.append([OPCODES['NOP']])

        else:
            raise SyntaxError(f"Неизвестная команда: {cmd}")

    def compile(self, source_code):
        self.bytecode.clear()
        self.labels.clear()
        for line in source_code.splitlines():
            tokenized = self.tokenize(line)
            if tokenized:
                number, content = tokenized
                self.labels[number] = len(self.bytecode)
                self.compile_line(number, content)

        final = []
        for instr in self.bytecode:
            if instr[0] in (OPCODES['JUMP'], OPCODES['JUMP_IF_TRUE'], OPCODES['GOSUB']):
                target = instr[1]
                if target not in self.labels:
                    raise ValueError(f"Метка {target} не найдена")
                final.append([instr[0], self.labels[target]])
            else:
                final.append(instr)
        return final

    def save(self, bytecode, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(bytecode, f)

if __name__ == '__main__':
    compiler = Compiler()
    with open('example.bas', encoding='utf-8') as f:
        source = f.read()
    bytecode = compiler.compile(source)
    compiler.save(bytecode, 'example.bbcode')
    print("Скомпилировано в example.bbcode")
