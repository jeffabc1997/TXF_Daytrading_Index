# import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import time
from tick_to_min import retrieve_data
import datetime

def show_plot(data_src: str = 'real-time', date: str = 'today'):
    now_time = datetime.datetime.now()
    if data_src == 'real-time' and now_time.time() > datetime.time(13, 45): # 收盤後從弄好的csv檔讀取
            data_src = 'history'
    if date == 'today':
        date = datetime.datetime.now().strftime('%Y-%m-%d')


    st.set_page_config(
        page_title="Market Trading Index",
        page_icon="✅",
        layout="wide",)
    st.title("能量圖")
    placeholder = st.empty()

    while(True):
        with placeholder.container():
            try:
                data = retrieve_data(data_src, date)
            except:
                print("no data")
            
            try:
                
                # guadan = guadan_energy_k()
                guadan = data[0]
                # print(guadan.head())
                guadan.rename(columns={ 'bid_ask_diffTtl': '大戶掛單', 'totalDealDiff': '散戶成交'}, inplace=True)
                st.markdown("## 大戶能量/散戶指標")
                st.line_chart(
                    data = guadan[['散戶成交','大戶掛單']], 
                    color = ["#0860F5", "#32C632"]) # Color Order should be checked           
            except:
                print("no 大戶能量")
                time.sleep(6)

            try:
                # bigsmallforce = bigforce_k()
                bigsmallforce = data[1]
                bigsmallforce.rename(columns={'largeSum':'大戶', 'smallSum': '散戶', 'cumulate': "總和"}, inplace=True)
                st.markdown("## 大戶力道")
                st.line_chart(
                    data = bigsmallforce[['大戶', '散戶','總和']], 
                    color = ["#0860F5", "#32C632", "#E60014"] # Color Order should be checked
                ) 
                # st.markdown("## TXF")
                # st.line_chart(
                #     data = dftick[['close']].resample('T').mean()
                # ) 
            except:
                print("no 力道")
                time.sleep(5)

            time.sleep(30)

if __name__ == '__main__':
    show_plot('real-time', 'today')
