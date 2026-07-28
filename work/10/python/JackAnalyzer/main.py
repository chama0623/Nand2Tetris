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
        while(line):
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
            return self.current_token
        else:
            return None

class CompilationEngine:
    def __init__(self, jack_file:str, xml_file:str):
        self._xml_file = open(xml_file, "w", encoding="utf-8")
        self._tokenizer = JackTokenizer(jack_file)

    def _write_xml(self, tag:str, value:str) -> str:
        self._xml_file.write(f"<{tag}>{value}</{tag}>\n") 

    def close(self) -> None:
        self._xml_file.close()

    def compileClass(self) -> None:
        if not self._tokenizer.hasMoreTokens():
            return 

        # <class>
        self._tokenizer.advance()
        self._xml_file.write("<class>\n")

        # <keyword>class</keyword>
        self._write_xml("keyword", self._tokenizer.current_token)

        # <identifier>className</identifier>
        self._tokenizer.advance()
        self._write_xml("identifier", self._tokenizer.current_token)

        # <symbol> } </symbol>
        self._tokenizer.advance()
        self._write_xml("symbol", self._tokenizer.current_token)

        # classVarDec
        self._tokenizer.advance()
        while(self._tokenizer.current_token in ["static", "field"]):
            self.compileClassVarDec()

        

        # <symbol> { </symbol>
        # このメソッドは上記jackファイルに対する処理が完成したときに正常に動作する
        self._tokenizer.advance()
        self._write_xml("symbol", self._tokenizer.current_token)

        # </class>
        self._xml_file.write("</class>\n")

    def compileClassVarDec(self) -> None:
        # <classVarDec>
        self._xml_file.write("<classVarDec>\n")

        # <keyword>static|field</keyword>
        self._write_xml("keyword", self._tokenizer.current_token)

        # <keyword>type</keyword>
        self._tokenizer.advance()
        self._write_xml("keyword", self._tokenizer.current_token)

        # <identifier>varName</identifier>
        self._tokenizer.advance()
        self._write_xml("identifier", self._tokenizer.current_token)

        self._tokenizer.advance()
        while(self._tokenizer.current_token != ";"):
            # <symbol>,</symbol>
            self._write_xml("symbol", self._tokenizer.current_token)

            # <identifier>varName</identifier>
            self._tokenizer.advance()
            self._write_xml("identifier", self._tokenizer.current_token)

            # <symbol>;</symbol>
            self._tokenizer.advance()
        
        self._write_xml("symbol", self._tokenizer.current_token)

        # </classVarDec>
        self._xml_file.write("</classVarDec>\n")
        self._tokenizer.advance()

        

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
            xml_file = jack_file.rsplit(".", 1)[0] + ".xml"
            print(f"Compiling: {jack_file} -> {xml_file}")

            engine = CompilationEngine(jack_file, xml_file)
            engine.compileClass()
            engine.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: JackAnalyzer <filename.jack>")
        sys.exit(1)

    path = sys.argv[1]

    jack_analyzer = JackAnalyzer(path)
    jack_analyzer.analyze()


if __name__ == "__main__":
    main()