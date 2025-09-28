import json
import operator
from bytecode import OPCODES

class ByteBasicVM:
    def __init__(self):
        self.vars = {}
        self.stack = []
        self.pc = 0
        self.labels = {}
        self.call_stack = []

    def preprocess_labels(self, bytecode):
        """Сохраняет все LABEL'ы"""
        for idx, instr in enumerate(bytecode):
            if instr[0] == OPCODES['LABEL']:
                self.labels[instr[1]] = idx

    def resolve_jump(self, arg, code_len):
        """Определяет куда прыгнуть (по индексу или по метке)"""
        if isinstance(arg, int):
            if arg < code_len:
                return arg
            elif arg in self.labels:
                return self.labels[arg]
        raise RuntimeError(f"Некорректный адрес перехода: {arg}")

    def resolve_value(self, v):
        """Разыменовывает переменные и конвертирует строки-числа в int"""
        if isinstance(v, str) and v in self.vars:
            v = self.vars[v]
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return v
        return v

    def safe_compare(self, a, b, op):
        a_val = self.resolve_value(a)
        b_val = self.resolve_value(b)

        if isinstance(a_val, (int, float)) and isinstance(b_val, str):
            try:
                b_val = int(b_val)
            except ValueError:
                raise RuntimeError(f"Невозможно сравнить значения: {a_val} и {b_val} (vars: {self.vars})")
        elif isinstance(b_val, (int, float)) and isinstance(a_val, str):
            try:
                a_val = int(a_val)
            except ValueError:
                raise RuntimeError(f"Невозможно сравнить значения: {a_val} и {b_val} (vars: {self.vars})")

        if isinstance(a_val, (int, float)) and isinstance(b_val, (int, float)):
            return op(a_val, b_val)
        
        if isinstance(a_val, str) and isinstance(b_val, str):
            return op(a_val, b_val)

        raise RuntimeError(f"Невозможно сравнить значения разных типов: {a_val} ({type(a_val).__name__}) и {b_val} ({type(b_val).__name__}) (vars: {self.vars})")


    def run(self, bytecode):
        self.preprocess_labels(bytecode)
        self.pc = 0

        while self.pc < len(bytecode):
            instr = bytecode[self.pc]
            opcode = instr[0]
            arg = instr[1] if len(instr) > 1 else None

            if opcode == OPCODES['LOAD_CONST']:
                self.stack.append(arg)

            elif opcode == OPCODES['STORE_VAR']:
                self.vars[arg] = self.stack.pop()

            elif opcode == OPCODES['LOAD_VAR']:
                self.stack.append(self.vars.get(arg, 0))

            elif opcode == OPCODES['PRINT']:
                value = self.resolve_value(self.stack.pop())
                print(value)

            elif opcode == OPCODES['INPUT']:
                val = input(f"{arg}? ")
                try:
                    self.vars[arg] = int(val)
                except ValueError:
                    self.vars[arg] = val

            elif opcode == OPCODES['COMPARE_EQ']:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.safe_compare(a, b, operator.eq))

            elif opcode == OPCODES['COMPARE_NEQ']:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.safe_compare(a, b, operator.ne))

            elif opcode == OPCODES['COMPARE_LT']:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.safe_compare(a, b, operator.lt))

            elif opcode == OPCODES['COMPARE_GT']:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.safe_compare(a, b, operator.gt))

            elif opcode == OPCODES['COMPARE_LE']:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.safe_compare(a, b, operator.le))

            elif opcode == OPCODES['COMPARE_GE']:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.safe_compare(a, b, operator.ge))

            elif opcode == OPCODES['JUMP_IF_TRUE']:
                cond = self.resolve_value(self.stack.pop())
                if cond:
                    self.pc = self.resolve_jump(arg, len(bytecode))
                    continue

            elif opcode == OPCODES['JUMP']:
                self.pc = self.resolve_jump(arg, len(bytecode))
                continue

            elif opcode == OPCODES['END']:
                break

            elif opcode == OPCODES['NOP'] or opcode == OPCODES['LABEL']:
                pass

            elif opcode == OPCODES['ADD']:
                b = self.resolve_value(self.stack.pop())
                a = self.resolve_value(self.stack.pop())
                self.stack.append(a + b)

            elif opcode == OPCODES['SUB']:
                b = self.resolve_value(self.stack.pop())
                a = self.resolve_value(self.stack.pop())
                self.stack.append(a - b)

            elif opcode == OPCODES['MUL']:
                b = self.resolve_value(self.stack.pop())
                a = self.resolve_value(self.stack.pop())
                self.stack.append(a * b)

            elif opcode == OPCODES['DIV']:
                b = self.resolve_value(self.stack.pop())
                a = self.resolve_value(self.stack.pop())
                self.stack.append(a / b)

            elif opcode == OPCODES['GOSUB']:
                self.call_stack.append(self.pc + 1)
                self.pc = self.resolve_jump(arg, len(bytecode))
                continue

            elif opcode == OPCODES['RETURN']:
                if not self.call_stack:
                    raise RuntimeError("RETURN без GOSUB")
                self.pc = self.call_stack.pop()
                continue

            elif opcode == OPCODES['JUMP_IF_TRUE_RETURN']:
                value = self.resolve_value(self.stack.pop())
                if value:
                    if not self.call_stack:
                        raise RuntimeError("JUMP_IF_TRUE_RETURN без GOSUB")
                    self.pc = self.call_stack.pop()
                    continue

            else:
                raise RuntimeError(f"Неизвестная инструкция: {opcode}")

            self.pc += 1

    def load_and_run(self, path):
        with open(path, encoding='utf-8') as f:
            code = json.load(f)
        self.run(code)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, help="Путь к .bbcode файлу")
    args = parser.parse_args()

    vm = ByteBasicVM()
    vm.load_and_run(args.file)
