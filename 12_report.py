# 有做一個小修改: leftover_history的removal_time型別從TIMESTAMP改成VARCHAR(50)
# (可直接去workbench修改)
import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql

from model import db, Buyer, Store, Review, Frequently_Used_Store, Leftover_History, Leftover_Product, Order, Order_Item 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Go140814@localhost:3306/BreadMaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# create connection to MySQL server
connection = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='Go140814'
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



@app.route('/storeReport', methods=['GET', 'POST']) # phone_number of the buyer
def show_leftoverHistory():
    if request.method == 'POST':
        branch_name = request.form['branch_name']
        datetime = request.form['datetime']
        leftover_history_list = Leftover_History.query.filter_by(branch_name=branch_name)\
                                                      .filter(Leftover_History.removal_time == datetime)
        return render_template('12_report.html', leftover_history_list=leftover_history_list)

    return render_template('12_report.html')


if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線