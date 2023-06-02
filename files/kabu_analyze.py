import pprint
import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib
import statistics


def calculate_percent(line: str):
    # lineをstrでもらい、1,3,5営業日後の株価の変化量%のリストを返す関数
    line = line.strip().split(",")
    percent = [0, 0, 0]
    percent[0] = round((float(line[10]) - float(line[4])) /
                       float(line[4]) * 100, 2)
    percent[1] = round((float(line[12]) - float(line[4])) /
                       float(line[4]) * 100, 2)
    percent[2] = round((float(line[14]) - float(line[4])) /
                       float(line[4]) * 100, 2)

    return percent


# データを入れるリスト
kabu_datas = []
# グループごとの日付とデータ数nを入れるリスト
kabu_dates_n = []

with open("output/outputs.csv", "r") as f:
    # groups, 日時ごとの行数を読み取り
    groups = [int(x) for x in f.readline().strip().split(",")]

    # ラベル行は飛ばす
    f.readline()

    # 残りを読む
    lines = f.read().splitlines()

# 配列を指定した個数で分割していくループ処理
n = 0
for i in groups:
    kabu_datas.append(lines[n:n+i])
    kabu_dates_n.append(f"{lines[n][5:10]}\nn={i}")
    n += i

# グループごとの成績のリスト
percents_select = []

# グループごとに平均成績を計算
for i, x in enumerate(groups):
    percent_avg = [0, 0, 0]
    for j in range(x-1):
        ret = calculate_percent(kabu_datas[i][j])
        percent_avg[0] += ret[0]
        percent_avg[1] += ret[1]
        percent_avg[2] += ret[2]

    percent_avg[0] = round(percent_avg[0] / x-1, 3)
    percent_avg[1] = round(percent_avg[1] / x-1, 3)
    percent_avg[2] = round(percent_avg[2] / x-1, 3)

    percents_select.append(percent_avg)

'''
# グループごとの中央値の成績リスト
percents_select_cent = []

# グループごとに中央値で成績を計算
for i, x in enumerate(groups):
    percent = []
    for j in range(x-1):
        percent.append(calculate_percent(kabu_datas[i][j]))

    # 中央値にしたいため、転置
    percent_t = [list(x) for x in zip(*percent)]
    for j in range(len(percent_t)):
        percent_t[j] = statistics.median(percent_t[j])

    percents_select_cent.append(percent_t)

    # 転置を戻す
    percents_select_cent = [list(x) for x in zip(*percents_select_cent)]
'''

# 日経平均株価の成績リスト
percents_nikkei = []

# 日経平均株価から成績を確認
for group in kabu_datas:
    percents_nikkei.append(calculate_percent(group[-1]))

# 二つのリストの差を計算
percents_sub = list(np.array(percents_select) - np.array(percents_nikkei))

# selectのみの増減率をプロット(set日別)
# 凡例が多く、日経平均があるとそれとの区別がつかなくなるため、日経平均は省略
xlabels = ["1営業日後", "3営業日後", "5営業日後"]
plt.figure(figsize=(7, 6))
for x in percents_select:
    plt.plot(xlabels, x)
plt.title("set日別の株価増減率平均(selectのみ描画)")
plt.xlabel("営業日(後)")
plt.ylabel("増減率(%)")
plt.grid()
plt.savefig("graph/analyze_result1.png")

# selectと日経平均の増減率の差をプロット(set日別)
plt.figure(figsize=(7, 6))
for x in percents_sub:
    plt.plot(xlabels, x)
plt.title("set日別の株価増減率平均(日経225アウトパフォーム)")
plt.xlabel("営業日(後)")
plt.ylabel("増減率(%)")
plt.grid()
plt.savefig("graph/analyze_result2.png")

# グラフ用に、1,3,5営業日, 日時の順になるよう転置
percents_select = [list(x) for x in zip(*percents_select)]
percents_nikkei = [list(x) for x in zip(*percents_nikkei)]
percents_sub = [list(x) for x in zip(*percents_sub)]

# selectとnikkeiの増減率をプロット(営業日後別)
plt.figure(figsize=(7, 6))
for x in percents_select:
    plt.plot(kabu_dates_n, x)
for x in percents_nikkei:
    plt.plot(kabu_dates_n, x)
plt.title("営業日後別の株価増減率平均(select, 日経平均共に描画)")
plt.xlabel("日付(日)、データ数(日)")
plt.ylabel("増減率(%)")
plt.grid()
plt.legend(["1営業日_select", "3営業日_select", "5営業日_select",
            "1営業日_nikkei", "3営業日_nikkei", "5営業日_nikkei"])
plt.savefig("graph/analyze_result3.png")

# selectとnikkeiの増減率の差をプロット(営業日後別)
plt.figure(figsize=(7, 6))
for x in percents_sub:
    plt.plot(kabu_dates_n, x)
plt.title("営業日後別の株価増減率平均(日経225アウトパフォーム)")
plt.xlabel("日付(日), データ数(日)")
plt.ylabel("増減率(%)")
plt.grid()
plt.legend(["1営業日", "3営業日", "5営業日"])
plt.savefig("graph/analyze_result4.png")

# 5日後の平均を計算して、ヒストグラムにする。
plt.figure(figsize=(7, 6))
#plt.hist(percents_select[0], alpha=0.5)
#plt.hist(percents_select[1], alpha=0.5)
plt.hist(percents_select[2], alpha=1.0, bins=len(percents_select[2]))
plt.title("set日別の株価増減率平均(selectのみ描画)")
plt.xlabel("増減率(%)")
plt.ylabel("件数(件)")
plt.grid()
plt.savefig("graph/analyze_result5.png")
