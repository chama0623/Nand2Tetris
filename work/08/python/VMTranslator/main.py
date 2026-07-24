import os, sys
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

class SOURCE_TYPE(Enum):
    FILE = 0
    DIR = 1

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
        elif first_word == "label":
            return CMD_TYPE.C_LABEL
        elif first_word == "goto":
            return CMD_TYPE.C_GOTO
        elif first_word == "if-goto":
            return CMD_TYPE.C_IF
        elif first_word == "function":
            return CMD_TYPE.C_FUNCTION
        elif first_word == "return":
            return CMD_TYPE.C_RETURN
        elif first_word == "call":
            return CMD_TYPE.C_CALL

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
        base_name = os.path.basename(asm_file) # ファイル名の先頭に含まれるパス情報を削除
        self._filename = os.path.splitext(base_name)[0]
        self._label_count = 0 # 比較演算や関数定義のラベル生成に用いる

    def writeInit(self) -> None:
        # StackPointerを256に設定する
        asm = [
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ]
        self._file.write("\n".join(asm) + "\n")
        # 最初に呼び出す関数はSys.initであるので、これの呼び出しを記載する
        self.writeCall("Sys.init", 0)

    def setFileName(self, fileName:str) -> None:
        """Static変数はクラス名ごとに定義付けられるため、クラス(処理するvmファイル)が変わったことを伝える必要がある.
        クラス名はファイル名に対応するためこのメソッドでファイル名を変更できる
        """
        self._filename = fileName

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
        SEGMENT_MAP = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
        }
        TEMP_BASE_ADDRESS = 5
        POINTER_BASE_ADDRESS = 3
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

        elif command == CMD_TYPE.C_PUSH and segment in SEGMENT_MAP:
            """
            push segment n(index)が与えられたとき、以下のアセンブリコードを返す.
            push segment nはRAM[symbol+n]の値をstackにpushする.
            symbolはsegment(local, argument, this, that)に対応するベースアドレスの記録場所を表わす.
            # nをDレジスタに記録
            @n
            D=A
            # symbolセグメントのベースアドレスを取得し、symbol+nを求める
            @symbol
            A=D+M
            # RAM[symbol+n]の値をDレジスタに記録
            D=M
            # stackにpushする
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """
            symbol = SEGMENT_MAP[segment]
            asm = [
                f"@{index}",
                "D=A",
                f"@{symbol}",
                "A=D+M",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
            ]
            self._file.write("\n".join(asm) + "\n")
        elif command == CMD_TYPE.C_POP and segment in SEGMENT_MAP:
            """
            pop segment n(index)が与えられたとき、以下のアセンブリコードを返す.
            symbol+iとpopした値を同時にDレジスタに保持できないため、R13でpopした値を保持する
            # symvolセグメントのベースアドレスを取得し、symbol+nを求める
            @n
            D=A
            @symbol
            D=D+M
            # R13にsymbol+iを保持する
            @R13
            M=D
            # stackからpopする
            @SP
            M=M-1
            A=M
            D=M
            # RAM[symbol+i]にpopした値を記録する
            @R13
            A=M
            M=D
            """
            symbol = SEGMENT_MAP[segment]
            asm = [
            f"@{index}",
            "D=A",
            f"@{symbol}",
            "D=D+M",
            "@R13",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@R13",
            "A=M",
            "M=D", 
            ]
            self._file.write("\n".join(asm) + "\n")
        
        elif command == CMD_TYPE.C_PUSH and segment == "temp":
            """push temp n(index)が与えられたとき、以下のアセンブリコードを返す.
            tempのbase addressは5で固定されているため、アセンブラコード内で5+nを計算せず、事前に計算した値を
            アセンブラコードに埋め込む.
            @5+n
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """
            address = TEMP_BASE_ADDRESS + index
            asm = [
                f"@{address}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command == CMD_TYPE.C_POP and segment == "temp":
            """pop temp n(index)が与えられたとき、以下のアセンブリコードを返す.
            @SP
            M=M-1
            A=M
            D=M
            @5+n
            M=D
            """
            address = TEMP_BASE_ADDRESS + index
            asm = [
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{address}",
                "M=D",
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command == CMD_TYPE.C_PUSH and segment == "pointer":
            """push pointer n(index)が与えられたとき、以下のアセンブリコードを返す
            pointer 0はRAM[3](this)、1はRAM[4](that)に対応している
            @3+n
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """
            address = POINTER_BASE_ADDRESS + index
            asm = [
                f"@{address}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",    
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command == CMD_TYPE.C_POP and segment == "pointer":
            """pop pointer n(index)が与えられたとき、以下のアセンブリコードを返す
            @SP
            M=M-1
            A=M
            D=M
            @3+n
            M=D
            """
            address = POINTER_BASE_ADDRESS + index
            asm = [
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{address}",
                "M=D",
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command == CMD_TYPE.C_PUSH and segment == "static":
            """push static n(index)が与えられたとき、以下のアセンブリコードを返す
            出力するアセンブリのシンボル名はfoo.asmのとき@foo.3とする
            @FileName.n
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """
            asm = [
                f"@{self._filename}.{index}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
            ]
            self._file.write("\n".join(asm) + "\n")

        elif command == CMD_TYPE.C_POP and segment == "static":
            """pop static n(index)が与えられたとき、以下のアセンブリコードを返す
            @SP
            M=M-1
            A=M
            D=M
            @Filename.n
            M=D
            """
            asm = [
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{self._filename}.{index}",
                "M=D",
            ]
            self._file.write("\n".join(asm) + "\n")

    def writeLabel(self, label:str) -> None:
        asm = f"({label})"
        self._file.write(asm + "\n")

    def writeGoto(self, label:str) -> None:
        asm = [
            f"@{label}",
            "0;JMP",
        ]
        self._file.write("\n".join(asm) + "\n")

    def writeIf(self, label:str):
        asm = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{label}",
            "D;JNE",
        ]
        self._file.write("\n".join(asm) + "\n")

    def writeFunction(self, functionName:str, nVars:int):
        self.writeLabel(functionName)
        for _ in range(nVars):
            self.writePushPop(CMD_TYPE.C_PUSH, "constant", 0)

    def writeReturn(self) -> None:
        """returnが呼び出されたとき、以下のアセンブリコードを返す
        # frame = LCLをR13に一時的に保存
        @LCL
        D=M
        @R13
        M=D

        # retAddr = frame-5, RAM[retAddr]の値=戻り先のアドレスをR14に一時的に保存
        @5
        A=D-A # frame-5のアドレスに移動
        D=M # RAM[retAddr]のアドレスをDレジスタに保持
        @R14
        M=D

        # *ARG = pop()
        @SP # Stackの最上段に関数の戻り値が積まれているため、それをDレジスタに保持
        AM=M-1
        D=M

        @ARG # ARGの先頭アドレスに戻り値を書き込む
        A=M
        M=D

        # SP=ARG+1
        @ARG
        D=M+1
        @SP
        M=D

        # THAT = *(frame-1)
        @R13
        D=M
        @1
        A=D-A
        D=M
        @THAT
        M=D
        
        # THIS = *(frame-2)
        @R13
        D=M
        @2
        A=D-A
        D=M
        @THIS
        M=D
        
        # ARG = *(frame-3)
        @R13
        D=M
        @3
        A=D-A
        D=M
        @ARG
        M=D
        
        # LCL = *(frame-4)
        @R13
        D=M
        @4
        A=D-A
        D=M
        @LCL
        M=D

        # goto retAddr
        @R14
        A=M
        0;JMP
        """
        segments = ["THAT", "THIS", "ARG", "LCL"]
        asm = [
            "@LCL",
            "D=M",
            "@R13",
            "M=D",
            "@5",
            "A=D-A",
            "D=M",
            "@R14",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",
        ]
        # 各セグメントの復元用アセンブリコード
        for i,segment in enumerate(segments):
            temp_asm = [
                "@R13",
                "D=M",
                f"@{i+1}",
                "A=D-A",
                "D=M",
                f"@{segment}",
                "M=D",
            ]
            asm = asm + temp_asm

        # goto retAddr用のアセンブリコード
        asm.extend([
            "@R14",
            "A=M",
            "0;JMP",
        ])

        self._file.write("\n".join(asm) + "\n")

    def writeCall(self, functionName:str, nArgs:int) -> None:
        """call functionName nArgsが呼び出されたとき、以下のアセンブリコードを返す
        # push returnaddress iは一意なlabel_count
        @functionName$ret.i
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1

        # push segment segment=[LCL, ARG, THIS, THAT]の値をstackにpush
        @segment
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1

        # ARG=SP-5-nArgs
        @SP
        D=M
        @5
        D=D-A
        @nArgs # アセンブリコードにnArgs値を埋め込む
        D=D-A
        @ARG
        M=D

        #LCL=SP
        @SP
        D=M
        @LCL
        M=D

        goto function
        @functionName # functionName$ret.iラベルではないことに注意. (functionName)はfunction f nVarsで生成される
        0;JMP

        (functionName$ret.1)
        """
        segments = ["LCL", "ARG", "THIS", "THAT"]
        # push returnaddress
        asm = [
            f"@{functionName}$ret.{self._label_count}",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

        # push LCL, ARG, THIS, THAT
        for segment in segments:
            temp_asm = [
                f"@{segment}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
            ]
            asm = asm + temp_asm

        # ARG=SP-5-nArgs
        asm.extend([
            "@SP",
            "D=M",
            "@5",
            "D=D-A",
            f"@{nArgs}",
            "D=D-A",
            "@ARG",
            "M=D",        
        ])

        # LCL=SP
        asm.extend([
            "@SP",
            "D=M",
            "@LCL",
            "M=D", 
        ])

        # goto function
        # (functionName$ret.1)
        asm.extend([
            f"@{functionName}",
            "0;JMP",
            f"({functionName}$ret.{self._label_count})",
        ])

        self._file.write("\n".join(asm) + "\n")
        self._label_count +=1

    def close(self) -> None:
        self._file.close()

def get_source_type(path:str) -> SOURCE_TYPE:
    """pathがファイル(.vm)であるときSOURCE_TYPE.FILE, ディレクトリであるときSOURCE_TYPE.DIRを返す
    """
    if os.path.isfile(path):
        return SOURCE_TYPE.FILE
    elif os.path.isdir(path):
        return SOURCE_TYPE.DIR
    raise ValueError(f"Invalid path: {path}")

def translate_vm_file(vm_file:str, code_writer:CodeWriter) -> None:
    """指定されたvmファイルを、指定されたcode_writerでアセンブリに翻訳する
    """
    base_name = os.path.basename(vm_file)
    class_name = os.path.splitext(base_name)[0]
    code_writer.setFileName(class_name)

    parser = Parser(vm_file)
    print(f"Translating {vm_file}...")
    while parser.hasMoreLines():
        parser.advance()
        cmd_type, arg1, arg2 = parser.commandType(), parser.arg1(), parser.arg2()
        # print(cmd_type, arg1, arg2)

        if cmd_type in (CMD_TYPE.C_PUSH, CMD_TYPE.C_POP):
            code_writer.writePushPop(cmd_type, arg1, arg2)
        elif cmd_type == CMD_TYPE.C_ARITHMETIC:
            code_writer.writeArithmetic(arg1)
        elif cmd_type == CMD_TYPE.C_LABEL:
            code_writer.writeLabel(arg1)
        elif cmd_type == CMD_TYPE.C_GOTO:
            code_writer.writeGoto(arg1)
        elif cmd_type == CMD_TYPE.C_IF:
            code_writer.writeIf(arg1)
        elif cmd_type == CMD_TYPE.C_FUNCTION:
            code_writer.writeFunction(arg1, arg2)
        elif cmd_type == CMD_TYPE.C_RETURN:
            code_writer.writeReturn()
        elif cmd_type == CMD_TYPE.C_CALL:
            code_writer.writeCall(arg1, arg2)

    print("Done!")


def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.vm>")
        sys.exit(1)

    path = sys.argv[1]
    source_type = get_source_type(path)
    print(f"path = {path}")

    vm_files = []
    asm_file = ""
    if source_type == SOURCE_TYPE.FILE:
        vm_files.append(path)
        asm_file = path.rsplit(".", 1)[0] + ".asm"
    elif source_type == SOURCE_TYPE.DIR:
        # os.path.normpath : 絶対値pathに変換
        # os.path.basename : pathの最後=ディレクトリ名を取り出す
        # pathがhoge/とhogeでディレクトリ名が変わらないように上記関数で処理している
        dir_name = os.path.basename(os.path.normpath(path))
        asm_file = os.path.join(path, dir_name + ".asm")
        vm_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".vm")] # vmファイルの一覧を取得

    code_writer = CodeWriter(asm_file)
    if source_type ==SOURCE_TYPE.DIR:
        code_writer.writeInit()

    for vm_file in vm_files:
        translate_vm_file(vm_file, code_writer)

    code_writer.close()
    print("Complete translating!")

if __name__ == "__main__":
    main()