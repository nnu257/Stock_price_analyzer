from bs4 import BeautifulSoup
import datetime as dt
import os
import re
import pandas as pd
import numpy as np
import biz_module as biz


# 銘柄名抜き出しのパターン
pattern_name = r"</span>(.*?)</h2>"
# PER, PBR抜き出しのパターン
pattern_pebr = r"<td>(.*?)<span"

# レコードを集めた表
records = [["登録日", "1営業日日付", "銘柄コード", "銘柄名",
            "株価", "MACD", "PER", "PBR", "権利落日"]]

# 登録日(15時以降/以前でファイルを管理するため、utc-15)
td = dt.timedelta(hours=15)
date = (dt.datetime.now() - td).strftime('%Y-%m-%d')
date_1_biz = biz.biz_list(dt.datetime.strptime(date, '%Y-%m-%d'), [1])[0]

# sourceディレクトリにある全てのファイルを開く
# ただし、日経平均株価は後で処理するので除く
for filename in [x for x in set(os.listdir("source_set")) if "0000_" not in x]:

    # ファイルを読み込み、soupオブジェクトを作成
    with open("source_set/" + filename, "r") as f1:
        soup1 = BeautifulSoup(f1, "lxml")

        # 一行のレコード
        record = [0]*9

        # 登録日
        record[0] = date

        # 1営業日日付
        record[1] = date_1_biz

        # 銘柄名とかの表
        info_tables_main = soup1.select("#stockinfo_i0")[0].find_all("div")

        # 銘柄コード(あえてここから抽出)
        record[2] = info_tables_main[1].select("div > h2 > span")[0].string

        # 銘柄名
        record[3] = re.search(pattern_name, str(
            info_tables_main[1].select("div > h2")[0])).group(1)

        # 株価
        record[4] = info_tables_main[2].find_all(
            "span")[1].string.replace("円", "").replace(",", "")

        # MACD : まず、kabu_valid_soupの一部を改変して、過去の株価を取得する。
        main_table_body = soup1.select(
            "#stock_kabuka_table > table.stock_kabuka_dwm > tbody")[0]

        # メイン表の行
        main_table_records = main_table_body.find_all("tr")

        # 始値、高値、安値、終値の一覧
        values = []
        for i in range(4):
            values.append([record.find_all("td")[i].string.replace(",", "")
                           for record in main_table_records])

        values = np.mean(np.array(values, dtype=np.float64), axis=0)[::-1]

        # 短期EMA(12週)
        semas = pd.Series(values).ewm(span=12, adjust=False).mean()
        sema = semas[len(semas)-1]

        # 長期EMA(26週)
        lemas = pd.Series(values).ewm(span=26, adjust=False).mean()
        lema = lemas[len(lemas)-1]

        # macd
        record[5] = str(round((sema - lema), 1))

        # PBRとかの表
        info_tables_funda = soup1.select("#stockinfo_i3")[
            0].find_all("td")[0:2]

        # PER
        record[6] = re.search(pattern_pebr, str(info_tables_funda[0])).group(1)

        # PBR
        record[7] = re.search(pattern_pebr, str(info_tables_funda[1])).group(1)

        # 権利落日、_rightsフォルダからyahooファイナンスのデータを読み込み
        with open("source_set_rights/" + filename, "r") as f2:
            soup2 = BeautifulSoup(f2, "lxml")

        # 株主優待があれば要素が1となるリスと
        incentive = soup2.select(
            "#root > main > div:nth-child(2) > div > div.XuqDlHPN > div:nth-child(3) > section._1naUMvAn > div > table > tbody > tr:nth-child(1) > td")

        # 株主優待を実施していれば権利落日、していなければ"なし"とする
        if incentive:
            rights = incentive[0].string
        else:
            rights = "なし"

        record[8] = rights

        # 一行を表に追加
        records.append(record)

# 日経平均株価のみのファイルを読み込み、soupオブジェクトを作成
filename_0000 = [x for x in os.listdir("source_set") if "0000_" in x]
if filename_0000:
    with open("source_set/" + filename_0000[0], "r") as f1:
        soup1 = BeautifulSoup(f1, "lxml")

        # 銘柄名の表
        info_tables_main = soup1.select("#stockinfo_i0")[0].find_all("div")

        # 日経平均株価
        stock_price = info_tables_main[2].find_all(
            "span")[1].string.replace("円", "").replace(",", "")

        # 一行を表に追加
        records.append([date, date_1_biz, "0000", "日経平均株価",
                        stock_price, "0", "0", "0", "なし"])


# 一つのファイルにまとめて記述、日にちが異なれば別ファイル、一緒なら複数回実行なので上書き
with open("output/output_set_" + date + ".csv", "w") as f:

    # 銘柄ごとの情報書き込み(header込み)
    for record in records:
        f.writelines(",".join(record) + "\n")
