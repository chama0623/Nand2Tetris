import os, sys, re
from enum import Enum, auto

class SOURCE_TYPE(Enum):
    FILE = auto()
    DIR = auto()

class TOKEN_TYPE(Enum):
    KEYWORD = auto()
    SYMBOL = auto()
    IDENTIFIER = auto()
    INT_CONST = auto()
    STRING_CONST = auto()

class KEYWORD_TYPE(Enum):
    CLASS = auto()
    METHOD = auto()
    FUNCTION = auto()
    CONSTRUCTOR = auto()
    INT = auto()
    BOOLEAN = auto()
    CHAR = auto()
    VOID = auto()
    VAR = auto()
    STATIC = auto()
    FIELD = auto()
    LET = auto()
    DO = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    THIS = auto()

class KIND_TYPE(Enum):
    STATIC = auto()
    FIELD = auto()
    ARG = auto()
    VAR = auto()
    NONE = auto()

class SEGMENT_TYPE(Enum):
    CONSTANT = auto()
    ARGUMENT = auto()
    LOCAL = auto()
    STATIC = auto()
    THIS = auto()
    THAT = auto()
    POINTER = auto()
    TEMP = auto()

class COMMAND_TYPE(Enum):
    ADD = auto()
    SUB = auto()
    NEG = auto()
    EQ = auto()
    GT = auto()
    LT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

def get_source_type(path:str) -> SOURCE_TYPE:
    """pathがファイル(.jack)であるときSOURCE_TYPE.FILE, ディレクトリであるときSOURCE_TYPE.DIRを返す
    """
    if os.path.isfile(path):
        return SOURCE_TYPE.FILE
    elif os.path.isdir(path):
        return SOURCE_TYPE.DIR
    raise ValueError(f"Invalid path: {path}")

