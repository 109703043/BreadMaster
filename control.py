import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

from sqlalchemy import update
from urllib.parse import urlencode

from datetime import datetime, timedelta, time

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



### 00 Error 
@app.route('/errorPage/<msg>/<url_redirect>')
def show_error(msg, url_redirect):
    return render_template('00_errorPage.html', 
                           msg = msg, 
                           url_redirect = url_redirect)
                        #    url_redirect = request.referrer)

@app.route('/errorPage/redirect', methods=['POST'])
def errorPage_redirect():
    url_redirect = request.form['url_redirect']
    return redirect(url_redirect)


### 01 登入 http://127.0.0.1:5000
@app.route('/')
def root_redirect_to_login():
    return redirect(url_for('render_login'))

@app.route('/login')
def render_login():
    return render_template('01_login.html')

@app.route('/login/<action>', methods=['GET', 'POST'])
def login(action):
    if request.method == 'POST':
        if action == 'buyer_login':
            buyer_phone = request.form['buyer_phone']
            buyer = Buyer.query.filter_by(phone_number = buyer_phone).first()
            if(buyer != None):
                return redirect(url_for('show_shoppingStore', phone_number = buyer_phone))
            else:
                return redirect(url_for('show_error', 
                                        msg = 'Buyer does not exist', 
                                        url_redirect = url_for('render_login')))
        elif action == 'store_login':
            store_name = request.form['seller_store']
            store = Store.query.filter_by(branch_name = store_name).first()
            if(store != None):
                return redirect(url_for('show_leftoverProduct', branch_name = store_name))
            else:
                return redirect(url_for('show_error', 
                                        msg = 'Store does not exist', 
                                        url_redirect = url_for('render_login')))
    return redirect(url_for('render_login'))



### 02 註冊 http://127.0.0.1:5000/register
@app.route('/register')
def render_register():
    return render_template('02_register.html')

@app.route('/register/<action>', methods=['GET', 'POST'])
def register(action):
    if request.method == 'POST':
        if action == 'buyer_reg':
            phone_number = request.form['buyer_phone']
            name = request.form['buyer_name']
            address = request.form['buyer_address']
            email = request.form['buyer_email']
            
            # Check if a Buyer record with the given phone_number exists
            buyer = Buyer.query.get(phone_number)
            
            # If a matching record is found, update the fields
            if buyer:
                return redirect(url_for('show_error', 
                                        msg = 'User existed', 
                                        url_redirect = url_for('render_register')))
                # buyer.name = name
                # buyer.address = address
                # buyer.email = email
                # db.session.commit()  # Commit the changes
            else:
                # If no matching record is found, create a new Buyer record
                buyer = Buyer(phone_number=phone_number, name=name, address=address, email=email)
                db.session.add(buyer)  # Add the new record
                db.session.commit()  # Commit the changes
            
        elif action == 'store_reg':
            branch_name = request.form['seller_store']
            phone_number = request.form['seller_phone']
            business_hours = request.form['seller_business_hours']
            address = request.form['seller_address']
            
            # Check if a Store record with the given branch_name exists
            store = Store.query.get(branch_name)
            
            # If a matching record is found, update the fields
            if store:
                return redirect(url_for('show_error', 
                                        msg = 'Store existed', 
                                        url_redirect = url_for('render_register')))
                # store.phone_number = phone_number
                # store.business_hours = business_hours
                # store.address = address
                # db.session.commit()  # Commit the changes
            else:
                # If no matching record is found, create a new Store record
                store = Store(branch_name=branch_name, phone_number=phone_number, business_hours=business_hours, address=address)
                db.session.add(store)  # Add the new record
                db.session.commit()  # Commit the changes
            
    return redirect(url_for('render_login'))



### 03 買家: 選店家 http://127.0.0.1:5000/0955336611/shoppingStore
# 前一頁登入後來到「選定特定店家的頁面」，傳<phone_number>進來
@app.route('/<phone_number>/shoppingStore') # buyer的phone_number
def show_shoppingStore(phone_number):
    frequently_used_stores = Frequently_Used_Store.query.filter_by(phone_number = phone_number).all()
    
    # 取得所有的常用店家的 branch_name
    frequently_used_branches = [store.branch_name for store in frequently_used_stores]

    # 根據常用店家的 branch_name 從 Store 表中取得完整的店家資訊，並存回 frequently_used_stores
    frequently_used_stores = Store.query.filter(Store.branch_name.in_(frequently_used_branches)).all()

    all_stores = Store.query.all()
    return render_template('03_shoppingStore.html',
                           frequently_used_stores = frequently_used_stores,
                           all_stores = all_stores, 
                           phone_number = phone_number)



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
                        item_price  = selected_leftover_product.price,
                        quantity_ordered = 1
                    ) 
                    db.session.add(new_order_item)
                db.session.commit()

       return redirect(url_for('purchase', phone_number = phone_number, branch_name = branch_name))
    else :    
       return redirect(url_for('purchase', phone_number = phone_number, branch_name = branch_name))



