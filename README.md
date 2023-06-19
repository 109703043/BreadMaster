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
#### 建立資料庫
開啟MySQL workbench，並於VSCode等編譯環境開啟BreadMaster資料夾，更改create_table.ipynb中的host, port, user, password並execute，即可於MySQL workbench看見breadmaster schema。
#### 輸入測試資料
於MySQL workbench執行breadmaster_TableValue.sql
#### 啟動後端
更改control.py中的host, port, user, password並執行  
```
python control.py
```
#### 開啟前端
開啟瀏覽器造訪http://127.0.0.1:5000 便可於上面進行操作  

# 系統架構
#### 前端程式語言
html  
#### 後端程式語言
python  
#### DBMS
MySQL  
#### 工具、系統模組 
pip install 的 packages 列表: Flask, requests, flask-sqlalchemy, pymysql  
![惜食平台圖檔](https://github.com/109703043/BreadMaster/assets/132145188/cb5ecd41-bbbc-45c0-af1e-f352db5843ca)


# ER Model
![惜食平台_ER Model](https://github.com/109703043/BreadMaster/assets/132145188/c5492a1a-05e6-4554-8425-ea396f99af12)

# Relational Schema
![惜食平台_Relational Schema設計報告_page-0001](https://github.com/109703043/BreadMaster/assets/132145188/8d914165-3bd1-4d8d-8ce9-2b7fca3193bc)


