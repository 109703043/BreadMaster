import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

from datetime import datetime

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



### 04 買家: 進入店家選購 http://127.0.0.1:5000/purchase/0923558899/Nandu%20Store
@app.route('/purchase/<phone_number>/<branch_name>') # buyer.phone_number
def purchase(phone_number, branch_name):
   leftover_products = db.session.query(Leftover_Product).filter(Leftover_Product.branch_name == branch_name).all()
   store = Store.query.filter_by(branch_name = branch_name).first()
   if leftover_products != []:
       return render_template('04_purchase.html', 
                              leftover_products = leftover_products, 
                              phone_number = phone_number, 
                              branch_name = branch_name, 
                              store = store)
   else:
       return render_template('04_purchase.html', 
                              message="No leftover_product found.", 
                              store = store)

@app.route("/addToFavorites", methods=['POST'])
def addToFavorites():
    phone_number = request.form['phone_number']
    branch_name = request.form['branch_name']
    frequently_used = db.session.query(Frequently_Used_Store).filter_by(phone_number = phone_number, 
                                                                        branch_name = branch_name).all()
    if frequently_used  :
        return redirect(request.referrer)
    else:
        new_frequently_used = Frequently_Used_Store(
            phone_number = phone_number,
            branch_name = branch_name
        )
        db.session.add(new_frequently_used)
        db.session.commit()
    return redirect(request.referrer)

@app.route("/removeFromFavorites",methods=['POST'])
def removeFromFavorites():
    phone_number = request.form['phone_number']
    branch_name = request.form['branch_name']
    new_frequently_used_to_delete = db.session.query(Frequently_Used_Store).filter_by(phone_number = phone_number, 
                                                                                      branch_name = branch_name).first()
    if new_frequently_used_to_delete :
        db.session.delete(new_frequently_used_to_delete)
        db.session.commit()
    return redirect(request.referrer)

# @app.route("/reviews",methods=['GET','POST'])
# def reviews():
#     reviews = db.session.query(Review).filter(Review.branch_name == selected_store.branch_name)
#     if reviews :
#       for review in reviews:
#         print(review.phone_number)
#         print(review.branch_name)
#         print(review.score)
#         print(review.content)
#     else :
#        print("No review found.")   
#     #return redirect(url_for('review_url'))
#     return '我已經幫你找到特定分店的review了,看你要用甚麼變數去接收'

# @app.route("/shoppingCart",methods=['GET','POST'])
# def shoppingCart():
#     #return redirect(url_for('shoppingCart_url'))
#     return'進入shoppingCart頁面'

# @app.route("/shoppingstore",methods=['GET','POST'])
# def shoppingstore():
#     #return redirect(url_for('shoppingstore_url'))
#     return'回到shoppingstore頁面'

@app.route("/order",methods=['GET','POST'])
def order():
    phone_number = request.form['phone_number']
    branch_name = request.form['branch_name']
    if request.method =='POST':
       selected_leftover_products_key = request.form.getlist('leftover_product')  #獲取被勾選的選項列表
       selected_leftover_products = db.session.query(Leftover_Product).filter_by(branch_name=branch_name).filter(Leftover_Product.product_code.in_(selected_leftover_products_key)).all()
       print(selected_leftover_products_key)
       for selected_leftover_product in selected_leftover_products :
            if selected_leftover_product.quantity_in_stock !=0 :
                order = Order.query.filter_by(phone_number = phone_number, 
                                              order_status = 'Not Submit Yet').first()
                if(order != None): # there's an order in cart
                    order_number = order.order_number
                else: # no order in cart
                    order_number = db.session.query(db.func.max(Order.order_number)).scalar()+1
                    new_order = Order(
                        order_number= order_number,
                        phone_number= phone_number,
                        order_status = "Not Submit Yet",
                        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    db.session.add(new_order)
                    db.session.commit()

                order_item = Order_Item.query.filter_by(product_code = selected_leftover_product.product_code, 
                                                        order_number = order_number).first()
                if(order_item != None): # order_item exists
                    order_item.quantity_ordered += 1
                else: # have not add this item to cart yet
                    new_order_item= Order_Item(
                        order_number = order_number,
                        branch_name  = branch_name,
                        product_code  = selected_leftover_product.product_code,
                        item_price  = selected_leftover_product.quantity_in_stock*selected_leftover_product.price,
                        quantity_ordered = 1
                    ) 
                    db.session.add(new_order_item)
                db.session.commit()

                selected_leftover_product.quantity_in_stock -= 1
                db.session.commit()
       return redirect(url_for('purchase', phone_number = phone_number, branch_name = branch_name))
    else :    
       return redirect(url_for('purchase', phone_number = phone_number, branch_name = branch_name))



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
def show_buyer_orderOutline(phone_number):

    order_list = Order.query.filter_by(phone_number = phone_number)

    return render_template('07_orderOutline.html',
                           order_list = order_list)



### 08 買家: 訂單詳細 http://127.0.0.1:5000/buyerOrderDetail/10001
@app.route('/buyerOrderDetail/<order_number>') # order_number of the order
def show_buyer_orderDetail(order_number):

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



### 10-1 店家: 訂單一覽 http://127.0.0.1:5000/branchOrderOutline/Daan%20Store
@app.route('/branchOrderOutline/<branch_name>') # phone_number of the buyer
def show_branch_orderOutline(branch_name):

    # 根據分店名稱 (branch_name) 從 Order_Item 表中取得該店家的所有訂單項目
    order_items = Order_Item.query.filter_by(branch_name=branch_name).all()

    # 取得訂單項目中的訂單編號
    order_numbers = [order_item.order_number for order_item in order_items]

    # 根據訂單編號從 Order 表中取得訂單資訊
    order_list = Order.query.filter(Order.order_number.in_(order_numbers)).all()

    return render_template('10(1)_seller_order.html',
                           order_list = order_list)

### 10-2 店家: 訂單詳細  pending   http://127.0.0.1:5000/branchOrderDetail/10018
###                     accepted  http://127.0.0.1:5000/branchOrderDetail/10016
###                     completed http://127.0.0.1:5000/branchOrderDetail/10026
@app.route('/branchOrderDetail/<order_number>') # order_number of the order
def show_seller_orderDetail(order_number):

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
        return redirect(url_for('show_seller_orderDetail', order_number=order_number))
    return {'success': False}

@app.route('/update_order_status/<order_number>/complete', methods=['POST'])
def complete_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    if order.order_status == 'Order Accepted':
        order.order_status = 'Completed'
        db.session.commit()
        return redirect(url_for('show_seller_orderDetail', order_number=order_number))
    return {'success': False}



### 11 店家: 歷史紀錄 http://127.0.0.1:5000/Daan%20Store/branch_history
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
