import requests
import datetime as dt
import time
import os
import shutil

# まずsourceフォルダの中身を削除
shutil.rmtree("source_valid")
os.makedirs("source_valid")

# コード一覧
codes = []

# 株価をスクレイピングしたいコードの一覧
with open("codes/codes_valid.txt", "r") as f:
    for line in f:
        codes.append(line.split(",")[0])

    # 日経平均株価用のコード
    codes = codes + ["0000"]


# urlから銘柄コードを抜いたアドレス
url = "https://kabutan.jp/stock/kabuka?code="
# 待ち時間
delay = 2
# 現在日時
now = dt.datetime.now().strftime('%Y%m%d-%H%M%S')


def fetch(url):
    # クロール関数
    return requests.get(url)


# コードを結合したURLのレスポンスを取得
responses = []
for code in codes:
    code_url = url + code
    responses.append(fetch(code_url))
    time.sleep(delay)


# コードごとにテキストを保存
for i, response in enumerate(responses):

    # コードに存在しない銘柄・不適切な文字が入っていない時の処理
    if "該当する銘柄は見つかりませんでした" not in response.text:

        # ファイル名は、コード_現在の日時とする
        filename = "source_valid/" + codes[i] + "_" + now

        # 作成したfilenameでテキスト書き込み
        with open(filename, "w") as f:
            f.write(response.text)
            f.write("\n" + response.encoding)

    # 入っていた時の処理
    else:
        print(f"不適切なコードがクロールされていません。code:{codes[i]}")