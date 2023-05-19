import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# from control import app, db

db = SQLAlchemy() # 建立了物件之後，就會提供一個名為Model的類別，此類別可以用於宣告Model

# 建立一個User類別，該類別繼承了db.Model，這個類別可以提供我們未來與資料庫進行溝通傳遞
class Users(db.Model):
    _id = db.Column('id', db.Integer, primary_key=True) # column：欄位
    name = db.Column('name', db.String(100))
    #email = db.Column(db.String(100))
    def __init__(self, name#, email
                            ):
        self.name =name
        #self.email = email
    def __repr__(self):
        return f'使用者名稱為 {self.name}'
    
class Buyer(db.Model):
    phone_number = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    late_record = db.Column(db.Integer, default=0)

class Store(db.Model):
    branch_name = db.Column(db.String(50), primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    business_hours = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)

class Leftover_Products(db.Model):
    __tablename__ = 'leftover_products'
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True, index = True)
    product_code = db.Column(db.String(20), nullable=False, primary_key=True, index = True)
    expiration_date = db.Column(db.Date, nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    
class Order(db.Model):
    order_number = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'), primary_key=True)
    order_status = db.Column(db.String(20), nullable=False)
    order_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

class Review(db.Model):
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(500), nullable=False)

class Frequently_Used_Store(db.Model):
    phone_number = db.Column(db.String(20), db.ForeignKey('buyer.phone_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)

class Order_Item(db.Model):
    order_number = db.Column(db.Integer, db.ForeignKey('order.order_number'), primary_key=True)
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    product_code = db.Column(db.String(20), db.ForeignKey('leftover_products.product_code'), primary_key=True)
    item_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)

class Leftover_History(db.Model):
    branch_name = db.Column(db.String(50), db.ForeignKey('store.branch_name'), primary_key=True)
    product_code = db.Column(db.String(20), db.ForeignKey('leftover_products.product_code'), primary_key=True)
    removal_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), primary_key=True)
    quantity_removed = db.Column(db.Integer, nullable=False)

tables = [Buyer, Store, Order, Leftover_Products, Order_Item, Leftover_History, Review, Frequently_Used_Store]

def add(name):
    # 1
    new_user = Users(name)
    # 2
    db.session.add(new_user)
    # 3
    db.session.commit()