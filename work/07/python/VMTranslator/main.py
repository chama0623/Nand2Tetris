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

def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.vm>")
        sys.exit(1)

    vm_file = sys.argv[1]
    parser = Parser(vm_file)
    print(f"Translating {vm_file}...")
    while parser.hasMoreLines():
        parser.advance()
        print(parser.commandType(), parser.arg1(), parser.arg2())


if __name__ == "__main__":
    main()