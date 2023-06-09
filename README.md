111/2 資料庫系統 期末專題
# 惜食平台
隨著對資源永續的意識提高，減少食物浪費的重要性日益凸顯。我們的惜食平台，讓連鎖店家能夠透過促銷方式，出清即期存貨，同時建立品牌綠色形象，買家
也能夠以實惠的價格，購買物超所值的商品。目前，此平台主要支持單一連鎖店使用。

# 安裝指南
#### 移動到目標資料夾
```
cd 路徑
```
#### 下載程式碼
```
git clone https://github.com/109703043/BreadMaster
```
#### 啟動後端
1. 開啟MySQL workbench  
2. 於VSCode等編譯環境開啟目標資料夾  
3. 安裝封包，於Terminal輸入  
```
pip install Flask, requests, flask-sqlalchemy, pymysql, mysqlclient 
```
4. 更改control.py中的host, port, user, password(Line 16, Line 22-25)並執行  
```
python control.py
```
若出現以下訊息表示成功，可於MySQL workbench看見名為breadmaster的schema，內含8個table
```
資料庫 'BreadMaster' 建立成功  
 * Serving Flask app 'control'  
 * Debug mode: on  
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.  
 * Running on http://127.0.0.1:5000  
Press CTRL+C to quit  
 * Restarting with stat  
資料庫 'BreadMaster' 建立成功  
 * Debugger is active!  
 * Debugger PIN: 107-444-901  
```

#### 輸入測試資料
於MySQL workbench開啟目標資料夾中的breadmaster_TableValue.sql並執行，完畢後讓MySQL workbench保持開啟狀態  

#### 開啟前端
開啟瀏覽器造訪http://127.0.0.1:5000 便可於上面進行操作系統功能  

# 系統功能一覽
![惜食平台系統功能一覽png](https://github.com/109703043/BreadMaster/assets/132145188/54b0505e-e5af-4a75-8e6f-fc383254e961)

# 系統架構
#### 前端程式語言
html  
#### 後端程式語言
python  
#### DBMS
MySQL  
#### 工具、系統模組 
pip install 的 packages 列表: Flask, requests, flask-sqlalchemy, pymysql, mysqlclient
![惜食平台圖檔](https://github.com/109703043/BreadMaster/assets/132145188/cb5ecd41-bbbc-45c0-af1e-f352db5843ca)

# ER Model
![惜食平台_ER Model](https://github.com/109703043/BreadMaster/assets/132145188/c5492a1a-05e6-4554-8425-ea396f99af12)

# Relational Schema
![惜食平台_Relational Schema設計報告_page-0001](https://github.com/109703043/BreadMaster/assets/132145188/8d914165-3bd1-4d8d-8ce9-2b7fca3193bc)


