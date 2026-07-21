# Python Assemblerを使うときのセットアップ(Linux)
1. pipをインストールする
```bash
sudo apt update
sudo apt install python3-pip
```

2. Venvで仮想環境を作る
```bash
sudo apt install python3-venv

python3 -m venv .venv
source .venv/bin/activate
```

3. hackassemblerをインストール
```bash
pip install -e .
```

4. `hackassembler`を実行する
```bash
hackassembler <hoge.asm>
```

5. 仮想環境を終了する
```bash
deactivate
```