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

from flask import request

@app.route('/register/<action>', methods=['GET', 'POST'])
def register(action):
    # print("enter register")
    if request.method == 'POST':
        # print("request.method == POST")
        if action == 'buyer_reg':
            phone_number = request.form['buyer_phone']
            name = request.form['buyer_name']
            address = request.form['buyer_address']
            email = request.form['buyer_email']
            
            # Check if a Buyer record with the given phone_number exists
            buyer = Buyer.query.get(phone_number)
            
            # If a matching record is found, update the fields
            if buyer:
                buyer.name = name
                buyer.address = address
                buyer.email = email
                db.session.commit()  # Commit the changes
            else:
                # If no matching record is found, create a new Buyer record
                buyer = Buyer(phone_number=phone_number, name=name, address=address, email=email)
                db.session.add(buyer)  # Add the new record
                db.session.commit()  # Commit the changes
            
            return render_template('03_shoppingstore.html', phone_number=phone_number)
            
        elif action == 'store_reg':
            branch_name = request.form['store_name']
            phone_number = request.form['seller_phone']
            business_hours = request.form['seller_business_hours']
            address = request.form['seller_address']
            
            # Check if a Store record with the given branch_name exists
            store = Store.query.get(branch_name)
            
            # If a matching record is found, update the fields
            if store:
                store.phone_number = phone_number
                store.business_hours = business_hours
                store.address = address
                db.session.commit()  # Commit the changes
            else:
                # If no matching record is found, create a new Store record
                store = Store(branch_name=branch_name, phone_number=phone_number, business_hours=business_hours, address=address)
                db.session.add(store)  # Add the new record
                db.session.commit()  # Commit the changes
            
            return render_template('11_seller_history.html', branch_name=branch_name)
            
    return render_template('02_register.html')



if __name__ =="__main__":
    with app.app_context():
        # db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線
