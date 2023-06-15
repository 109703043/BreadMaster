from flask import Flask, request, render_template, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql


#建立Flask應用程式
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:Hsnut%40102260424@localhost:3306/breadmaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SESSION_REFERRER'] = True

db = SQLAlchemy(app)

#直接跳到74行
class Buyer(db.Model):
    __tablename__ = 'buyer'
    phone_number = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    late_record = db.Column(db.Integer, default=0)

class Store(db.Model):
    __tablename__ = 'store'
    branch_name = db.Column(db.String(50), primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    business_hours = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)

class Order(db.Model):
    __tablename__ = 'order'
    order_number = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'))
    order_status = db.Column(db.String(20), nullable=False)
    order_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

class Order_Item(db.Model):
    __tablename__ = 'order_item'
    order_number = db.Column(db.Integer, db.ForeignKey('order.order_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    product_code = db.Column(db.String(20), db.ForeignKey('leftover_product.product_code'), primary_key=True)
    item_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)

class Review(db.Model):
    __tablename__ = 'review'
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    score = db.Column(db.Integer)
    content = db.Column(db.String(500))

class Frequently_Used_Store(db.Model):
    __tablename__ = 'frequently_used_store'
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)

class Leftover_Product(db.Model):
    __tablename__ = 'leftover_product'
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True, index = True)
    product_code = db.Column(db.String(20), primary_key=True, index = True)
    expiration_date = db.Column(db.Date, nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)

class Leftover_History(db.Model):
    __tablename__ = 'leftover_history'
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    product_code = db.Column(db.String(20), db.ForeignKey('leftover_product.product_code'), primary_key=True)
    removal_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), primary_key=True)
    quantity_removed = db.Column(db.Integer, nullable=False)

############################################

buyer=Buyer(
    phone_number  = "0911223344",
    name = "Li Jialing",
    address = "No. 51, Section 2, Minzu Road, South District, Tainan City",
    email = "ligialin@gmail.com",
    late_record = 0
)


selected_store = Store(
    branch_name="Daan Store",
    phone_number="02-7756-3322",
    business_hours="08:00–22:00",
    address="No. 89, Section 4, Renai Road, Daan District, Taipei City"
)

new_frequently_used =Frequently_Used_Store(
    phone_number = "0911223344",
    branch_name = "Daan Store"
)


@app.route('/purchase')
def purchase():
   leftover_products = db.session.query(Leftover_Product).filter(Leftover_Product.branch_name == "Daan Store").all()
   if leftover_products :
       return render_template('purchase.html',leftover_products=leftover_products)
   else :
       return render_template('purchase.html',message="No leftover_product found.")

@app.route("/addToFavorites", methods=['POST'])
def addToFavorites():
  frequently_used = db.session.query(Frequently_Used_Store).filter_by(phone_number = buyer.phone_number,branch_name = selected_store.branch_name).all()
  if frequently_used  :
    return redirect(request.referrer)
  else: 
   db.session.add(new_frequently_used)
   db.session.commit()
   return redirect(request.referrer)
 

@app.route("/removeFromFavorites",methods=['POST'])
def removeFromFavorites():
  new_frequently_used_to_delete = db.session.query(Frequently_Used_Store).filter_by(phone_number = buyer.phone_number,branch_name = selected_store.branch_name).first()
  if new_frequently_used_to_delete :
    db.session.delete( new_frequently_used_to_delete)
    db.session.commit()
  return redirect(request.referrer)
 

@app.route("/reviews",methods=['GET','POST'])
def reviews():
    reviews = db.session.query(Review).filter(Review.branch_name == selected_store.branch_name)
    if reviews :
      for review in reviews:
        print(review.phone_number)
        print(review.branch_name)
        print(review.score)
        print(review.content)
    else :
       print("No review found.")   
    #return redirect(url_for('review_url'))
    return '我已經幫你找到特定分店的review了,看你要用甚麼變數去接收'

@app.route("/shoppingCart",methods=['GET','POST'])
def shoppingCart():
    #return redirect(url_for('shoppingCart_url'))
    return'進入shoppingCart頁面'

@app.route("/shoppingstore",methods=['GET','POST'])
def shoppingstore():
    #return redirect(url_for('shoppingstore_url'))
    return'回到shoppingstore頁面'

@app.route("/order",methods=['GET','POST'])
def order():
    if request.method =='POST':
       selected_leftover_products_key = request.form.getlist('leftover_product')  #獲取被勾選的選項列表
       selected_leftover_products = db.session.query(Leftover_Product).filter_by(branch_name=selected_store.branch_name).filter(Leftover_Product.product_code.in_(selected_leftover_products_key)).all()
       print(selected_leftover_products_key)
       for selected_leftover_product in selected_leftover_products :
        if selected_leftover_product.quantity_in_stock !=0 :
         new_order = Order(
            order_number= db.session.query(db.func.max(Order.order_number)).scalar()+1,
            phone_number= buyer.phone_number,
            order_status = "Completed",
            order_time = "2023-06-24 10:00:00"
         )
         db.session.add(new_order)
         db.session.commit()
        
         new_order_item= Order_Item(
           order_number = new_order.order_number,
           branch_name  = selected_store.branch_name,
           product_code  = selected_leftover_product.product_code,
           item_price  = selected_leftover_product.quantity_in_stock*selected_leftover_product.price,
           quantity_ordered = selected_leftover_product.quantity_in_stock
         ) 
         db.session.add(new_order_item)
         db.session.commit()

         selected_leftover_product.quantity_in_stock = 0
         db.session.commit()
       return redirect(url_for('purchase'))
    else :    
       return redirect(url_for('purchase'))
if __name__ == '__main__':
    app.run()
