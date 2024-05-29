import shioaji as sj
from shioaji import BidAskFOPv1, Exchange
from shioaji import TickFOPv1, Exchange
from csv import DictWriter
import time # to simulate a real time data, time loop
import datetime
from tick_to_min import guadan_energy_k, bigforce_k
# import pandas as pd

def read_secret_key(pathname: str):
    with open(pathname, 'r') as fd:
        password = fd.read().splitlines()
        fd.close()
    return password

def writehead(filepath, field):
    with open(filepath, 'w') as fd:
        for i in range(len(field)-1):
            fd.write(field[i] + ",")

        fd.write(field[len(field)-1] +'\n')
        fd.close()

def init():
    sanhuField = ['datetime', 'totalDealDiff']
    guadanField = ['datetime', 'bid_ask_diffTtl']
    forceField = ['datetime', 'largeSum', 'smallSum', 'cumulate']
    tickpath = "./sanhu_deal_data.csv"
    test_forcepath = "./dahu_force_data.csv"
    test_bidpath = "./dahu_guadan_data.csv"

    writehead(test_bidpath, guadanField)
    writehead(tickpath, sanhuField)
    writehead(test_forcepath, forceField)

large_threshold = 11
small_threshold = 5
large_scale = 7
small_scale = 1
Forces = [0, 0, 0]
def large_label(x):
    if (x['volume'] >= large_threshold and x['tick_type'] == 1):
        return large_scale
    elif (x['volume'] >= large_threshold and x['tick_type'] == 2):
        return -large_scale
    else:
        return 0

def small_label(x):
    if (x['volume'] <= small_threshold and x['tick_type'] == 1):
        return small_scale
    elif (x['volume'] <= small_threshold and x['tick_type'] == 2):
        return -small_scale
    else:
        return 0
    
Last_bid = [0,0,0,0,0]
Last_ask = [0,0,0,0,0]
Empty_bidask = [0,0,0,0,0]
Sum_bidask = 0
def reset_global():
    global Last_ask, Last_bid, Sum_bidask, Forces
    Last_bid = [0,0,0,0,0]
    Last_ask = [0,0,0,0,0]
    Sum_bidask = 0
    Forces = [0, 0, 0]
def main():
    
    begin_time =datetime.time(8, 45)
    end_time = datetime.time(13, 45)
    while not (datetime.datetime.now().time() > begin_time and datetime.datetime.now().time() <= end_time):
        time.sleep(3)
    print("START WORKING")
    # 建立 Shioaji api 物件
    api = sj.Shioaji()

    # 登入帳號
    password = read_secret_key('password.txt') # 請修改此處
    api_key= password[0] # Your own key
    secret_key= password[1] # Your own key

    accounts = api.login(api_key=api_key, secret_key=secret_key)
    contract = min(
        [x for x in api.Contracts.Futures.TXF
            if x.code[-2:] not in ["R1", "R2"]
        ], key=lambda x: x.delivery_date
    )   
    sanhuField = ['datetime', 'totalDealDiff']
    guadanField = ['datetime', 'bid_ask_diffTtl']
    forceField = ['datetime', 'largeSum', 'smallSum', 'cumulate']
    tickpath = "./sanhu_deal_data.csv"
    test_forcepath = "./dahu_force_data.csv"
    test_bidpath = "./dahu_guadan_data.csv"

    # TICK 資料
    def quote_callback(self, exchange:Exchange, tick:TickFOPv1):
        global Forces
        appendTick = tick.to_dict()
        appendTick['datetime'] = appendTick['datetime'].strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # 累計賣盤成交-買盤成交 (散戶成交)
        with open(tickpath,'a', newline="") as fd:
            sanhu = appendTick['ask_side_total_vol'] - appendTick['bid_side_total_vol']
            theTick = {'datetime': appendTick['datetime'], 'totalDealDiff': sanhu} 
            dict_object = DictWriter(fd, fieldnames=sanhuField)
            dict_object.writerow(theTick) # 寫入散戶成交
            fd.close()
        large_force = large_label(appendTick)
        small_force = small_label(appendTick)
        cumu = large_force + small_force
        # 大戶力道
        with open(test_forcepath,'a', newline="") as fd:
            Forces[0] += large_force
            Forces[1] += small_force
            Forces[2] += cumu
            dict_object = DictWriter(fd, fieldnames=forceField)
            force_tick = {'datetime':appendTick['datetime'], 'largeSum':Forces[0], 'smallSum':Forces[1], 'cumulate':Forces[2]}
            dict_object.writerow(force_tick) # 寫入三個大戶力道的總和，即時
            fd.close()
    # 5檔報價
    def quote_callback2(self, exchange:Exchange, bidask:BidAskFOPv1):
        global Last_ask, Last_bid, Sum_bidask
        if bidask.diff_bid_vol == Last_bid:
            bidask.diff_bid_vol = Empty_bidask[:] # we don't count the same list, so make it 0s
        else:
            Last_bid = bidask.diff_bid_vol[:] # if not equals, then we copy to be the previous one

        if bidask.diff_ask_vol == Last_ask:
            bidask.diff_ask_vol = Empty_bidask[:]
        else:
            Last_ask = bidask.diff_ask_vol[:]
        ### Threshold should be kept for better memory usage
        if (sum(bidask.diff_bid_vol) == 0) and (sum(bidask.diff_ask_vol) == 0):
            return
        appendBidask = bidask.to_dict()
        appendBidask['datetime'] = appendBidask['datetime'].strftime("%Y-%m-%d %H:%M:%S.%f")
        guadan = sum(appendBidask['diff_bid_vol']) - sum(appendBidask['diff_ask_vol']) # 當下的,還需要組成分k後cumsum()
        # theBidask = {'datetime': appendBidask['datetime'], 'bid_ask_diffTtl': guadan} 
        # 當根委買-委賣 (大戶掛單)
        Sum_bidask += guadan # 可以視為即時的
        with open(test_bidpath,'a', newline="") as fd:   # 寫入大戶掛單sum(最理想的狀態)
            dict_object = DictWriter(fd, fieldnames= guadanField)
            dict_object.writerow({'datetime': appendBidask['datetime'], 'bid_ask_diffTtl': Sum_bidask})
            fd.close()

    # TICK 資料
    api.quote.subscribe(
        contract,
        quote_type = sj.constant.QuoteType.Tick,
        version = sj.constant.QuoteVersion.v1,
    )
    # 5檔報價
    api.quote.subscribe(
        contract,
        quote_type = sj.constant.QuoteType.BidAsk,
        version = sj.constant.QuoteVersion.v1
    )
    api.quote.set_on_tick_fop_v1_callback(quote_callback, bind = True)
    api.quote.set_on_bidask_fop_v1_callback(quote_callback2, bind = True)

    while(datetime.datetime.now().time() <= end_time): # main function 一定要sleep, 不然api會直接結束
        time.sleep(3)
    
    api.quote.unsubscribe(contract, quote_type='tick')
    api.quote.unsubscribe(contract, quote_type='bidask')
    print("FINISH API. ", datetime.datetime.today())
    api.logout()

if __name__ == '__main__':
    
    while(1):
        reset_global()
        begin_time =datetime.time(8, 45)
        end_time = datetime.time(13, 45)
        print("SLEEPING")
        while not (datetime.datetime.now().time() > begin_time and datetime.datetime.now().time() <= end_time) \
        and datetime.datetime.now().weekday() < 6:
            time.sleep(3)
        init()
        main()
        bigforce_k().to_csv("deals.csv", mode='a', header=False)
        guadan_energy_k().to_csv("pending_order.csv", mode='a', header=False)
        # time.sleep(3600)