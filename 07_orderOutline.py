import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

from model import db, Buyer, Store, Review, Frequently_Used_Store, Leftover_History, Leftover_Product, Order, Order_Item 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/BreadMaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# create connection to MySQL server
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



@app.route('/buyerOrderOutline/<phone_number>/') # phone_number of the buyer
def show_orderOutline(phone_number):

    order_list = Order.query.filter_by(phone_number = phone_number)

    return render_template('07_orderOutline.html',
                           order_list = order_list)



@app.route('/buyerOrderDetail/<order_number>/') # order_number of the order
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

    return render_template('08_orderDetail.html',
                           order = order, 
                           order_item = order_item, 
                           product_name = product_name, 
                           price_sum = price_sum, 
                           order_item_len = order_item.count())



if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線