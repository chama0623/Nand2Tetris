import sys
from enum import Enum

class CMD_TYPE(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8

class Parser:
    def __init__(self, vm_file:str) -> None:
        self._vm_file = vm_file
        with open(self._vm_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        self._cmds = self._clean_lines(lines)
        self._current_idx = -1
        self._current_cmd = ""

    def _clean_lines(self, lines:list) -> list:
        """入力文字列からコメント、改行文字を削除する.
        空白は削除せず残す
        """
        return [
            code for l in lines
            if (code := l.split("//")[0].strip())
        ]
    
    def hasMoreLines(self) -> bool:
        return self._current_idx+1 < len(self._cmds)
    
    def advance(self) -> None:
        if self.hasMoreLines():
            self._current_idx += 1
            self._current_cmd = self._cmds[self._current_idx]

    def commandType(self) -> CMD_TYPE:
        """現在のコマンドのTYPEを返す
        """
        ARITHMETIC_COMMANDS = {
            "add",
            "sub",
            "neg",
            "eq",
            "gt",
            "lt",
            "and",
            "or",
            "not",
        }

        if (first_word := self._current_cmd.split()[0]) in ARITHMETIC_COMMANDS:
            return CMD_TYPE.C_ARITHMETIC
        elif first_word == "push":
            return CMD_TYPE.C_PUSH
        elif first_word == "pop":
            return CMD_TYPE.C_POP
        # 8章で残りのコマンドタイプを追加する.ひとまずは算術論理コマンドとpush,popしかでないと仮定する

    def arg1(self) -> str:
        splited_cmds = self._current_cmd.split()
        if (cmd_type := self.commandType()) == CMD_TYPE.C_RETURN:
            return ""
        elif cmd_type == CMD_TYPE.C_ARITHMETIC:
            return splited_cmds[0]
        else:
            return splited_cmds[1]

    def arg2(self) -> int:
        splited_cmds = self._current_cmd.split()
        CALLABLE_TYPE = [CMD_TYPE.C_PUSH, CMD_TYPE.C_POP, CMD_TYPE.C_FUNCTION, CMD_TYPE.C_CALL]
        if self.commandType() in CALLABLE_TYPE:
            return int(splited_cmds[2])
        else:
            return 0

class CodeWriter:
    def __init__(self, asm_file:str) -> None:
        self._file = open(asm_file, "w", encoding="utf-8")
        self._label_count = 0

    def writeArithmetic(self, command:str) -> None:
        unary_operators = {
            "neg" : "-",
            "not" : "!"
        }
        binary_operators = {
            "add" : "+",
            "sub" : "-",
            "and" : "&",
            "or" : "|",
        }
        compare_operators = {
            "eq": "JEQ",
            "gt": "JGT",
            "lt": "JLT",
        }

        if command in unary_operators:
            """
            単項演算子が与えられたとき、以下のアセンブリコードを返す
            @SP
            M=M-1
            A=M
            M=?M(?は指定された単項演算)
            @SP
            M=M+1
            """
            operator = unary_operators[command]
            asm = [
                "@SP",
                "M=M-1",
                "A=M",
                f"M={operator}M",
                "@SP",
                "M=M+1",
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command in binary_operators:
            operator = binary_operators[command]
            """
            2項演算子が与えられたとき、以下のアセンブリコードを返す
            # SP-1(arg2)を取り出す
            @SP
            M=M-1
            A=M
            D=M # 値をDレジスタに記録
            # SP-2(arg1)を取り出す
            @SP
            M=M-1
            A=M
            M=D ? M # arg1 ? arg2(?は指定された2項演算). 引き算はD ? Mにしてはいけない
            # SPがarg1にいるので、1つ進める
            @SP
            M=M+1
            """
            asm = [
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "M=M-1",
                "A=M",
                f"M=M-D" if command == "sub" else f"M=D{operator}M",
                "@SP",
                "M=M+1",
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command in compare_operators:
            operator = compare_operators[command]
            """
            比較演算子が与えられたとき、以下のアセンブリコードを返す
            # SP-1(arg2)を取り出す
            @SP
            M=M-1
            A=M
            D=M # 値をDレジスタに記録
            
            # SP-2(arg1)を取り出す
            @SP
            M=M-1
            A=M
            
            # D = arg1 - arg2
            D=M-D
            @TRUE_LABEL_*(*はlabel_count)
            D;?(?は指定された比較演算)
            
            # FALSEの時の処理
            D=0
            @END_LABEL_*
            0;JMP

            # TRUEの時の処理
            (TRUE_LABEL_*)
            D=-1
            (END_LABEL_*)

            # DをStackに書く
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """
            asm = [
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                
                "@SP",
                "M=M-1",
                "A=M",
                
                "D=M-D",
                f"@TRUE_LABEL_{self._label_count}",
                f"D;{operator}",
                "D=0",
                f"@END_LABEL_{self._label_count}",
                "0;JMP",

                f"(TRUE_LABEL_{self._label_count})",
                "D=-1",
                f"(END_LABEL_{self._label_count})",

                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",                
            ]
            self._file.write("\n".join(asm) + "\n")
            self._label_count += 1

    def writePushPop(self, command:CMD_TYPE, segment:str, index:int) -> None:
        if command == CMD_TYPE.C_PUSH and segment == "constant":
            """
            push constant n(index)が与えられたとき、以下のアセンブリコードを返す

            @n # Aレジスタにnを入れる
            D=A # DレジスタにA(=n)を記録する
            @SP # AレジスタにSPを入れる(RAM[0]を指す). 
            A=M # SPの値をAレジスタに入れる. RAM[0]=256(RAMのStack領域の先頭アドレス)で初期化されている
            M=D # RAM[A]にDレジスタの値を入れる
            @SP # AレジスタにSPを入れる
            M=M+1 # SPの値をインクリメント(SPを1つ進める)
            """
            asm = [
            f"@{index}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command == CMD_TYPE.C_POP:
            pass
        else:
            pass

    def close(self) -> None:
            self._file.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.vm>")
        sys.exit(1)

    vm_file = sys.argv[1]
    asm_file = vm_file.rsplit(".", 1)[0] + ".asm"
    parser = Parser(vm_file)
    code_writer = CodeWriter(asm_file)
    print(f"Translating {vm_file}...")
    while parser.hasMoreLines():
        parser.advance()
        cmd_type, arg1, arg2 = parser.commandType(), parser.arg1(), parser.arg2()
        # print(cmd_type, arg1, arg2)

        if cmd_type == CMD_TYPE.C_PUSH:
            code_writer.writePushPop(cmd_type, arg1, arg2)
        elif cmd_type == CMD_TYPE.C_ARITHMETIC:
            code_writer.writeArithmetic(arg1)

    code_writer.close()
    print("Done!")

if __name__ == "__main__":
    main()