### 05 買家: 店家評價 http://127.0.0.1:5000/reviews/0912445566/Daan%20Store
# 前一頁按了一個btn，傳phone_number和branch_name進來
@app.route('/reviews/<phone_number>/<branch_name>')
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
                           , reviews = reviews, my_score=my_score, my_content=my_content, phone_number = phone_number)

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



### 06 買家: 購物車 http://127.0.0.1:5000/0912345678/shoppingCart
@app.route('/<phone_number>/shoppingCart')
def render_shoppingCart(phone_number):
    order = Order.query.filter_by(phone_number = phone_number, 
                                  order_status = 'Not Submit Yet').first()
    if(order == None): # no order in cart
        order_number = db.session.query(db.func.max(Order.order_number)).scalar()+1
        new_order = Order(
                        order_number= order_number,
                        phone_number= phone_number,
                        order_status = "Not Submit Yet",
                        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
        db.session.add(new_order)
        db.session.commit()
        order = Order.query.filter_by(phone_number = phone_number, 
                                      order_status = 'Not Submit Yet').first()
    order_item = Order_Item.query.filter_by(order_number = order.order_number).all()
    order_item_info = [Leftover_Product.query.filter_by(branch_name = p.branch_name, 
                                                        product_code = p.product_code).first()
                       for p in order_item]
    return render_template('06_shoppingCart.html', 
                           phone_number = phone_number, 
                           order_item = order_item, 
                           order_item_info = order_item_info, 
                           len = len(order_item))

@app.route('/<phone_number>/shoppingCart/<action>', methods=['GET', 'POST'])
def shoppingCart(phone_number, action):
    order = Order.query.filter_by(phone_number = phone_number, 
                                  order_status = 'Not Submit Yet').first()
    if request.method == 'POST':
        order_list = Order_Item.query.join(Order).join(Leftover_Product).filter(
        Order_Item.order_number == Order.order_number,
        Order_Item.product_code == Leftover_Product.product_code,
        Order.order_status == 'Not Submit Yet').all()
        
        if action == 'submit_cart':
            if(order_list != []):
                # renew item price
                for item in order_list:
                    quantity_ordered = request.form[f'quantity_ordered_{item.branch_name}_{item.product_code}']
                    item_price = int(item.item_price) * int(quantity_ordered)
                    item.quantity_ordered = quantity_ordered
                    item.item_price = item_price

                # renew status and time of order
                order.order_status = 'Pending Order'
                order.order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                db.session.commit()

                return redirect(url_for('show_buyer_orderDetail', 
                                        phone_number = phone_number, 
                                        order_number = order.order_number))
            else:
                return redirect(url_for('render_shoppingCart', 
                                        phone_number = phone_number))

        elif action == 'clear_cart':
            # clear order_item
            for order in order_list:
                db.session.delete(order)
                
            db.session.commit()

            return redirect(url_for('render_shoppingCart', 
                                    phone_number = phone_number))



### 07 買家: 訂單一覽 http://127.0.0.1:5000/buyerOrderOutline/0922334455
@app.route('/buyerOrderOutline/<phone_number>') # phone_number of the buyer
def show_buyer_orderOutline(phone_number):

    order_list = Order.query.filter(Order.phone_number == phone_number, 
                                    Order.order_status != 'Not Submit Yet')

    return render_template('07_orderOutline.html',
                           order_list = order_list, 
                           phone_number = phone_number)



### 08 買家: 訂單詳細 http://127.0.0.1:5000/buyerOrderDetail/10001
@app.route('/buyerOrderDetail/<phone_number>/<order_number>') # order_number of the order
def show_buyer_orderDetail(phone_number, order_number):

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
                           order_item_len = order_item.count(), 
                           phone_number = phone_number)



### 09 店家: 上架中商品 http://127.0.0.1:5000/Daan%20Store/storeLeftover
#查詢該分店的上架中剩食
@app.route('/<branch_name>/storeLeftover')
def show_leftoverProduct(branch_name):
    leftover_Product_list = Leftover_Product.query.filter_by(branch_name=branch_name)
    return render_template('09_storeLeftover.html', leftover_Product_list=leftover_Product_list, branch_name=branch_name)

