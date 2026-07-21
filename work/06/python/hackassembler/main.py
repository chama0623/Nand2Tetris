import sys
from enum import Enum

class INSTRUCTION(Enum):
    A_INSTRUCTION = 0
    C_INSTRUCTION = 1
    L_INSTRUCTION = 2

def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.asm>")
        sys.exit(1)

    asm_file = sys.argv[1]
    print(f"Assembling {asm_file}...")
    parser = Parser(asm_file)
    while(parser.hasMoreLines()):
        parser.advanced()
        itype = parser.instructionType()
        if itype in (INSTRUCTION.A_INSTRUCTION, INSTRUCTION.L_INSTRUCTION):
            print(parser.symbol())
        else:
            print(parser.dest(), parser.comp(), parser.jump())
        print("")

class Parser:
    def __init__(self, asm_file:str) ->None:
        """コンストラクタ asmファイルを読み込んで文字列の前処理を行う"""
        self._asm_file = asm_file
        # ファイル全体をlistで読み込む
        with open(self._asm_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self._cmds = self._clean_lines(lines)
        self._current_idx = -1
        self._current_cmd = ""

    def _clean_lines(self, lines:list) -> list:
        """入力文字列からコメント、空白、改行文字を削除する"""
        return [
            code for l in lines
            if (code := l.split("//")[0].replace(" ","").strip()) # //より前の文字列から空白と改行文字を削除する
        ]

    def hasMoreLines(self) -> bool:
        """未処理の行があるか判定する"""
        return self._current_idx+1 < len(self._cmds)

    def advanced(self) -> None:
        """hasMoreLineがTrueのとき、次の命令を読み込む"""
        if self.hasMoreLines():
            self._current_idx += 1
            self._current_cmd = self._cmds[self._current_idx]
            print(f"{self._current_idx} : {self._current_cmd}")


    def instructionType(self) -> INSTRUCTION:
        """INSTRUCTIONの種類をENUMで返す"""
        #[0]参照だとcurrent_idxが-1のときエラーになるためstartwithで先頭文字をとる
        if self._current_cmd.startswith("@"):
            return INSTRUCTION.A_INSTRUCTION
        elif self._current_cmd.startswith("("):
            return INSTRUCTION.L_INSTRUCTION
        else:
            return INSTRUCTION.C_INSTRUCTION

    def symbol(self) -> str:
        """
        A_INSTRUCTIONのとき、@xxxから@を除いてxxxを返す.
        L_INSTRUCTIONのとき、(xxx)から()を除いてxxxを返す.
        """
        if self.instructionType() == INSTRUCTION.A_INSTRUCTION:
            return self._current_cmd[1:]
        elif self.instructionType() == INSTRUCTION.L_INSTRUCTION:
            return self._current_cmd[1:-1]
        else:
            return ""

    def _split_c_instruction(self) -> tuple[str, str, str]:
        """tuple(dest, comp, jump)を返す"""
        cmd = self._current_cmd
        # jumpとそれ以外に分ける
        if ";" in cmd:
            remaining, jump = cmd.split(";")
        else:
            remaining, jump = cmd, ""

        # destとcompに分ける
        if "=" in remaining:
            dest, comp = remaining.split("=")
        else:
            dest, comp = "", remaining

        return dest, comp, jump

    def dest(self) -> str:
        if self.instructionType() == INSTRUCTION.C_INSTRUCTION:
            return self._split_c_instruction()[0]
        else:
            return ""

    def comp(self) -> str:
        if self.instructionType() == INSTRUCTION.C_INSTRUCTION:
            return self._split_c_instruction()[1]
        else:
            return ""

    def jump(self) -> str:
        if self.instructionType() == INSTRUCTION.C_INSTRUCTION:
            return self._split_c_instruction()[2]
        else:
            return ""


if __name__ == "__main__":
    main()