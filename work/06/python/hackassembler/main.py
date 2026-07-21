import sys
from enum import Enum

class INSTRUCTION(Enum):
    A_INSTRUCTION = 0
    C_INSTRUCTION = 1
    L_INSTRUCTION = 2

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
            # print(f"{self._current_idx} : {self._current_cmd}")


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
        
    def reset_idx(self):
        """現在のidxとcmdをリセットする(第2パスの処理用)"""
        self._current_idx = -1
        self._current_cmd = ""

class Code:
    def dest(self, d:str) -> str:
        """destを2進数表示3bitの文字列で返す"""
        bin_dest = 0b000
        if "M" in d:
            bin_dest = bin_dest | 0b001
        if "D" in d:
            bin_dest = bin_dest | 0b010
        if "A" in d:
            bin_dest = bin_dest | 0b100
        return f"{bin_dest:03b}" # 03b:3桁のbinary表記で先頭を0埋めする
    
    def comp(self, c:str) -> str:
        """compを2進数表示7bitの文字列で返す.
        MとAでc1~c6は同じであることを利用してマッピングテーブルを削減する
        """
        comp_table = {
            "0": "101010",
            "1": "111111",
            "-1": "111010",
            "D": "001100",
            "A": "110000",
            "!D": "001101",
            "!A": "110001",
            "-D": "001111",
            "-A": "110011",
            "D+1": "011111",
            "A+1": "110111",
            "D-1": "001110",
            "A-1": "110010",
            "D+A": "000010",
            "D-A": "010011",
            "A-D": "000111",
            "D&A": "000000",
            "D|A": "010101",
        }
        if "M" in c:
            c_replaced = c.replace("M", "A")
            return "1" + comp_table.get(c_replaced, "000000") # 一応禁則入力に備えてdefault値を入れる
        else:
            return "0" + comp_table.get(c, "000000")

    def jump(self, j: str) -> str:
        """jumpを2進数表示3bitの文字列で返す"""
        jump_table = {
            "": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111",
        }
        return jump_table.get(j, "000")
    
class SymbolTable:
    def __init__(self) -> None:
        # 定義済みSymbolの追加
        self._table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KBD": 24576,
        }

        # R0~R15を追加する
        for i in range(16):
            self._table[f"R{i}"] = i
        
    def addEntry(self, symbol:str, address:int) -> None:
        """Symbol Tableに<K, V> = <symbol, address>を追加する"""
        self._table[symbol] = address

    def contains(self, symbol:str) -> bool:
        """Symbol TableのKeyにsymbokが含まれるときtrue"""
        return symbol in self._table
    
    def getAddress(self, symbol:str) -> int:
        """key symbolに対応するaddressを返す
        key symbolが存在しないとき、0を返す
        """
        return self._table.get(symbol, 0)

def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.asm>")
        sys.exit(1)

    asm_file = sys.argv[1]
    out_file = asm_file.rsplit(".", 1)[0] + ".hack"
    parser = Parser(asm_file)
    code = Code()
    symbol_table =  SymbolTable()
    results = []
    rom_address = 0 # 行番号の記録用
    ram_address = 16 # 変数に番号を付与する用
    print(f"Assembling {asm_file}...")
    print("Pass 1 Processing...")
    while parser.hasMoreLines():
        parser.advanced()
        itype = parser.instructionType()
        if itype == INSTRUCTION.L_INSTRUCTION:
            symbol_table.addEntry(parser.symbol(), rom_address)
        else:
            rom_address += 1
    # print(symbol_table._table)
    print("Done!")

    print("Pass 2 Processing...")
    parser.reset_idx()
    while parser.hasMoreLines():
        parser.advanced()
        itype = parser.instructionType()
        bin = ""
        if itype == INSTRUCTION.A_INSTRUCTION:
            sym = parser.symbol()
            if sym.isdigit(): #定数Symbolのとき
                address = int(sym)
            elif symbol_table.contains(parser.symbol()): # 定義済みSymbol, Pass1で登録済みのSymbol
                address = symbol_table.getAddress(sym)
            else: # 未登録の変数
                # Symbol Tableに追加する(未予約の16以降のアドレスに追加する)
                symbol_table.addEntry(parser.symbol(), ram_address)
                address = ram_address
                ram_address += 1
            bin = f"0{address:015b}"
        elif itype == INSTRUCTION.C_INSTRUCTION:
            pass
            comp, dest, jump = code.comp(parser.comp()), code.dest(parser.dest()), code.jump(parser.jump())
            bin = f"111{comp}{dest}{jump}"
        else: # L_INSTRUCTION
            continue

        results.append(bin)
        
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print("Done!")
    

if __name__ == "__main__":
    main()