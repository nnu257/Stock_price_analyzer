import requests
import datetime as dt
import time
import os
import shutil


# まずsourceフォルダの中身を削除
shutil.rmtree("source_set")
os.makedirs("source_set")
shutil.rmtree("source_set_rights")
os.makedirs("source_set_rights")

# 株価をスクレイピングしたいコードの一覧
# codes_after.txtには、スクレイピングしたいコードを一コード一行で記述する
with open("codes/codes_set.txt", "r") as f:
    codes = f.read().splitlines()
    # コードの書いていない行は削除
    codes = [code for code in codes if code]

# 日経平均株価入りのcodes
codes_0000 = codes + ["0000"]

# カブタンurlから銘柄コードを抜いたアドレス
url_kabutan = "https://kabutan.jp/stock/kabuka?code="
# 権利落用、yahooファイナンスから銘柄コード.Tとincentiveを抜いたアドレス
url_rights = "https://finance.yahoo.co.jp/quote/"
# 待ち時間
delay = 2
# 現在日付
now = dt.datetime.now().strftime('%Y%m%d-%H%M%S')


def fetch(url):
    # クロール関数
    return requests.get(url)


# コードを結合したURLのレスポンスを取得
# 0000以外にもコードが存在した時のみ
responses_kabutan = []
if len(codes_0000) >= 2:
    for code in codes_0000:
        code_url = url_kabutan + code
        responses_kabutan.append(fetch(code_url))
        time.sleep(delay)

responses_yahoo = []
for code in codes:
    code_url = url_rights + code + ".T/incentive"
    responses_yahoo.append(fetch(code_url))
    time.sleep(delay)


# コードごとにテキストを保存
for i, response in enumerate(responses_kabutan):

    # コードに存在しない銘柄・不適切な文字が入っていない時の処理
    if "該当する銘柄は見つかりませんでした" not in response.text:

        # ファイル名は、コード_現在の日時とする
        filename = "source_set/" + codes_0000[i] + "_" + now

        # 作成したfilenameでテキスト書き込み
        with open(filename, "w") as f:
            f.write(response.text)
            f.write("\n" + response.encoding)

    # 入っていた時の処理
    else:
        print(f"不適切なコードがクロールされていません。code:{codes[i]}")


# コードごとにテキストを保存
for i, response in enumerate(responses_yahoo):

    # コードに存在しない銘柄・不適切な文字が入っていない時の処理
    if "指定されたページまたは銘柄は存在しません。" not in response.text:

        # ファイル名は、コード_現在の日時とする
        filename = "source_set_rights/" + codes[i] + "_" + now

        # 作成したfilenameでテキスト書き込み
        with open(filename, "w") as f:
            f.write(response.text)
            f.write("\n" + response.encoding)


# 当日の日にち(15時切り替え、soup.py参照)
td = dt.timedelta(hours=15)
date = (dt.datetime.now() - td).strftime('%Y-%m-%d')

# ファイル名をdateに変更した上で、codes_set.txtをcodes_saveにコピー
shutil.copy('codes/codes_set.txt', 'codes_save/' + date)
