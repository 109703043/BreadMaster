import os
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import model

app = Flask(__name__)
# <username>、<password>、<host>、<port>和<database>
app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:root@localhost:3306/breadmaster" # 改MySQL檔案路徑
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # 建立了物件之後，就會提供一個名為Model的類別，此類別可以用於宣告Model

@app.route('/form') #選擇觸發url的網址
def formPage():
    return render_template('form.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        user = request.form['user']
        print("post : user => ", user)
        return redirect(url_for('success', name=user, action="post"))
    else:
        user = request.args.get('user')
        print("get : user => ", user)
        return redirect(url_for('success', name=user, action="get"))

@app.route('/success/<action>/<name>')
def success(name, action):
    #model.add(name)
    return '{} : Welcome {} ~ !!!'.format(action, name)


if __name__ =="__main__":
    with app.app_context():
        db.create_all()
    app.run(#'0.0.0.0', 
                debug = True) #允許外部連線

#@app.route('/data/appInfo/<name>', methods=['GET']) #加入接收的參數
