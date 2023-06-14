import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

from model import db, Buyer, Store, Review, Frequently_Used_Store, Leftover_History, Leftover_Product, Order, Order_Item 

# 建立Flask應用程式
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/BreadMaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 建立與MySQL伺服器的連線
connection = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='root'
)

# create empty schema
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


@app.route('/<branch_name>/branch_history') # branch的name
def show_branch_history_orders(branch_name):

    # 根據分店名稱 (branch_name) 從 Order_Item 表中取得該店家的所有訂單項目
    order_items = Order_Item.query.filter_by(branch_name=branch_name).all()

    # 取得訂單項目中的訂單編號
    order_numbers = [order_item.order_number for order_item in order_items]

    # 根據訂單編號從 Order 表中取得訂單資訊
    orders = Order.query.filter(Order.order_number.in_(order_numbers)).all()

    # 根據買家電話號從 Buyer 表中取得買家名字
    buyer_phones = [order.phone_number for order in orders]
    buyer_name = Buyer.query.filter(Buyer.phone_number.in_(buyer_phones)).all()

    # 將買家名字以字典形式存儲，方便後續查詢
    buyer_names = {buyer.phone_number: buyer.name for buyer in buyer_name}

    # 將訂單項目和訂單合併
    merged_data = []
    for order_item in order_items:
        order = next((order for order in orders if order.order_number == order_item.order_number), None)
        if order:
            buyer_name = buyer_names.get(order.phone_number)
            merged_data.append((order_item, order, buyer_name))


    return render_template('11_seller_history.html', merged_data = merged_data)

    
if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線