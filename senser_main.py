# coding: UTF-8
from flask import (
    Flask, render_template) #webに接続する
import sqlite3 #データベース
import insert_temp #温度をデータベースに保存する
import threading #スレッド
import schedule #定期実行


#毎時0分に実行させる関数を登録
schedule.every().hour.at(":00").do(insert_temp.insert_temp)

#scheduleをループする関数
def th1_job():
    while True:
        #scheduleがループして設定時刻ににinsert_tempを実行
        schedule.run_pending()

#温度センサから得られる値を毎時00分にテーブルに保存していくスレッド
th1 = threading.Thread(target=th1_job)
#スレッドを実行
th1.start()


#Flaskオブジェクトの生成
app = Flask(__name__)


#「/」、「/update」へアクセスがあった場合"senser_web.html"を返す関数
@app.route('/update', methods=['GET'])
@app.route('/', methods=['GET'])
def temp_web():

    #データベースに接続
    conn = sqlite3.connect("Sample.sqlite3")
    #カーソル生成
    c = conn.cursor()
    
    
    #idで降順に並び替えて最新の温度（小数点第一位以上）だけ取り出す
    c.execute("SELECT SUBSTR(temp, 1, 4) FROM temp_table ORDER BY id DESC")
    #render_templateでhtmlに渡す変数に温度の文字列を入れる
    temp_now = c.fetchone()
    #値がNoneのときは文字列「データ取得待ち」を変数に渡す
    if temp_now is None:
        temp_now = 'データ取得待ち'
    else:
        #タプルから文字列に変換
        temp_now = str(temp_now[0])
        #温度に℃をつける
        temp_now = temp_now+"℃"
    
    #idで降順に並び替えて最新の日時だけ取り出す
    c.execute("SELECT SUBSTR(timestamp,1, 11) FROM temp_table ORDER BY id DESC")
    data = c.fetchone()
    if data is None:
        data_now = 'データ取得待ち'
    else:
        data_now = data[0]

    #グラフの表示に使うtempのタプルを渡す
    c.execute('SELECT temp FROM temp_table')
    temp_forjs = c.fetchall()

    #グラフの表示に使うtimestampのタプルを渡す
    c.execute('SELECT timestamp FROM temp_table')
    timestamp_forjs = c.fetchall()

    #htmlに変数を渡す
    return render_template('senser_web.html', title='temperatur', temp_now=temp_now, data=data_now, temp_forjs=temp_forjs, timestamp_forjs=timestamp_forjs)
    
    #データベース接続を閉じる
    conn.close()


if __name__ == "__main__":
    #ローカルで接続する
    app.run(debug=True, host='127.0.0.1', port=80)