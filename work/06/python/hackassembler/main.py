import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.asm>")
        sys.exit(1)

    asm_file = sys.argv[1]
    print(f"Assembling {asm_file}...")

if __name__ == "__main__":
    main()