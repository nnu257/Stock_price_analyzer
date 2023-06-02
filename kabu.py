import subprocess
import tkinter as tk
import threading
import datetime as dt
import jpholiday


def isBizDay(DATE: str):
    # 営業日かを判定する関数
    Date = dt.date(int(DATE[0:4]), int(DATE[4:6]), int(DATE[6:8]))
    if Date.weekday() >= 5 or jpholiday.is_holiday(Date):
        return 0
    else:
        return 1


def set_state(event):
    # 押されたボタンの名前を入れて、ルートを停止、あとでdestoroyかける
    global state
    state = event.widget["text"]
    root.quit()


def dest(event):
    # 単純に停止するだけ
    root.quit()


# 営業時間内か判断するための変数
now = dt.datetime.now().strftime("%H%M")
today = dt.date.today().strftime("%Y%m%d")
first = "0900"
last = "1500"

# 証券取引所営業時刻中は実行させない
if (first < now and now < last) and isBizDay(today) == 1:
    # モニターのサイズを取得、ルートはその半分
    root = tk.Tk()
    root.title("kabu.app")
    root_width = round(root.winfo_screenwidth()/3)
    root_height = round(root.winfo_screenheight()/4)
    location = f"{root_width}x{root_height}+{round(root_width)}+{round(root_height)}"
    root.geometry(location)

    # ラベル
    chars = "\n証券取引所が営業中です。\n実行は、営業時間外に行ってください。"
    label = tk.Label(text=chars, font=("MSゴシック", "25"))
    label.pack()

    # ボタンの設定
    button_ok = tk.Button(root, text="終了", font=(
        "MSゴシック", "40"), width=5, height=2)

    # ボタンの場所の設定
    button_ok.place(x=round((root_width/2.85)), y=round((root_height/2.1)))

    # 押された時にstateを設定
    button_ok.bind("<1>", dest)
    button_ok.bind("<Return>", dest)

    # 1画面目を表示する
    root.mainloop()
    # quitで抜けたら、次の画面のためにdestroyしておく
    root.destroy()

