import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, time
from sqlalchemy import update
from urllib.parse import urlencode
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


#查詢該分店的上架中剩食
@app.route('/storeLeftover', methods=['GET', 'POST'])
def show_leftoverHistory():
    if request.method == 'POST':
        branch_name = request.form['branch_name']
        leftover_Product_list = Leftover_Product.query.filter_by(branch_name=branch_name)
        return render_template('09_storeLeftover.html', leftover_Product_list=leftover_Product_list, branch_name=branch_name)

    branch_name = request.args.get('branch_name')
    if branch_name:
        leftover_Product_list = Leftover_Product.query.filter_by(branch_name=branch_name)
    else:
        leftover_Product_list = []

    return render_template('09_storeLeftover.html', leftover_Product_list=leftover_Product_list)

#修改上架中剩食數量
@app.route('/updateQuantity', methods=['POST'])
def update_quantity():
    branch_name = request.form['branch_name']
    product_code = request.form['product_code']
    new_quantity = int(request.form['new_quantity'])

    # 查詢要修改的紀錄
    leftover_product = Leftover_Product.query.filter_by(branch_name=branch_name, product_code=product_code).first()
    if leftover_product:
        leftover_product.quantity_in_stock = new_quantity
        db.session.commit()
        
        params = urlencode({'branch_name': branch_name})  # 將分店名稱設為編碼參數
        redirect_url = '/storeLeftover?' + params  # 按下修改後還可以顯示該分店的上架中剩食
        return redirect(redirect_url)
    else:
        return "紀錄不存在"

#關店
@app.route('/closeStore', methods=['POST'])
def close_store():
    branch_name = request.form['branch_name']

    # 查询该分店的所有记录
    leftover_products = Leftover_Product.query.filter_by(branch_name=branch_name).all()
    for product in leftover_products:
        
        b = product.branch_name
        p = product.product_code
        expirationdate = product.expiration_date  # 原始的保存期限
        r = None  # 預設為 None，稍後會根據 branch_name 的不同進行設定
        q = product.quantity_in_stock

        if b == 'Daan Store':
            r = datetime.combine(expirationdate, time(hour=22))  # 設置removal_time的時分秒為 22:00:00
        elif b == 'Xinyi Store':
            r = datetime.combine(expirationdate, time(hour=20))
        elif b == 'Zhongshan Store':
            r = datetime.combine(expirationdate, time(hour=19))
        elif b == 'Zhongxiao Store':
            r = datetime.combine(expirationdate, time(hour=21))
        elif b == 'Songshan Store':
            r = datetime.combine(expirationdate, time(hour=22))
        elif b == 'Shinkuchan Store':
            r = datetime.combine(expirationdate, time(hour=21))
        elif b == 'Nandu Store':
            r = datetime.combine(expirationdate, time(hour=20))
        elif b == 'Zhongxing Store':
            r = datetime.combine(expirationdate, time(hour=19))
             
        q = product.quantity_in_stock

        leftoverHistory = Leftover_History(branch_name = b,product_code = p,removal_time = r,quantity_removed = q)
        db.session.add(leftoverHistory)
        
        product.expiration_date += timedelta(days=1)  #要關店了，把保存期限設為隔一天，這樣明天開店就直接新增上架數量就好
        product.quantity_in_stock = 0 #要關店報銷了，把數量清0
    
    #要關店了，檢查有無尚未完成的訂單，全部改為'Cancelled'
    update_query = update(Order).where(
        (Order.order_status == 'Pending Order') | (Order.order_status == 'Order Accepted')
    ).values(order_status='Cancelled')
    db.session.execute(update_query)

    db.session.commit()

    params = urlencode({'branch_name': branch_name})  # 將分店名稱設為編碼參數
    redirect_url = '/storeLeftover?' + params  # 按下關店之後還可以顯示該分店的上架中剩食(就會看到數量都是0、保存期限被加了一天)
    return redirect(redirect_url)

if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線