#修改上架中剩食數量
@app.route('/updateQuantity', methods=['POST'])
def update_quantity():
    branch_name = request.form['branch_name']
    product_code = request.form['product_code']
    new_quantity = int(request.form[f'new_quantity_{product_code}'])

    # 查詢要修改的紀錄
    leftover_product = Leftover_Product.query.filter_by(branch_name=branch_name, product_code=product_code).first()
    if leftover_product:
        leftover_product.quantity_in_stock = new_quantity
        db.session.commit()
        
        params = urlencode({'branch_name': branch_name})  # 將分店名稱設為編碼參數
        redirect_url = f'/{branch_name}/storeLeftover?' + params  # 按下修改後還可以顯示該分店的上架中剩食
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
        (Order.order_status == 'Pending Order') | (Order.order_status == 'Order Accepted')| (Order.order_status == 'Not Submit Yet')
    ).values(order_status='Cancelled')
    db.session.execute(update_query)

    db.session.commit()

    params = urlencode({'branch_name': branch_name})  # 將分店名稱設為編碼參數
    redirect_url = f'/{branch_name}/storeLeftover?' + params  # 按下關店之後還可以顯示該分店的上架中剩食(就會看到數量都是0、保存期限被加了一天)
    return redirect(redirect_url)



### 10-1 店家: 進行中訂單(一覽) http://127.0.0.1:5000/Nandu%20Store/branchOrderOutline
@app.route('/<branch_name>/branchOrderOutline') # phone_number of the buyer
def show_branch_orderOutline(branch_name):

    # 根據分店名稱 (branch_name) 從 Order_Item 表中取得該店家的所有訂單項目
    order_items = Order_Item.query.filter_by(branch_name=branch_name).all()

    # 取得訂單項目中的訂單編號
    order_numbers = [order_item.order_number for order_item in order_items]

    # 根據訂單編號從 Order 表中取得訂單資訊
    order_list = Order.query.filter(Order.order_number.in_(order_numbers), 
                                    Order.order_status != 'Completed',
                                    Order.order_status != 'Cancelled').all()

    return render_template('10(1)_seller_order.html',
                           order_list = order_list, 
                           branch_name = branch_name)

### 10-2 店家: 訂單詳細  pending   http://127.0.0.1:5000/Zhongxing%20Store/branchOrderDetail/10018
###                     accepted  http://127.0.0.1:5000/Shinkuchan%20Store/branchOrderDetail/10016
###                     completed http://127.0.0.1:5000/Nandu%20Store/branchOrderDetail/10026
@app.route('/<branch_name>/branchOrderDetail/<order_number>') # order_number of the order
def show_seller_orderDetail(branch_name, order_number):

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
                           order_item_len = order_item.count(), 
                           branch_name = branch_name)

@app.route('/<branch_name>/<order_number>/update_order_status/accept', methods=['POST'])
def accept_order(branch_name, order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    if order.order_status == 'Pending Order':
        order.order_status = 'Order Accepted'
        db.session.commit()

        # update the quantity in stock
        order_item = Order_Item.query.filter_by(order_number = order_number)
        for p in order_item:
            product = Leftover_Product.query.filter_by(branch_name = p.branch_name, 
                                                       product_code = p.product_code).first()
            product.quantity_in_stock -= p.quantity_ordered
            db.session.commit()

        return redirect(url_for('show_seller_orderDetail', 
                                branch_name = branch_name, 
                                order_number=order_number))
    return {'success': False}

@app.route('/<branch_name>/<order_number>/update_order_status/complete', methods=['POST'])
def complete_order(branch_name, order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    if order.order_status == 'Order Accepted':
        order.order_status = 'Completed'
        db.session.commit()
        return redirect(url_for('show_seller_orderDetail', 
                                branch_name = branch_name, 
                                order_number=order_number))
    return {'success': False}



### 11 店家: 歷史訂單 http://127.0.0.1:5000/Daan%20Store/branch_history
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

    return render_template('11_seller_history.html', 
                           merged_data = merged_data, 
                           branch_name = branch_name)



### 12 店家: 報表 http://127.0.0.1:5000/Daan%20Store/storeReport
@app.route('/<branch_name>/storeReport', methods=['GET', 'POST']) # phone_number of the buyer
def show_report(branch_name):
    if request.method == 'POST':
        datetime = request.form['datetime']
        leftover_history_list = Leftover_History.query.filter_by(branch_name=branch_name)\
                                                      .filter(Leftover_History.removal_time == datetime)
        return render_template('12_report.html', 
                               leftover_history_list=leftover_history_list, 
                               branch_name = branch_name)

    return render_template('12_report.html', 
                           leftover_history_list = [], 
                           branch_name = branch_name)



if __name__ =="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit() #?
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線
