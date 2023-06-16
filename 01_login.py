import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

# 匯入 model　中的　table
from model import db, Buyer, Store, Review, Frequently_Used_Store, Leftover_History, Leftover_Product, Order, Order_Item 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/BreadMaster' # 改MySQL檔案路徑
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 建立與MySQL伺服器的連線
connection = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='Cty125qq'
)

# 建立空schema
try:
    with connection.cursor() as cursor:
        sql = "CREATE DATABASE IF NOT EXISTS BreadMaster"
        cursor.execute(sql)
    connection.commit()
    print("資料庫 'BreadMaster' 建立成功")
except pymysql.Error as e:
    print("資料庫建立失敗:", str(e))
finally:
    connection.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    print("enter login")
    if request.method == 'POST':
        print("request.method == POST")
        if 'buyer_button' in request.form:
            buyer_phone = request.form['buyer_phone']
            return render_template('03_shoppingstore.html', phone_number = buyer_phone)
        elif 'store_button' in request.form:
            store_name = request.form['store_name']
            # 09_...html
            return render_template('11_seller_history.html', branch_name = store_name)
        elif 'register_button' in request.form:
            print("click register_button")
            return render_template('02_register.html')

    return render_template('01_login.html')

if __name__ =="__main__":
    with app.app_context():
        # db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線
