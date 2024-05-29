# Log in API
這邊是使用永豐提供的API, 必須登入才能獲取即時資料
`app.py`
- You need to have your password in a password.txt (created by yourself)
- format (2 lines in the text file):
```
your api_key
your secret_key
```
# 建立存放指標的檔案
`python header.py`

# Run
```
python app.py
```
# Output
`app.py`
- main()會產生出3個tick等級的即時資料, 存在csv檔 (*_data.csv)
- 讀上述的3個csv檔的最後一筆資料即為最新的指標資訊
- 收盤後有兩個function把上述的3個csv檔轉成2個csv檔(分k)

# 即時圖表
用`streamlit run app_stream.py`可以看到當日即時的指標圖表

# 聲明
此程式產生之指標僅供研究期貨者參考, 並無推銷買賣進場之用途