# 営業時間外なら実行する
else:
    # まずメモ帳を開き、更新させる
    codes_set = "files/codes/codes_set.txt"
    app = "/Applications/テキストエディット.app/"
    subprocess.run(f"open -a textEdit {codes_set}", shell=True)

    # モニターのサイズを取得、ルートはその半分
    root = tk.Tk()
    root.title("kabu.app")
    root_width = round(root.winfo_screenwidth()/2)
    root_height = round(root.winfo_screenheight()/2.5)
    location = f"{root_width}x{root_height}+{round(root_width/2)}+{round(root_height/3.25)}"
    root.geometry(location)

    # ラベル
    chars = "\ncodes_set.txtを更新・保存後、OKをクリックして下さい。\n中止する場合はExitをクリックしてください。"
    label = tk.Label(text=chars, font=("MSゴシック", "25"))
    label.pack()

    # ボタンの設定
    button_ok = tk.Button(root, text="OK", font=(
        "MSゴシック", "40"), width=5, height=2)
    button_ex = tk.Button(root, text="Exit", font=(
        "MSゴシック", "40"), width=5, height=2)

    # ボタンの場所の設定
    button_ok.place(x=round((root_width/3.8)), y=round((root_height/3)))
    button_ex.place(x=round((2*root_width/3.8)), y=round((root_height/3)))

    # 押された時にstateを設定
    button_ok.bind("<1>", set_state)
    button_ex.bind("<1>", set_state)
    button_ok.bind("<Return>", set_state)
    button_ex.bind("<Return>", set_state)

    # 1画面目を表示する
    root.mainloop()
    # quitで抜けたら、次の画面のためにdestroyしておく
    root.destroy()

    # 1画面面の表示が終了し、2画面目が開始するまでに、メモ帳を終了する。
    pid = subprocess.run(
        "ps -A | grep -m1 TextEdit | awk '{print $1}'", shell=True, stdout=subprocess.PIPE, check=True).stdout
    pid = pid.decode("utf-8").strip()
    subprocess.run(f"kill {pid}", shell=True)

    def threading_run(root):
        # OKが押された時、マルチスレッドで行う処理
        subprocess.run("python3 kabu_set.py", cwd="files", shell=True)
        print("kabu_set:終了")
        subprocess.run("python3 kabu_valid.py", cwd="files", shell=True)
        print("kabu_valid:終了")
        subprocess.run("python3 kabu_zip.py", cwd="files", shell=True)
        print("kabu_zip:終了")
        subprocess.run("python3 kabu_analyze.py", cwd="files", shell=True)
        print("kabu_analyze:終了")
        root.quit()

    def update_timer(now_time):
        # timerのupdate用関数
        timer["text"] = "予想残り時間:" + str(now_time) + "秒+valid*5秒"
        if now_time > 0:
            # afterに渡す引数に関して、関数の引数は、afterの第三引数として渡す必要がある。
            # threadingと一緒。
            root.after(1000, update_timer, now_time-1)

    # 押されたボタンに合わせて分岐
    if state == "OK":
        root = tk.Tk()
        root.title("kabu.app")
        root.geometry(location)

        chars1 = "\n実行中です。\n処理終了後、この画面は非表示となり、\n分析結果が表示されます。\n"
        label1 = tk.Label(text=chars1, font=("MSゴシック", "30"))
        label1.pack()

        stocks = len(open(codes_set, "r").readlines())
        times = round(stocks * 5.4)
        timer = tk.Label(text="予想残り時間：" + str(times) +
                         "秒", font=('Helvetica', 40), bg="#c8c8c8")
        timer.pack()
        update_timer(times)

        # スレッドスタート
        t = threading.Thread(target=threading_run, args=(root,), daemon=True)
        t.start()

        # 表示スタート
        root.mainloop()
        root.destroy()

        # 分析結果の出力画面
        root = tk.Tk()
        root_width = round(root.winfo_screenwidth())
        root_height = round(root.winfo_screenheight())
        location = f"{root_width}x{root_height}"
        root.title("kabu.app")
        root.geometry(location)

        chars = "分析結果は以下の通りです。終了ボタンでアプリを終了します。\n"
        label = tk.Label(text=chars, font=("MSゴシック", "30"))
        label.place(x=round(root_width/8), y=round(1.5*root_height/32))

        button_ok = tk.Button(root, text="終了", font=(
            "MSゴシック", "40"), width=5, height=2)
        button_ok.place(x=round(3*root_width/4), y=10)

        button_ok.bind("<1>", dest)
        button_ok.bind("<Return>", dest)

        # キャンバス作成
        canvas = tk.Canvas(root, bg="#ffffff", height=round(
            3*root_height/4)-60, width=root_width-45, borderwidth=10)
        # キャンバス表示
        canvas.place(x=13, y=round(4*root_height/32)+5)

        # イメージ作成
        img1 = tk.PhotoImage(file="files/graph/analyze_result1.png",
                             width=1200, height=8000)
        img2 = tk.PhotoImage(file="files/graph/analyze_result2.png",
                             width=1200, height=800)

        # キャンバスにイメージを表示
        canvas.create_image(5, 10, image=img1, anchor=tk.NW)
        canvas.create_image(710, 10, image=img2, anchor=tk.NW)

        # 表示スタート
        root.mainloop()
        root.destroy()

    elif state == "Exit":
        root = tk.Tk()
        root.title("kabu.app")
        location = location = f"{round(root_width/2.5)}x{round(root_height/2)}+{round(root_width/1.2)}+{round(root_height/1.5)}"
        root.geometry(location)
        label = tk.Label(text="終了しました", font=("MSゴシック", "25"))
        label.place(x=round(root_width/11), y=round(root_height/19))
        button_ok = tk.Button(root, text="OK", font=(
            "MSゴシック", "40"), width=5, height=2)
        button_ok.place(x=round((root_width/9)), y=round((root_height/5.5)))
        button_ok.bind("<1>", dest)
        button_ok.bind("<Return>", dest)
        root.mainloop()
        root.destroy()
