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
        self._label_index = 0 # 一意なラベル生成用

    def close(self) -> None:
        self._vm_writer.close()

    def compileClass(self) -> None:
        # クラス用のシンボルテーブル
        self._class_table = SymbolTable()

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

        # classVarDec
        while self._tokenizer.current_token in ["static", "field"]:
             self.compileClassVarDec()

        # subroutineDec
        while self._tokenizer.current_token in ["constructor", "function", "method"]:
            self.compileSubroutine()

        # symbol }

    def compileClassVarDec(self) -> None:
        # keyword static|field
        _kind = KIND_TYPE.STATIC if self._tokenizer.current_token == "static" else KIND_TYPE.FIELD
        self._tokenizer.advance()

        # if type in [int, char, boolean]  
        #   <keyword>type</keyword>
        # else(type is className)
        #   <identifier>className</identifier>
        _type = self._tokenizer.current_token
        self._tokenizer.advance()

        # identifier varName
        _name = self._tokenizer.current_token
        self._tokenizer.advance()

        self._class_table.define(_name, _type, _kind)

        while self._tokenizer.current_token != ";":
            # symbol ,
            self._tokenizer.advance()
            
            # identifier varName
            _name = self._tokenizer.current_token
            self._tokenizer.advance()

            self._class_table.define(_name, _type, _kind)

        # symbol ;
        self._tokenizer.advance()

    def compileSubroutine(self) -> None:
        # self._label_index = 0
        # サブルーチン用のシンボルテーブル
        self._subroutine_table = SymbolTable()

        # keyword constructor|function|method
        self._subroutine_type = self._tokenizer.current_token
        self._tokenizer.advance()

        if self._subroutine_type == "method":
            self._subroutine_table.define("this", self._class_name, KIND_TYPE.ARG)

        # 戻り値の型をスキップ
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
            # type in [int, char, boolean] | className
            _type = self._tokenizer.current_token
            self._tokenizer.advance()

            # identifier varName
            _var_name = self._tokenizer.current_token
            self._tokenizer.advance()

            self._subroutine_table.define(_var_name, _type, KIND_TYPE.ARG)

            if self._tokenizer.current_token != ")":
                # symbol ,
                self._tokenizer.advance() 

    def compileSubroutineBody(self) -> None:
        # symbol {
        self._tokenizer.advance()

        # varDec
        while self._tokenizer.current_token == "var":
            self.compileVarDec()

        var_count = self._subroutine_table.varCount(KIND_TYPE.VAR)
        self._vm_writer.writeFunction(f"{self._class_name}.{self._subroutine_name}", var_count)

        if self._subroutine_type == "method":
            self._vm_writer.writePush(SEGMENT_TYPE.ARGUMENT, 0)
            self._vm_writer.writePop(SEGMENT_TYPE.POINTER, 0)
        elif self._subroutine_type == "constructor":
            field_count = self._class_table.varCount(KIND_TYPE.FIELD)
            self._vm_writer.writePush(SEGMENT_TYPE.CONSTANT, field_count)
            self._vm_writer.writeCall("Memory.alloc", 1)
            self._vm_writer.writePop(SEGMENT_TYPE.POINTER, 0)

        # statements
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
                self.compileLet()
            elif self._tokenizer.current_token == "if":
                self.compileIf()
            elif self._tokenizer.current_token == "while":
                self.compileWhile()
            elif self._tokenizer.current_token == "do":
                self.compileDo()
            elif self._tokenizer.current_token == "return":
                self.compileReturn()

    def _kind_to_segment(self, kind: KIND_TYPE) -> SEGMENT_TYPE:
        mapping = {
            KIND_TYPE.STATIC: SEGMENT_TYPE.STATIC,
            KIND_TYPE.FIELD: SEGMENT_TYPE.THIS,
            KIND_TYPE.ARG: SEGMENT_TYPE.ARGUMENT,
            KIND_TYPE.VAR: SEGMENT_TYPE.LOCAL,
        }
        return mapping.get(kind)

    def _lookup_var(self, name:str) ->tuple:
        """
        サブルーチンレベルのシンボルテーブルでnameを検索し、見つかった場合は(kind, index, type)を返す.
        サブルーチンレベルのシンボルテーブルで見つからない場合は、クラスレベルのシンボルテーブルを検索する.
        どちらのシンボルテーブルにも見つからない場合、(None, None, None)を返す
        """
        kind = self._subroutine_table.kindOf(name)
        if kind is not None and kind != KIND_TYPE.NONE:
            return kind, self._subroutine_table.indexOf(name), self._subroutine_table.typeOf(name)

        kind = self._class_table.kindOf(name)
        if kind is not None and kind != KIND_TYPE.NONE:
            return kind, self._class_table.indexOf(name), self._class_table.typeOf(name)
            
        return None, None, None

    def compileLet(self) -> None:
        # keyword let
        self._tokenizer.advance()

        # identifier varName
        _var_name = self._tokenizer.current_token
        _kind, _index, _ = self._lookup_var(_var_name)
        _segment = self._kind_to_segment(_kind)
        self._tokenizer.advance()
        is_array = False

        # if ('[' expression ']')?
        if self._tokenizer.current_token == "[":
            is_array = True
            # 配列のベースアドレスをpush
            _segment = self._kind_to_segment(_kind)
            self._vm_writer.writePush(_segment, _index)

            # symbol [
            self._tokenizer.advance()

            # expression
            self.compileExpression()

            # <symbol>]</symbol>
            self._tokenizer.advance()

            # 配列のベースアドレス + indexで実際にアクセスするアドレスを求める
            self._vm_writer.writeArithmetic(COMMAND_TYPE.ADD)

        # symbol =
        self._tokenizer.advance()

        # expression
        self.compileExpression()

        # symbol ;
        self._tokenizer.advance()

        if is_array:
            self._vm_writer.writePop(SEGMENT_TYPE.TEMP, 0)     # 右辺の値を一時退避
            self._vm_writer.writePop(SEGMENT_TYPE.POINTER, 1)  # アドレスを THAT にセット
            self._vm_writer.writePush(SEGMENT_TYPE.TEMP, 0)    # 右辺の値を復元
            self._vm_writer.writePop(SEGMENT_TYPE.THAT, 0)     # THAT 0 にポップ
        else:
            # pop varName(kind index)
            self._vm_writer.writePop(_segment, _index)

    def _get_label(self) ->str:
        _label = f"{self._class_name}_{self._label_index}"
        self._label_index += 1
        return _label

    def compileIf(self) -> None:
        """
        Jack
        if(expression0)
            statement1
        else
            statement2
        
        vm
        compileExpression0() # 真のとき-1, 偽のとき0
        not
        if-goto L1
        compileExpression1()
        goto L2
        label L1
        compileExpression2()
        label L2
        """
        # keyword if
        self._tokenizer.advance()

        # symbol (
        self._tokenizer.advance()

        # expression
        self.compileExpression()

        # symbol )
        self._tokenizer.advance()

        # 条件が偽のときのジャンプ先ラベル
        _label_false = self._get_label()
        
        # 条件式の結果を反転して偽のときにジャンプさせる
        self._vm_writer.writeArithmetic(COMMAND_TYPE.NOT)
        self._vm_writer.writeIf(_label_false)

        # symbol {
        self._tokenizer.advance()
        # statements
        self.compileStatements()
        # symbol }
        self._tokenizer.advance()

        if self._tokenizer.current_token == "else":
            _label_end = self._get_label()
            self._vm_writer.writeGoto(_label_end)
            
            self._vm_writer.writeLabel(_label_false)
            
            # keyword else
            self._tokenizer.advance()

            # symbol {
            self._tokenizer.advance()

            self.compileStatements()

            # symbol }
            self._tokenizer.advance()
            
            self._vm_writer.writeLabel(_label_end)
        else:
            # elseがない場合、正解にあるような連続ラベル構造（gotoとlabelのペア）を再現
            _label_end = self._get_label()
            self._vm_writer.writeGoto(_label_end)
            self._vm_writer.writeLabel(_label_false)
            self._vm_writer.writeLabel(_label_end)
            
    def compileWhile(self) -> None:
        # keyword while
        self._tokenizer.advance()

        # symbol (
        self._tokenizer.advance()

        # label L1
        _label1 = self._get_label()
        self._vm_writer.writeLabel(_label1)

        # expression
        self.compileExpression()

        # symbol )
        self._tokenizer.advance()

        # not
        self._vm_writer.writeArithmetic(COMMAND_TYPE.NOT)

        # if-goto L2
        _label2 = self._get_label()
        self._vm_writer.writeIf(_label2)

        # symbol {
        self._tokenizer.advance()

        # statements
        self.compileStatements()

        # symbol }
        self._tokenizer.advance() 

        # goto L1
        self._vm_writer.writeGoto(_label1)

        # label L2
        self._vm_writer.writeLabel(_label2)

    def compileDo(self) -> None:
        _expression_count = 0
        # keyword do
        self._tokenizer.advance()

        # subroutineCall: subroutineName | (className|varName)
        _sub_routine_name = self._tokenizer.current_token
        _kind, _index, _type = self._lookup_var(_sub_routine_name)
        self._tokenizer.advance()

        # if subroutineCall subroutineName(expressionList)
        if self._tokenizer.current_token == "(":
            # 自クラスのメソッドを直接呼ぶ場合（例: draw()）
            _callee_name = self._class_name
            _sub_method_name = _sub_routine_name
            self._vm_writer.writePush(SEGMENT_TYPE.POINTER, 0)
            _expression_count += 1

            # symbol (
            self._tokenizer.advance()
            # expressionList
            _expression_count += self.compileExpressionList()
            # symbol )
            self._tokenizer.advance()

        # if subroutineCall (className|varName).subroutineName(expressionList)
        elif self._tokenizer.current_token == ".":
            # symbol .
            self._tokenizer.advance()

            # identifier subroutineName
            _sub_method_name = self._tokenizer.current_token
            self._tokenizer.advance()

            if _kind is not None and _kind != KIND_TYPE.NONE:
                # 変数(オブジェクト)のメソッドなら、thisをstackに積む
                _segment = self._kind_to_segment(_kind)
                self._vm_writer.writePush(_segment, _index)
                _expression_count += 1
                _callee_name = _type
            else:
                # クラス名直接の場合（例: SquareGame.new など）
                _callee_name = _sub_routine_name

            # symbol (
            self._tokenizer.advance()

            # expressionList
            _expression_count += self.compileExpressionList()

            # symbol )
            self._tokenizer.advance()

        # symbol ;
        self._tokenizer.advance()

        _full_name = f"{_callee_name}.{_sub_method_name}"
        self._vm_writer.writeCall(_full_name, _expression_count)

        # doの場合、返り値（void）を破棄するためにスタック上の値をポップする
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
            # 文字列を取得する
            string_val = self._tokenizer.stringVal()

            length = len(string_val)
            self._vm_writer.writePush(SEGMENT_TYPE.CONSTANT, length)
            self._vm_writer.writeCall("String.new", 1)

            for c in string_val:
                # 文字のASCIIコードを取得
                char_code = ord(c)
                self._vm_writer.writePush(SEGMENT_TYPE.CONSTANT, char_code)
                self._vm_writer.writeCall("String.appendChar", 2)
                
            self._tokenizer.advance()
        elif self._tokenizer.tokenType() == TOKEN_TYPE.KEYWORD: # true, false, null
            _keyword = self._tokenizer.current_token
            if _keyword == "true":
                self._vm_writer.writePush(SEGMENT_TYPE.CONSTANT, 1)
                self._vm_writer.writeArithmetic(COMMAND_TYPE.NEG) # -1 にする
            elif _keyword in ["false", "null"]:
                self._vm_writer.writePush(SEGMENT_TYPE.CONSTANT, 0)
            elif _keyword == "this":
                self._vm_writer.writePush(SEGMENT_TYPE.POINTER, 0)
            self._tokenizer.advance()
        elif self._tokenizer.tokenType() == TOKEN_TYPE.IDENTIFIER: # varName|varName[expression]|subroutineCall
            _name = self._tokenizer.current_token
            self._tokenizer.advance()

            _kind, _index, _type = self._lookup_var(_name)

            if self._tokenizer.current_token == "[": # 配列参照
                # 配列のベースアドレスをpush
                _segment = self._kind_to_segment(_kind)
                self._vm_writer.writePush(_segment, _index)

                # symbol [
                self._tokenizer.advance()

                # expression
                self.compileExpression()

                # symbol ]
                self._tokenizer.advance()

                # 2. アドレスを計算してTHATに設定し、値を取り出す
                self._vm_writer.writeArithmetic(COMMAND_TYPE.ADD)
                self._vm_writer.writePop(SEGMENT_TYPE.POINTER, 1)
                self._vm_writer.writePush(SEGMENT_TYPE.THAT, 0)

            elif self._tokenizer.current_token == "(" or self._tokenizer.current_token == ".": # subroutine call
                _expression_count = 0
                _sub_method_name = ""
                
                # 次のトークンが "." なら (className または varName).methodName() の形
                if self._tokenizer.current_token == ".":
                    if _kind is not None and _kind != KIND_TYPE.NONE:
                        # 変数(オブジェクト)のメソッドなら, thisをstackに積む
                        _segment = self._kind_to_segment(_kind)
                        self._vm_writer.writePush(_segment, _index)
                        _expression_count += 1
                        _callee_name = _type # 変数の型（例: SquareGame）
                    else:
                        # クラス名直接の場合（例: Square.new など）
                        _callee_name = _name

                    # symbol .
                    self._tokenizer.advance()

                    # identifier subroutineName
                    _sub_method_name = self._tokenizer.current_token
                    self._tokenizer.advance()
                else:
                    # "(" が続く場合（現在のクラスのメソッドを直接呼ぶ場合、例: draw() など）
                    # 暗黙的に this を積む
                    _callee_name = self._class_name
                    _sub_method_name = _name
                    self._vm_writer.writePush(SEGMENT_TYPE.POINTER, 0)
                    _expression_count += 1

                # symbol (
                self._tokenizer.advance()

                # expressionList
                _expression_count += self.compileExpressionList()

                # symbol )
                self._tokenizer.advance()

                _full_name = f"{_callee_name}.{_sub_method_name}"
                self._vm_writer.writeCall(_full_name, _expression_count)

            else: # 単なる変数の参照
                if _kind is not None and _kind != KIND_TYPE.NONE:
                    _segment = self._kind_to_segment(_kind)
                    self._vm_writer.writePush(_segment, _index)

        elif self._tokenizer.current_token == "(":
            # symbol (
            self._tokenizer.advance()

            # expression
            self.compileExpression()

            # symbol )
            self._tokenizer.advance()

        elif (unaryOp := self._tokenizer.current_token) in ["-", "~"]:
            # symbol unaryOp 
            self._tokenizer.advance()

            # term
            self.compileTerm()

            if unaryOp == "-":
                self._vm_writer.writeArithmetic(COMMAND_TYPE.NEG)
            else: # unaryOp == "~"
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