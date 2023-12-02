# 実行方法

サンプルコードの実行方法は以下の通りです。
fastapi と uvicorn のパッケージがインストールされていれば動作しますので、venv 以外の方法でも問題ありません。

```bash
# venv作成
$ python -m venv .venv

# venv有効化
$ . .venv/bin/activate

# packageインストール
$ pip install fastapi uvicorn

# uvicornでfastapiを実行
$ python -m uvicorn main:app --port 8080 --reload

# main2.pyを実行する場合
$ python -m uvicorn main2:app --port 8080 --reload
```

上記でuvicorn起動後、以下にアクセスするとswagger画面が開きます。
http://localhost:8080/docs