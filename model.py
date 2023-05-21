import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # 建立了物件之後，就會提供一個名為Model的類別，此類別可以用於宣告Model


#__init__ 可以用來初始化Class類別；__repr__可以讓我們在使用print() 顯示我們希望Class出現的的資料。
#     def __init__(self, name#, email
#                             ):
#         self.name =name
#         #self.email = email
#     def __repr__(self):
#         return f'使用者名稱為 {self.name}'


# 建立一個類別，該類別繼承了db.Model，這個類別可以提供我們未來與資料庫進行溝通傳遞    
class Buyer(db.Model):
    __tablename__ = 'buyer'
    phone_number = db.Column(db.String(20), primary_key=True) # column：欄位
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
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'))#, primary_key=True)
    order_status = db.Column(db.String(20), nullable=False)
    order_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

class Leftover_Product(db.Model):
    __tablename__ = 'leftover_product'
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True, index = True)
    product_code = db.Column(db.String(20), primary_key=True, index = True)
    expiration_date = db.Column(db.Date, nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)

class Order_Item(db.Model):
    __tablename__ = 'order_item'
    order_number = db.Column(db.Integer, db.ForeignKey('order.order_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    product_code = db.Column(db.String(20), db.ForeignKey('leftover_product.product_code'), primary_key=True)
    item_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)

class Leftover_History(db.Model):
    __tablename__ = 'leftover_history'
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    product_code = db.Column(db.String(20), db.ForeignKey('leftover_product.product_code'), primary_key=True)
    removal_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), primary_key=True)
    quantity_removed = db.Column(db.Integer, nullable=False)

class Review(db.Model):
    __tablename__ = 'review'
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    score = db.Column(db.Integer)#, nullable=False)
    content = db.Column(db.String(500))#, nullable=False)

class Frequently_Used_Store(db.Model):
    __tablename__ = 'frequently_used_store'
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)