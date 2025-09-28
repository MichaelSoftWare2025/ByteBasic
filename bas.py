import argparse
from vm import ByteBasicVM

def main():
    parser = argparse.ArgumentParser(description="ByteBasic интерпретатор")
    parser.add_argument('-f', '--file', type=str, help="Файл байткода .bbcode для исполнения")
    args = parser.parse_args()

    if args.file:
        vm = ByteBasicVM()
        vm.load_and_run(args.file)
    else:
        print("Укажите файл байткода: -f <file.bbcode>")

if __name__ == "__main__":
    main()