class JackTokenizer:
    def __init__(self, jack_file:str) -> None:
        self._tokens = []
        self._current_idx = -1
        self.current_token = ""
        self._key_words = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void",
                     "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
        self._symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ".", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]

        with open(jack_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        lines = self._clean_lines(lines)

        for l in lines:
            self._tokens = self._tokens + self._tokenize_line(l)
        print(self._tokens)

    def _clean_lines(self, lines:list) -> list:
        """入力文字列からコメント(複数行コメント含む)、改行文字を削除する.
        空白は削除せず残す.
        """
        in_multiline_comment = False # 前行が複数行コメントで閉じていないときTrue
        cleaned_lines = []
        for line in lines:
            if in_multiline_comment:
                if "*/" in line:
                    line = line.split("*/", 1)[1].strip()
                    in_multiline_comment = False
                else:
                    continue

            if "/*" in line:
                if "*/" in line:
                    head = line.split("/*", 1)[0]
                    tail = line.split("*/", 1)[1]
                    line = (head + tail).strip()
                else:
                    in_multiline_comment = True
                    line = line.split("/*", 1)[0].strip()

            line = line.split("//", 1)[0].strip()
            if line:
                cleaned_lines.append(line)

        return cleaned_lines

    def _tokenize_line(self, line:str) -> list:
        tokens = []
        while line :
            token = ""
            if match := re.match(r'"[^"]*"', line): # 文字列
                token = match.group()
            elif match := re.match(r'\d+', line): # 整数定数
                token = match.group()
            elif line[0] in self._symbols: # 先頭がシンボル
                token = line[0]
            else:
                """
                上記条件に合致しないとき
                最初にマッチした半角スペースまたは記号より前の塊を取り出す. 以下のような行では先頭だけではパースする位置を判断できないため、
                マッチした部分より前を取り出してtokenに代入する
                a+b
                main()
                SquareGame game
                """

                match = re.match(r'[^ \s{}()[\].,;+\-*/&|<>=~]+', line)
                if match:
                    token = match.group()

            if not token: # どれにも合致しないとき
                token = line.split(" ")[0]

            tokens.append(token)
            # lineをtokenと残りの部分に分ける
            line = line[len(token):].lstrip()

        return tokens

    def hasMoreTokens(self) -> bool:
        return self._current_idx+1 < len(self._tokens)

    def advance(self):
        if self.hasMoreTokens():
            self._current_idx += 1
            self.current_token = self._tokens[self._current_idx]

    def tokenType(self) -> TOKEN_TYPE:
        if re.match(r'"[^"]*"', self.current_token):
            return TOKEN_TYPE.STRING_CONST
        elif re.match(r'\d+', self.current_token):
            return TOKEN_TYPE.INT_CONST
        elif self.current_token in self._symbols:
            return TOKEN_TYPE.SYMBOL
        elif self.current_token in self._key_words:
            return TOKEN_TYPE.KEYWORD
        else:
            return TOKEN_TYPE.IDENTIFIER


    def keyword(self) -> KEYWORD_TYPE:
        key_words = {
            "class": KEYWORD_TYPE.CLASS,
            "constructor": KEYWORD_TYPE.CONSTRUCTOR,
            "function": KEYWORD_TYPE.FUNCTION,
            "method": KEYWORD_TYPE.METHOD,
            "field": KEYWORD_TYPE.FIELD,
            "static": KEYWORD_TYPE.STATIC,
            "var": KEYWORD_TYPE.VAR,
            "int": KEYWORD_TYPE.INT,
            "char": KEYWORD_TYPE.CHAR,
            "boolean": KEYWORD_TYPE.BOOLEAN,
            "void": KEYWORD_TYPE.VOID,
            "true": KEYWORD_TYPE.TRUE, 
            "false": KEYWORD_TYPE.FALSE, 
            "null": KEYWORD_TYPE.NULL, 
            "this": KEYWORD_TYPE.THIS,
            "let": KEYWORD_TYPE.LET, 
            "do": KEYWORD_TYPE.DO,
            "if": KEYWORD_TYPE.IF, 
            "else": KEYWORD_TYPE.ELSE, 
            "while": KEYWORD_TYPE.WHILE, 
            "return": KEYWORD_TYPE.RETURN
                    }

        if self.current_token in key_words:
            return key_words.get(self.current_token)

    def symbol(self) -> str:
        if self.tokenType() == TOKEN_TYPE.SYMBOL:
            return self.current_token
        else:
            return None

    def identifier(self) -> str:
        if self.tokenType() == TOKEN_TYPE.IDENTIFIER:
            return self.current_token
        else:
            return None

    def intVal(self) -> int:
        if self.tokenType() == TOKEN_TYPE.INT_CONST:
            return int(self.current_token)
        else:
            return None

    def stringVal(self) -> str:
        if self.tokenType() == TOKEN_TYPE.STRING_CONST:
            return self.current_token[1:-1]
        else:
            return None

class CompilationEngine:
    def __init__(self, jack_file:str, vm_file:str):
        self._vm_writer = VMWriter(vm_file)
        self._tokenizer = JackTokenizer(jack_file)

    def close(self) -> None:
        self._vm_writer.close()

    def compileClass(self) -> None:
        if not self._tokenizer.hasMoreTokens():
            return 
        self._tokenizer.advance()


        # keyword class
        self._tokenizer.advance()

        # className
        self._class_name = self._tokenizer.current_token
        self._tokenizer.advance()

        # symbol {
        self._tokenizer.advance()

        # Sevenでの検証のため、classVarDecはとりあえずないものと仮定
        # classVarDec
        # while self._tokenizer.current_token in ["static", "field"]:
        #     self.compileClassVarDec()

        # 次にここを作る いったんGeminiに方向性があってるか聞く
        # subroutineDec
        while self._tokenizer.current_token in ["constructor", "function", "method"]:
            self.compileSubroutine()

        # symbol }


    def compileClassVarDec(self) -> None:
        # <classVarDec>
        self._xml_file.write("<classVarDec>\n")

        # <keyword>static|field</keyword>
        self._write_xml("keyword", self._tokenizer.current_token)
        self._tokenizer.advance()

        # if type in [int, char, boolean]  
        #   <keyword>type</keyword>
        # else(type is className)
        #   <identifier>className</identifier>
        if self._tokenizer.current_token in ["int", "char", "boolean"]:
            self._write_xml("keyword", self._tokenizer.current_token)
        else:
            self._write_xml("identifier", self._tokenizer.current_token)
        self._tokenizer.advance()

        # <identifier>varName</identifier>
        self._write_xml("identifier", self._tokenizer.current_token)
        self._tokenizer.advance()

        while self._tokenizer.current_token != ";":
            # <symbol>,</symbol>
            self._write_xml("symbol", self._tokenizer.current_token)
            self._tokenizer.advance()
            
            # <identifier>varName</identifier>
            self._write_xml("identifier", self._tokenizer.current_token)
            self._tokenizer.advance()

        # <symbol>;</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)

        # </classVarDec>
        self._xml_file.write("</classVarDec>\n")
        self._tokenizer.advance()

    def compileSubroutine(self) -> None:
        # サブルーチン用のシンボルテーブル
        self._subroutine_table = SymbolTable()

        # keyword constructor|function|method
        subroutine_type = self._tokenizer.current_token
        self._tokenizer.advance()

        if subroutine_type == "method":
            self._subroutine_table.define("this", self._class_name, KIND_TYPE.ARG)

        # 戻り値はvmの記載に寄与しないためスキップ
        # if return-type in [void, int, char, boolean]  
        #   <keyword>type</keyword>
        # else (type is className)
        #   <identifier>className</identifier>
        # if self._tokenizer.current_token in ["void", "int", "char", "boolean"]:
        #     self._write_xml("keyword", self._tokenizer.current_token)
        # else:
        #     self._write_xml("identifier", self._tokenizer.current_token)
        self._tokenizer.advance()

        # identifier subroutineName
        self._subroutine_name = self._tokenizer.current_token
        self._tokenizer.advance()

        # symbol (
        self._tokenizer.advance()

        # parameterList
        self.compileParameterList()
        
        # symbol )
        self._tokenizer.advance()

        # subroutineBody
        self.compileSubroutineBody()

    def compileParameterList(self) -> None:
        while self._tokenizer.current_token != ")":
            # Sevenの実行には必要がないのでとりあえずpass
            # if type in [int, char, boolean]  
            #   <keyword>type</keyword>
            # else(type is className)
            #   <identifier>className</identifier>
            # if self._tokenizer.current_token in ["int", "char", "boolean"]:
            #     self._write_xml("keyword", self._tokenizer.current_token)
            # else:
            #     self._write_xml("identifier", self._tokenizer.current_token)
            self._tokenizer.advance()

            # <identifier>varName</identifier>
            # self._write_xml("identifier", self._tokenizer.current_token)
            self._tokenizer.advance()

            if self._tokenizer.current_token != ")":
                # <symbol>,</symbol>
                # self._write_xml("symbol", self._tokenizer.current_token)
                self._tokenizer.advance() 

    def compileSubroutineBody(self) -> None:
        var_count = 0
        # symbol {
        self._tokenizer.advance()

        #varDec
        while self._tokenizer.current_token == "var":
            self.compileVarDec()

        var_count = self._subroutine_table.varCount(KIND_TYPE.VAR)

        # function className.functionName varCountを書き込む
        self._vm_writer.writeFunction(f"{self._class_name}.{self._subroutine_name}", var_count)

        #statements
        self.compileStatements()

        # symbol }
        self._tokenizer.advance()

    def compileVarDec(self) -> None:
        # keyword var
        self._tokenizer.advance()

        # if type in [int, char, boolean]  
        #   <keyword>type</keyword>
        # else(type is className)
        #   <identifier>className</identifier>
        # if self._tokenizer.current_token in ["int", "char", "boolean"]:
        #     self._write_xml("keyword", self._tokenizer.current_token)
        # else:
        #     self._write_xml("identifier", self._tokenizer.current_token)
        _var_type = self._tokenizer.current_token
        self._tokenizer.advance()

        # identifier varName
        _var_name = self._tokenizer.current_token
        self._tokenizer.advance()

        self._subroutine_table.define(_var_name, _var_type, KIND_TYPE.VAR)

        while self._tokenizer.current_token != ";":
            # symbol ,
            self._tokenizer.advance() 

            # identifier varName
            _var_name = self._tokenizer.current_token
            self._tokenizer.advance()

            self._subroutine_table.define(_var_name, _var_type, KIND_TYPE.VAR)

        # symbol ;
        self._tokenizer.advance() 

    def compileStatements(self) -> None:

        while self._tokenizer.current_token in ["let", "if", "while", "do", "return"]:
            if self._tokenizer.current_token == "let":
                pass
                # self.compileLet()
            elif self._tokenizer.current_token == "if":
                pass
                # self.compileIf()
            elif self._tokenizer.current_token == "while":
                pass
                # self.compileWhile()
            elif self._tokenizer.current_token == "do":
                self.compileDo()
            elif self._tokenizer.current_token == "return":
                self.compileReturn()


    def compileLet(self) -> None:
        # <letStatement>
        self._xml_file.write("<letStatement>\n")

        # <keyword>let</keyword>
        self._write_xml("keyword", self._tokenizer.current_token)
        self._tokenizer.advance()

        # <identifier>varName</identifier>
        self._write_xml("identifier", self._tokenizer.current_token)
        self._tokenizer.advance()

        # if ('[' expression ']')?
        if self._tokenizer.current_token == "[":
            # <symbol>[</symbol>
            self._write_xml("symbol", self._tokenizer.current_token)
            self._tokenizer.advance()

            # expression
            self.compileExpression()

            # <symbol>]</symbol>
            self._write_xml("symbol", self._tokenizer.current_token)
            self._tokenizer.advance()

        # <symbol>=</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # expression
        self.compileExpression()

        # <symbol>;</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # </letStatement>
        self._xml_file.write("</letStatement>\n")

    def compileIf(self) -> None:
        # <ifStatement>
        self._xml_file.write("<ifStatement>\n")

        # <keyword>if</keyword>
        self._write_xml("keyword", self._tokenizer.current_token)
        self._tokenizer.advance()

        # <symbol>(</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # expression
        self.compileExpression()

        # <symbol>)</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # <symbol>{</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # statements
        self.compileStatements()

        # <symbol>}</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # (else { statements })?
        if self._tokenizer.current_token == "else":
            # <keyword>else</keyword>
            self._write_xml("keyword", self._tokenizer.current_token)
            self._tokenizer.advance()   

            # <symbol>{</symbol>
            self._write_xml("symbol", self._tokenizer.current_token)
            self._tokenizer.advance()

            # statements
            self.compileStatements()

            # <symbol>}</symbol>
            self._write_xml("symbol", self._tokenizer.current_token)
            self._tokenizer.advance()         

        # </ifStatement>
        self._xml_file.write("</ifStatement>\n")

    def compileWhile(self) -> None:
        # <whileStatement>
        self._xml_file.write("<whileStatement>\n")

        # <keyword>while</keyword>
        self._write_xml("keyword", self._tokenizer.current_token)
        self._tokenizer.advance()

        # <symbol>(</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # expression
        self.compileExpression()

        # <symbol>)</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # <symbol>{</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance()

        # statements
        self.compileStatements()

        # <symbol>}</symbol>
        self._write_xml("symbol", self._tokenizer.current_token)
        self._tokenizer.advance() 
        
        # </whileStatement>
        self._xml_file.write("</whileStatement>\n")

    def compileDo(self) -> None:
        _expression_count = 0
        # keyword do
        self._tokenizer.advance()

        # subroutineCall
        # subroutineName | (className|varName)
        _sub_routine_name = self._tokenizer.current_token
        self._tokenizer.advance()

        # if subroutineCall subroutineName(expressionList)
        if self._tokenizer.current_token == "(":
            # symbol (
            self._tokenizer.advance()

            # expressionList
            _expression_count = self.compileExpressionList()

            # symbol )
            self._tokenizer.advance()

        _sub_method_name = ""
        # if subroutineCall (className|varName).subroutineName(expressionList)
        if self._tokenizer.current_token == ".":
            # symbol .
            self._tokenizer.advance()

            # identifier subroutineName
            _sub_method_name = self._tokenizer.current_token
            self._tokenizer.advance()

            # symbol (
            self._tokenizer.advance()

            # expressionList
            _expression_count = self.compileExpressionList()

            # symbol )
            self._tokenizer.advance()

        # symbol ;
        self._tokenizer.advance()

        if _sub_method_name:
            _full_name = f"{_sub_routine_name}.{_sub_method_name}"
        else:
            # do function()のときは暗黙的にクラス名は自クラス
            # ClassName.function
            _full_name = f"{self._class_name}.{_sub_routine_name}"
        self._vm_writer.writeCall(_full_name, _expression_count)

        # doの場合引数は関係ないため、do function()でstackに積まれた0をpopする
        self._vm_writer.writePop(SEGMENT_TYPE.TEMP, 0)

    def compileReturn(self) -> None:

        # keyword return
        self._tokenizer.advance()

        if self._tokenizer.current_token != ";":
            self.compileExpression()
        else:
            self._vm_writer.writePush(SEGMENT_TYPE.CONSTANT, 0)

        # symbol ;
        self._tokenizer.advance()

        self._vm_writer.writeReturn()

    def compileExpression(self) -> None:
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

        # term
        self.compileTerm()

        # (op term)*
        while self._tokenizer.current_token in ops:
            op = self._tokenizer.current_token
            # symbol op
            # self._write_xml("symbol", self._tokenizer.current_token)
            self._tokenizer.advance()

            # term
            self.compileTerm()

            # a op bについてvmへの出力は以下順番のため、ここで演算子に応じたvmコードを出力する
            # push segment a
            # push segment b
            # op
            if op == "+":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.ADD)
            elif op == "-":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.SUB)
            elif op == "*":
                self._vm_writer.writeCall("Math.multiply", 2)
            elif op == "/":
                self._vm_writer.writeCall("Math.divide", 2)
            elif op == "<":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.LT)
            elif op == ">":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.GT)
            elif op == "=":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.EQ)
            elif op == "&":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.AND)
            elif op == "|":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.OR)

    def compileTerm(self) -> None:
        if self._tokenizer.tokenType() == TOKEN_TYPE.INT_CONST: # 正の整数定数
            self._vm_writer.writePush(SEGMENT_TYPE.CONSTANT, self._tokenizer.intVal())
            self._tokenizer.advance()
        elif self._tokenizer.tokenType() == TOKEN_TYPE.STRING_CONST: # 文字列
            # self._write_xml("stringConstant", self._tokenizer.stringVal())
            self._tokenizer.advance()
        elif self._tokenizer.tokenType() == TOKEN_TYPE.KEYWORD: # true, false, null
            # self._write_xml("keyword", self._tokenizer.current_token)
            self._tokenizer.advance()
        elif self._tokenizer.tokenType() == TOKEN_TYPE.IDENTIFIER: # varName|varName[expression]|subroutineCall
            _sub_routine_name = self._tokenizer.current_token
            self._tokenizer.advance()
            # if ('[' expression ']'
            _expression_count = 0
            _sub_method_name = ""
            if self._tokenizer.current_token == "[":
                # symbol [
                self._tokenizer.advance()

                # expression
                self.compileExpression()

                # symbol ]
                self._tokenizer.advance()

            # if subroutineCall subroutineName(expressionList)
            if self._tokenizer.current_token == "(":
                # symbol (
                self._tokenizer.advance()

                # expressionList
                _expression_count = self.compileExpressionList()

                # symbol )
                self._tokenizer.advance()

            # if subroutineCall (className|varName).subroutineName(expressionList)
            if self._tokenizer.current_token == ".":
                # symbol .
                self._tokenizer.advance()

                # identifier subroutineName
                _sub_method_name = self._tokenizer.current_token
                self._tokenizer.advance()

                # symbol (
                self._tokenizer.advance()

                # expressionList
                _expression_count = self.compileExpressionList()

                # symbol )
                self._tokenizer.advance()

            if _sub_method_name:
                _full_name = f"{_sub_routine_name}.{_sub_method_name}"
            else:
                _full_name = f"{self._class_name}.{_sub_routine_name}"
            self._vm_writer.writeCall(_full_name, _expression_count)

        elif self._tokenizer.current_token == "(":
            # symbol (
            self._tokenizer.advance()

            # expression
            self.compileExpression()

            # symbol )
            self._tokenizer.advance()

        elif unaryOp := self._tokenizer.current_token in ["-", "~"]:
            # symbol unaryOp 
            self._tokenizer.advance()

            # term
            self.compileTerm()

            if unaryOp == "-":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.NEG)
            else: # unaryOp == "~""
                self._vm_writer.writeArithmetic(COMMAND_TYPE.NOT)

    def compileExpressionList(self) ->int:
        expression_count = 0

        if self._tokenizer.current_token != ")":
            # expression
            self.compileExpression()
            expression_count +=1

            while self._tokenizer.current_token == ",":
                # symbol ,
                self._tokenizer.advance()

                # expression
                self.compileExpression()
                expression_count += 1

        return expression_count

