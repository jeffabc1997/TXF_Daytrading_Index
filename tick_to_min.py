import pandas as pd

def bigforce_k(): # 大戶力道
    test_forcepath = "./dahu_force_data.csv"
    bigforce = pd.read_csv(test_forcepath)
    bigforce['datetime'] = pd.to_datetime(bigforce['datetime'])
    bigforce.set_index("datetime", inplace=True)

    result = bigforce[['largeSum', 'smallSum', 'cumulate']].resample('1min').last()# 取每分鐘的最後一個data 即可
    return result
    

def dahu_guadan_k(): # 大戶掛單
    test_bidpath = "./dahu_guadan_data.csv"
    guadan = pd.read_csv(test_bidpath)
    guadan['datetime'] = pd.to_datetime(guadan['datetime'])
    guadan.set_index("datetime", inplace=True)

    result = guadan[['bid_ask_diffTtl']].resample('1min').last()# 取每分鐘的最後一個data 即可
    return result

def sanhu_k(): # 散戶成交
    tickpath = "./sanhu_deal_data.csv"
    tickdf = pd.read_csv(tickpath)
    tickdf['datetime'] = pd.to_datetime(tickdf['datetime'])
    tickdf.set_index("datetime", inplace=True)

    sanhu = tickdf.resample('1min').last()
    return sanhu
    
def guadan_energy_k(): # 掛單能量(大戶掛單和散戶成交)
    
    sanhu = sanhu_k().reset_index()
    dahu = dahu_guadan_k().reset_index()
    result = pd.merge(dahu, sanhu, how='outer', on='datetime')
    result.set_index("datetime", inplace=True)
    return result
    
def retrieve_data(data_src: str, date: str):
    if data_src == 'real-time':
        return guadan_energy_k(), bigforce_k()
    elif data_src == 'history':
        guadan_energy = pd.read_csv("掛單能量.csv")
        guadan_energy['datetime'] = pd.to_datetime(guadan_energy['datetime'], format='mixed')
        guadan_energy.set_index("datetime", inplace=True)

        bigforce = pd.read_csv("大戶力道.csv")
        bigforce['datetime'] = pd.to_datetime(bigforce['datetime'], format='mixed')
        bigforce.set_index("datetime", inplace=True)
        
        return guadan_energy.loc[date], bigforce.loc[date]
    
if __name__ == '__main__':
    dfs = retrieve_data('history', '2024-03-13')
    # print(dfs[0])