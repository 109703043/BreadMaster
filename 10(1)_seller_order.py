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



@app.route('/branchOrderOutline/<branch_name>/') # phone_number of the buyer
def show_branch_orderOutline(branch_name):

    # 根據分店名稱 (branch_name) 從 Order_Item 表中取得該店家的所有訂單項目
    order_items = Order_Item.query.filter_by(branch_name=branch_name).all()

    # 取得訂單項目中的訂單編號
    order_numbers = [order_item.order_number for order_item in order_items]

    # 根據訂單編號從 Order 表中取得訂單資訊
    order_list = Order.query.filter(Order.order_number.in_(order_numbers)).all()

    return render_template('10(1)_seller_order.html',
                           order_list = order_list)



@app.route('/branchOrderDetail/<order_number>/') # order_number of the order
def show_orderDetail(order_number):

    order = Order.query.filter_by(order_number = order_number).first()

    order_item = Order_Item.query.filter_by(order_number = order_number)

    product_name = list()
    price_sum = 0

    for p in order_item:
        product_name.append(
            Leftover_Product.query.filter_by(branch_name = p.branch_name, 
                                             product_code = p.product_code).first().product_name
        )
        price_sum += p.item_price

    return render_template('10(2)_seller_order.html',
                           order = order, 
                           order_item = order_item, 
                           product_name = product_name, 
                           price_sum = price_sum, 
                           order_item_len = order_item.count())


@app.route('/update_order_status/<order_number>/accept', methods=['POST'])
def accept_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    if order.order_status == 'Pending Order':
        order.order_status = 'Order Accepted'
        db.session.commit()
        return redirect(url_for('show_orderDetail', order_number=order_number))
    return {'success': False}


@app.route('/update_order_status/<order_number>/complete', methods=['POST'])
def complete_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    if order.order_status == 'Order Accepted':
        order.order_status = 'Completed'
        db.session.commit()
        return redirect(url_for('show_orderDetail', order_number=order_number))
    return {'success': False}



if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線