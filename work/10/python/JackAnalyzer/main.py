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
        self._jack_file = jack_file
        self._tokens = []
        self._current_idx = -1
        self._current_token = ""

        with open(self._jack_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        lines = self._clean_lines(lines)
        print(lines)
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
        key_words = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void",
                     "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
        symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ".", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]

        tokens = []
        while(line):
            token = ""
            if match := re.match(r'"[^"]*"', line): # 文字列
                token = match.group()
            elif match := re.match(r'\d+', line): # 整数定数
                token = match.group()
            elif line[0] in symbols: # 先頭がシンボル
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
            self._current_token = self._tokens[self._current_idx]


def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.vm>")
        sys.exit(1)

    path = sys.argv[1]
    source_type = get_source_type(path)
    print(f"path = {path}")

    jack_files = []
    xml_file = ""
    if source_type == SOURCE_TYPE.FILE:
        jack_files.append(path)
        xml_file = path.rsplit(".", 1)[0] + ".xml"

    print(xml_file)
    jack_tokenizer = JackTokenizer(jack_files[0])

if __name__ == "__main__":
    main()