class JackAnalyzer:
    def __init__(self, path:str):
        source_type = get_source_type(path)

        self._jack_files = []
        if source_type == SOURCE_TYPE.FILE:
            self._jack_files.append(path)
        elif source_type == SOURCE_TYPE.DIR:
            self._jack_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".jack")]

    def analyze(self) -> None:
        for jack_file in self._jack_files:
            vm_file = jack_file.rsplit(".", 1)[0] + ".vm"
            print(f"Compiling: {jack_file} -> {vm_file}")

            engine = CompilationEngine(jack_file, vm_file)
            engine.compileClass()
            engine.close()

class SymbolTable:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.table = {
            KIND_TYPE.STATIC: [],
            KIND_TYPE.FIELD: [],
            KIND_TYPE.ARG: [],
            KIND_TYPE.VAR: [],
        }

    def __str__(self) -> str:
        result = []
        for kind, items in self.table.items():
            result.append(f"{kind.name} : count={len(items)}")
            for item in items:
                result.append(f"  {item}")
        return "\n".join(result) if result else "SymbolTable is empty."

    def define(self, name:str, type: str, kind:KIND_TYPE) -> None:
        self.table[kind].append({"name":name, "type":type})

    def varCount(self, kind:KIND_TYPE) -> int:
        return len(self.table[kind])

    def kindOf(self, name:str) -> KIND_TYPE:
        for kind, items in self.table.items():
            for item in items:
                if item["name"] == name:
                    return kind
        return None

    def typeOf(self, name:str) -> str:
        for _, items in self.table.items():
            for item in items:
                if item["name"] == name:
                    return item["type"]
        return None

    def indexOf(self, name:str) -> int:
        for _, items in self.table.items():
            for i, item in enumerate(items):
                if item["name"] == name:
                    return i 
        return None

