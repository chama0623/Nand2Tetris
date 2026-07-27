import os, sys
from enum import Enum

class SOURCE_TYPE(Enum):
    FILE = 0
    DIR = 1

def get_source_type(path:str) -> SOURCE_TYPE:
    """pathがファイル(.jack)であるときSOURCE_TYPE.FILE, ディレクトリであるときSOURCE_TYPE.DIRを返す
    """
    if os.path.isfile(path):
        return SOURCE_TYPE.FILE
    elif os.path.isdir(path):
        return SOURCE_TYPE.DIR
    raise ValueError(f"Invalid path: {path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: hackassembler <filename.vm>")
        sys.exit(1)

    path = sys.argv[1]
    source_type = get_source_type(path)
    print(f"path = {path}")

    jack_files = []
    vm_file = ""
    if source_type == SOURCE_TYPE.FILE:
        jack_files.append(path)
        vm_file = path.rsplit(".", 1)[0] + ".vm"


if __name__ == "__main__":
    main()