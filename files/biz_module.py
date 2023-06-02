import datetime as dt
import jpholiday


def isBizDay(DATE: str):
    # 営業日かを判定する関数
    Date = dt.date(int(DATE[0:4]), int(DATE[4:6]), int(DATE[6:8]))
    if Date.weekday() >= 5 or jpholiday.is_holiday(Date):
        return 0
    else:
        return 1


def day_n_far_biz(date1: dt, today: dt, n: int):
    # 二つの日付に対して、n営業日以上離れているか確認する関数

    # 離れている日にちを計算して返す
    count = 0
    # n営業日になるまで計算
    while count < n:

        count += 1
        date1 += dt.timedelta(days=1)
        while isBizDay(date1.strftime("%Y%m%d")) == 0:
            date1 += dt.timedelta(days=1)

        # その途中でtodayを追い越したらアウト
        if date1 > today:
            return 0
    return 1


def biz_list(date: dt, days: list):
    # dateから見て、[days]営業日の日時をstrのリストで渡す関数

    # 営業日のリスト
    bizs = []

    # daysの中で一番大きい数字を見つける
    most_elapsed = max(days)

    # daysの最終営業日進める。
    for i in range(most_elapsed):
        date += dt.timedelta(days=1)
        while isBizDay(date.strftime("%Y%m%d")) == 0:
            date += dt.timedelta(days=1)

        # [days]の時、bizsに日付を追加する。
        if i+1 in days:
            bizs.append(date.strftime("%Y/%m/%d"))

    return bizs


def biz_list_before(date: dt, days: list):
    # dateから見て、[days]営業日前の日時をstrのリストで渡す関数

    # 営業日のリスト
    bizs = []

    # 一番前の日
    most_before = min(days)

    # daysの最終営業日進める。
    for i in range(abs(most_before)):
        date -= dt.timedelta(days=1)
        while isBizDay(date.strftime("%Y%m%d")) == 0:
            date -= dt.timedelta(days=1)

        # [days]の時、bizsに日付を追加する。
        if -1*(i+1) in days:
            bizs.append(date.strftime("%Y/%m/%d"))

    return bizs
