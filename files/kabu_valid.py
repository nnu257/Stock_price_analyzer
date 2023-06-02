import subprocess
import os
import datetime as dt
import biz_module as biz


# codes_saveの中にファイル名(日付)の中で、５営業日以上立っている日付のリスト
spent_dates = []

# 今日
td = dt.timedelta(hours=15)
today = (dt.datetime.now() - td).date()


for date in os.listdir("codes_save"):

    # dateを日付に変換
    date = dt.datetime.strptime(date, "%Y-%m-%d").date()

    # その中から、5営業日以上立っているものを選択
    if biz.day_n_far_biz(date, today, 5) == 1:
        spent_dates.append(date)

# 5営業日以上が過ぎたコードのリスト
spent_codes = []

# コードをspent_codesに追加していく
for date in spent_dates:
    with open("codes_save/" + date.strftime("%Y-%m-%d"), "r") as f:
        for line in f:
            bizs135 = biz.biz_list(date, [1, 3, 5])
            record = [line.strip()] + bizs135
            spent_codes.append(",".join(record))


# codes_validに5営業日以上過ぎた、検証対象のコードを渡す
with open("codes/codes_valid.txt", "w") as f:
    for spent_code in spent_codes:
        f.write(spent_code + "\n")


# 渡したコードは、再度検証されないよう削除する
for date in spent_dates:
    os.remove("codes_save/" + date.strftime("%Y-%m-%d"))

subprocess.run("python3 kabu_valid_requests.py", shell=True)
subprocess.run("python3 kabu_valid_soup.py", shell=True)
