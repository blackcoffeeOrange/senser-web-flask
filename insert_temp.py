import sqlite3 #データベース

#センサーに接続する（公式ライブラリのインストールが必要）
import board
import busio
import adafruit_adt7410

from datetime import datetime #日時取得


#データベースに接続
conn = sqlite3.connect("Sample.sqlite3")
#カーソル生成
c = conn.cursor()
#テーブルの存在を確認してみて無ければ作成（カラム　id、日時、温度）
c.execute("CREATE TABLE IF NOT EXISTS temp_table (id INTEGER PRIMARY KEY AUTOINCREMENT, temp INTEGER, timestamp TEXT PRYMARYKEY UNIQUE)")
#テーブル情報保存
conn.commit()
#データベース接続を閉じる
conn.close()

#センサーに接続
i2c_bus = busio.I2C(board.SCL, board.SDA)
adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
adt.high_resolution = True


#センサーで取得した温度と日時をテーブルに保存する関数
def insert_temp():

    #日時の表記を日本語文字列に直して取得(TEXT型)
    timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    #センサーから温度取得(INTEGER型)
    temp = adt.temperature

    print(timestamp,"\n", temp)#取得した日時と温度を表示

    #取得した日時と温度のデータをテーブルに入れるためのオブジェクトを作成
    temp_time=[(temp, timestamp)]

    #timestampの値が重複した時の例外処理
    #threadを使うとなぜか０分に関数が二回実行されてしまい、テーブルに入れる値が二重になるので、timestampをUNIQUEに設定して例外処理で保存させないようにした
    try:
        conn = sqlite3.connect("Sample.sqlite3")
        c = conn.cursor()
        #テーブルに温度と日時を入れる
        c.executemany("insert into temp_table (temp, timestamp) values (?, ?)", temp_time)

    except sqlite3.IntegrityError:
        print("timestampが重複しています")

    conn.commit()
    conn.close()