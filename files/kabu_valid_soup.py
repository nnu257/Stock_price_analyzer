from bs4 import BeautifulSoup
import os
import datetime as dt

# あえて、requestが吐き出したsource_valid内のファイルから
# スクレイピングし、それに上書き(コードのみのファイル名で書き込み、元は削除)をする。
# その後、それをもう一度読み込んで、1,3,5営業日のものだけをoutputに出力する。
# これは、1,3,5営業日以外のデータを見たい時・プログラム変更したい時に対応するためのものである。

# メイン表の日時を取り出すパターン
pattern_mr = r">(.+?)</time>"

# sourceディレクトリにある全てのファイルを開く
for filename in os.listdir("source_valid"):

    # ファイルを読み込み、soupオブジェクトを作成
    with open("source_valid/" + filename, "r") as f:
        soup = BeautifulSoup(f, "lxml")

        # メイン表のheader
        main_table_header = soup.select(
            "#stock_kabuka_table > table.stock_kabuka_dwm > thead")[0]

        # headerの中身をelementsに格納
        main_table_header_elements = [
            element.string.strip() for element in main_table_header.find_all("th")]

        # 当日情報の表
        today_table_body = soup.select(
            "#stock_kabuka_table > table.stock_kabuka0 > tbody")[0]

        # 当日情報から要素を取り出す
        date = [today_table_body.find("time").string]
        values = [value.string.replace(",", "")
                  for value in today_table_body.find_all("td")[0:4]]
        change = [x.string.replace(",", "")
                  for x in today_table_body.select("td > span")]
        if len(change) == 0:
            change = ["0", "0.0"]
        volume = [today_table_body.find_all("td")[6].string.replace(",", "")]

        today_record = date + values + change + volume

        # メイン表
        main_table_body = soup.select(
            "#stock_kabuka_table > table.stock_kabuka_dwm > tbody")[0]

        # メイン表の行
        main_table_records = main_table_body.find_all("tr")

        # メイン表の各行から、要素を取り出す
        main_table_recors_value = []
        for record in main_table_records:

            date = [record.select("th > time")[0].string.replace(",", "")]
            values = [value.string.replace(",", "")
                      for value in record.find_all("td")[0:4]]
            change = [x.string.replace(",", "")
                      for x in record.select("td > span")]
            if len(change) == 0:
                change = ["0", "0.0"]
            volume = [record.find_all("td")[6].string.replace(",", "")]

            value_record = date + values + change + volume
            main_table_recors_value.append(value_record)

        # メイン表すべて
        main_table = [main_table_header_elements] + \
            [today_record] + main_table_recors_value

    # ファイル名は後でコードから開きたいので、銘柄コードのみの名前で書き込み
    with open("source_valid/" + filename.split("_")[0], "w") as f:
        for record in main_table:
            f.writelines(",".join(record) + "\n")

    # 読み取りに使ったファイルは削除
    os.remove("source_valid/" + filename)


# ここから、再度ファイルを開き、1,3,5営業日のものだけをoutputに出力する。


def get_unique_list(seq):
    # uniqueなリストを返す関数
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]


# codesのリスト
codes = []
# 1,3,5営業日のリスト
bizs_135 = []
# 何世紀-1
century_minus1 = "20"

with open("codes/codes_valid.txt", "r") as f:
    for line in f:
        codes.append(line.split(",")[0])
        bizs_135.append(line.strip().split(",")[1:4])

# set日時のuniqueな数に応じて、codesに0000を追加し、1,3,5営業日のリストをbizs_135に追加する
for list in get_unique_list(bizs_135):
    codes.append("0000")
    bizs_135.append(list)


# output_validの方に出力するレコードのリスト
output_records = []

for i, code in enumerate(codes):

    # output_validに出力するレコード=1,3,5営業日の日付と終値
    output_record = []

    # codes内のコードがファイル名になっているものを開く
    with open("source_valid/" + code) as f:
        for line in f:
            line = line.strip().split(",")

            # 時系列データのうち、1,3,5営業日に該当する時の日付と終値
            if century_minus1 + line[0] in bizs_135[i]:
                # reverseで二次元目も逆になるみたいなので、逆で入れる
                output_record += [line[4], line[0]]

        # 日時が逆順になっているので、逆ソートしてcodeを最初につけてからからappend
        output_record.reverse()
        output_record = [code] + output_record
        output_records.append(output_record)

# output_recordsを並び替えて、日経平均がそれぞれの日付ごとの最後にくるようにする
output_records.sort(key=lambda x: x[1])

# 最後にラベルを追加
output_records = [["銘柄", "1営業日日付", "1営業日株価",
                  "3営業日日付", "3営業日株価", "5営業日日付", "5営業日株価"]] + output_records

# kabu_set_soup.py参照
td = dt.timedelta(hours=15)
date = (dt.datetime.now() - td).strftime('%Y-%m-%d')


# もしファイルが存在しなければ、書き込む。
# これは、5日経ったcodesを一回のみ処理するために、実行時に削除しているため、
# 2回kabu.pyを実行した時にcodesが削除されたもので実行され、
# validcodesなしの状態でsoupしたものが上書きしないようにするためのものである。
filename_output = "output/output_valid_" + date + ".csv"
if os.path.isfile(filename_output) == False:
    with open(filename_output, "w") as f:
        for record in output_records:
            f.writelines(",".join(record) + "\n")
