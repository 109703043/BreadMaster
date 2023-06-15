import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

from model import db, Buyer, Store, Order, Leftover_Product, Order_Item, Leftover_History, Review, Frequently_Used_Store  #, tables

app = Flask(__name__)
# <username>、<password>、<host>、<port>和<database>
app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:root@localhost:3306/breadmaster" # 改MySQL檔案路徑
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



### 03 買家: 選店家 http://127.0.0.1:5000/0955336611/shoppingstore
# 前一頁登入後來到「選定特定店家的頁面」，傳<phone_number>進來
@app.route('/<phone_number>/shoppingstore') # buyer的phone_number
def show_shoppingstore(phone_number):
    frequently_used_stores = Frequently_Used_Store.query.filter_by(phone_number = phone_number).all()
    
    # 取得所有的常用店家的 branch_name
    frequently_used_branches = [store.branch_name for store in frequently_used_stores]

    # 根據常用店家的 branch_name 從 Store 表中取得完整的店家資訊，並存回 frequently_used_stores
    frequently_used_stores = Store.query.filter(Store.branch_name.in_(frequently_used_branches)).all()

    all_stores = Store.query.all()
    return render_template('03_shoppingstore.html',
                           frequently_used_stores = frequently_used_stores,
                           all_stores = all_stores)



### 05 買家: 店家評價 http://127.0.0.1:5000/reviews/0912445566/Daan%20Store
# 前一頁按了一個btn，傳phone_number和branch_name進來
@app.route('/reviews/<phone_number>/<branch_name>', methods=['GET','POST'])
def show_reviews(phone_number,branch_name):

    buyer = Buyer.query.filter_by(phone_number = phone_number).first()
    branch = Store.query.filter_by(branch_name = branch_name).first()
    favorite = Frequently_Used_Store.query.filter_by(phone_number = phone_number, branch_name = branch_name).first()
    is_favorite = False
    if(favorite is not None):
        is_favorite = True

    reviews = Review.query.filter_by(branch_name=branch_name).all()
    my_review = Review.query.filter_by(phone_number=phone_number, branch_name=branch_name).first()
    if(my_review != None):
        my_score = Review.query.filter_by(phone_number=phone_number, branch_name=branch_name).first().score
        my_content = Review.query.filter_by(phone_number=phone_number, branch_name=branch_name).first().content
    else:
        my_score = 0
        my_content = ''
    return render_template('05_reviews.html',buyer = buyer, store = branch, is_favorite = is_favorite
                           , reviews = reviews, my_score=my_score, my_content=my_content)

@app.route('/reviews/<action>', methods=['POST', 'GET']) #加入接收的參數
def modify_review(action):
    if request.method == 'POST':
        if action == 'add_favorite':
            phone_number = request.form['phone_number']
            branch_name = request.form['branch_name']
    
            favorite_store = Frequently_Used_Store(phone_number=phone_number, branch_name=branch_name)
            db.session.add(favorite_store)
            db.session.commit()
        elif action == 'delete_favorite':
            phone_number = request.form['phone_number']
            branch_name = request.form['branch_name']
    
            favorite_store = Frequently_Used_Store.query.filter_by(phone_number=phone_number, branch_name=branch_name).first()
            db.session.delete(favorite_store)
            db.session.commit()
        elif action == 'modify_review':
            my_score = int(request.form['my_score'])
            my_content = request.form['my_content']
            phone_number = request.form['phone_number']
            branch_name = request.form['branch_name']

            review = Review.query.filter_by(phone_number=phone_number, branch_name=branch_name).first()

            if review is not None:
                # 修改現有評論  
                review.score = my_score
                review.content = my_content
                
                # print(review.score == 0, review.content == '')
                # 刪除空評論
                if review.score == 0 and review.content == '':
                    db.session.delete(review)

            else:
                # 新增新的評論
                review = Review(phone_number=phone_number, branch_name=branch_name, score=my_score, content=my_content)
                db.session.add(review)

    db.session.commit()
    return redirect(url_for('show_reviews', phone_number=phone_number, branch_name=branch_name))



### 07 買家: 訂單一覽 http://127.0.0.1:5000/buyerOrderOutline/0922334455
@app.route('/buyerOrderOutline/<phone_number>') # phone_number of the buyer
def show_orderOutline(phone_number):

    order_list = Order.query.filter_by(phone_number = phone_number)

    return render_template('07_orderOutline.html',
                           order_list = order_list)



### 08 買家: 訂單詳細 http://127.0.0.1:5000/buyerOrderDetail/10001
@app.route('/buyerOrderDetail/<order_number>') # order_number of the order
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
