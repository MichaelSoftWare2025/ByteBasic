import argparse
from compiler import Compiler

def main():
    parser = argparse.ArgumentParser(description="ByteBasic компилятор")
    parser.add_argument('-c', '--compile', type=str, help="Файл исходного кода .bas для компиляции")
    args = parser.parse_args()

    if args.compile:
        compiler = Compiler()
        with open(args.compile, 'r', encoding='utf-8') as f:
            source = f.read()
        bytecode = compiler.compile(source)
        out_file = args.compile.rsplit('.', 1)[0] + '.bbcode'
        compiler.save(bytecode, out_file)
        print(f"Скомпилировано в {out_file}")
    else:
        print("Укажите файл для компиляции: -c <file.bas>")

if __name__ == "__main__":
    main()
