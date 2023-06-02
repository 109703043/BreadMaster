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
    password='root'
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

# 前一頁登入後來到「選定特定店家的頁面」，傳<phone_number>進來
@app.route('/<phone_number>/shoppingstore') # buyer的phone_number
def show_shoppingstore(phone_number):
    frequently_used_stores = Frequently_Used_Store.query.filter_by(phone_number = phone_number).all()
    
    # 取得所有的常用店家的 branch_name
    frequently_used_branches = [store.branch_name for store in frequently_used_stores]

    # 根據常用店家的 branch_name 從 Store 表中取得完整的店家資訊，並存回 frequently_used_stores
    frequently_used_stores = Store.query.filter(Store.branch_name.in_(frequently_used_branches)).all()

    all_stores = Store.query.all()
    return render_template('shoppingstore.html',
                           frequently_used_stores = frequently_used_stores,
                           all_stores = all_stores)

if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線