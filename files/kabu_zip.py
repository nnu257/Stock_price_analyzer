import datetime as dt
import os
import biz_module as biz
import re


# 方針として、データを全て残しておきたいので、データの削除は行わないこととする。
# このプログラムの実行に時間が多大にかかるようになれば、削除して追記していくよう変更する。
# 2022-05-31現在 0.081s


# 今日の日付
td = dt.timedelta(hours=15)
date = (dt.datetime.now() - td).date()

# ５営業日前の日付
before5_date = biz.biz_list_before(date, [-5])[0]

# output内のファイルのリスト
files = os.listdir("output")
# 日付順になるよう、この時点でソートしておく
files.sort()

# set用日付抽出用パターン
pattern_set = r"output_set_(.+).csv"
# setファイルのリスト(日時strのみ)
set_files = [re.match(pattern_set, x).group(1) for x in files if "set" in x]
# setファイルリスト(5営業日前以前)
set_files_before = [
    x for x in set_files if dt.datetime.strptime(x, "%Y-%m-%d") <= dt.datetime.strptime(before5_date, "%Y/%m/%d")]

# valid用日付抽出パターン
pattern_valid = r"output_valid_(.+).csv"
# setファイルのリスト
valid_files = [x for x in files if "valid" in x]

# kabu_analyze用に、日付のグループがそれぞれ何行あるか記録する
groups = []

# setファイルのレコードを全て読む
records_set = ["登録日,1営業日日付,銘柄コード,銘柄名,株価,MACD,PER,PBR,権利落日"]
for date in set_files_before:
    with open("output/output_set_" + date + ".csv", "r") as f:
        records = f.read().splitlines()[1:]
        records_set += records

        # 先頭行=ラベル行を除いた行数がgroupsの要素となる
        groups.append(str(len(records)))
        groups = [x for x in groups if x != "0"]

# validファイルのレコードを全て読む
records_valid = ["1営業日日付,1営業日株価,3営業日日付,3営業日株価,5営業日日付,5営業日株価"]
for file in valid_files:
    with open("output/" + file, "r") as f:
        records_valid += [record[5:] for record in f.read().splitlines()[1:]]

# 最初に、groupsを出力。
# 次にsetとvalidを結合、レコードを改行でjoinして出力
with open("output/outputs.csv", "w") as f:
    f.write(",".join(groups) + "\n")

    for i in range(len(records_set)):
        f.write(records_set[i] + "," + records_valid[i] + "\n")