class VMWriter:
    def __init__(self, vm_file:str) -> None:
        self._vm_file = open(vm_file, "w", encoding="utf-8")

    def writePush(self, segment:SEGMENT_TYPE, index:int) -> None:
        segment_map = {
            SEGMENT_TYPE.CONSTANT: "constant",
            SEGMENT_TYPE.ARGUMENT: "argument",
            SEGMENT_TYPE.LOCAL: "local",
            SEGMENT_TYPE.STATIC: "static",
            SEGMENT_TYPE.THIS: "this",
            SEGMENT_TYPE.THAT: "that",
            SEGMENT_TYPE.POINTER: "pointer",
            SEGMENT_TYPE.TEMP: "temp",
        }
        segment_str = segment_map.get(segment, "")
        self._vm_file.write(f"push {segment_str} {index}\n")

    def writePop(self, segment:SEGMENT_TYPE, index:int) -> None:
        segment_map = {
            SEGMENT_TYPE.ARGUMENT: "argument",
            SEGMENT_TYPE.LOCAL: "local",
            SEGMENT_TYPE.STATIC: "static",
            SEGMENT_TYPE.THIS: "this",
            SEGMENT_TYPE.THAT: "that",
            SEGMENT_TYPE.POINTER: "pointer",
            SEGMENT_TYPE.TEMP: "temp",
        }
        segment_str = segment_map.get(segment, "")
        self._vm_file.write(f"pop {segment_str} {index}\n")

    def writeArithmetic(self, command:COMMAND_TYPE) -> None:
        command_map = {
            COMMAND_TYPE.ADD: "add",
            COMMAND_TYPE.SUB: "sub",
            COMMAND_TYPE.NEG: "neg",
            COMMAND_TYPE.EQ: "eq",
            COMMAND_TYPE.GT: "gt",
            COMMAND_TYPE.LT: "lt",
            COMMAND_TYPE.AND: "and",
            COMMAND_TYPE.OR: "or",
            COMMAND_TYPE.NOT: "not",
        }
        command_str = command_map.get(command, "")
        self._vm_file.write(f"{command_str}\n")

    def writeLabel(self, label:str) -> None:
        self._vm_file.write(f"label {label}\n")

    def writeGoto(self, label:str) -> None:
        self._vm_file.write(f"goto {label}\n")

    def writeIf(self, label:str) -> None:
        self._vm_file.write(f"if-goto {label}\n")

    def writeCall(self, name:str, nargs:int) -> None:
        self._vm_file.write(f"call {name} {nargs}\n")

    def writeFunction(self, name:str, nvars:int) -> None:
        self._vm_file.write(f"function {name} {nvars}\n") 

    def writeReturn(self) -> None:
        self._vm_file.write(f"return\n") 

    def close(self) -> None:
        self._vm_file.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: JackCompiler <filename.jack>")
        sys.exit(1)

    path = sys.argv[1]

    jack_analyzer = JackAnalyzer(path)
    jack_analyzer.analyze()


if __name__ == "__main__":
    main()