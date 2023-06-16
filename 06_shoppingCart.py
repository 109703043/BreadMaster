import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql
from datetime import datetime


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
    password=''
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

@app.route('/shoppingCart/<action>', methods=['GET', 'POST'])
def shoppingCart(action):
    if request.method == 'POST':
        order_list = Order_Item.query.join(Order).join(Leftover_Product).filter(
        Order_Item.order_number == Order.order_number,
        Order_Item.product_code == Leftover_Product.product_code,
        Order.order_status == 'Not Submit Yet').all()
        
        if action == 'submit_cart':
            # renew item price
            for item in order_list:
                quantity_ordered = int(request.form.get(f"quantity_ordered_{item.order_number}"))
                item_price = item.leftover_product.price * quantity_ordered
                item.quantity_ordered = quantity_ordered
                item.item_price = item_price

            # renew status and time of order
            order.order_status = 'Pending Order'
            order.order_time = datetime.now()

        elif action == 'clear_cart':
            # clear order_item
            for order in order_list:
                order.order_item.clear()
            
    return render_template('06_shoppingCart.html')


if __name__ =="__main__":
    with app.app_context():
        # db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線
