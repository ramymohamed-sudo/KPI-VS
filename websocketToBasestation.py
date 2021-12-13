
import websocket
import json
import sys
import pandas as pd
import time
from datetime import datetime, timedelta, date
import sys
import requests
import pprint
import os.path
from os import path
import math
import csv



webSocketUri = "ws://9.161.154.25:9001/"
msg = '{"message": "ue_get","stats":true}'    # "" msg = '{"message": "stats"}'  ,"stats": true
isDataReceived =  False
# df = pd.DataFrame()
# selecSetOfKpis = ['Timestamp','ue_id','Status','cell_id','dl_bitrate','ul_bitrate',
#                     'pucch1_snr','dl_mcs','ul_mcs']      # 'mssjjjs','hehw','whjjw' ran_ue_id for 5G     'ue_id'    'test',  'mssjjjs'



def initializedData():   # """ i think it is not needed as you type them static """
     if len(sys.argv) >= 2:
         print("arg",sys.argv[1])
         global msg
         global webSocketUri
         webSocketUri = sys.argv[1]
         msg = sys.argv[2]
         print("input",msg)

def handleData(jsonData):
    global df
    df = pd.DataFrame.from_dict(jsonData)



def on_message(ws, message):
    global isDataReceived
    if isDataReceived==True:
        receivedData = json.loads(message)
        handleData(jsonData=receivedData)
        ws.close()
    if isDataReceived==False:
        isDataReceived = True
        msg = '{"message":"ue_get","stats":true}'     # '{"message": "ue_get",}'  #   '{"message": "stats", "message_id": "id#1" }'
        ws.send(msg)


def on_error(ws, error):
 print (error)

def on_close(ws):
 print ("\n### ---------closed ###")

def on_open(ws):
    # print ("### opened ###")
    global msg
    # print("+++++++++ msg after global msg", msg)
    ws.send(msg)

# def main():
    # initializedData()
# websocket_object = websocket.WebSocketApp(webSocketUri,on_message = on_message,
#                     on_error = on_error,
#                     on_close = on_close)
# on_open = on_open

# websocket.enableTrace(True)    
ws = websocket.WebSocketApp(webSocketUri,on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open)


        

# if __name__ == "__main__":
#     print("Now the test is started ....")
#     start_stop_exp(code='start')
#     timeAfterOneHrs = datetime.now() + timedelta(seconds = testDuration)
#     mainiIter = 1
#     while datetime.now() < timeAfterOneHrs:
#     # maybe here delete the file after each main to send the new kpis
#         print("Main iteration loop number {}".format(mainiIter))
#         if path.exists(kpiFileName):      # guru99.csv      'kpifile.csv'
#             os.remove(kpiFileName)
#         main()
#         print(" >>>>>>>>>> Now, the data is being sent <<<<<<<<<<")
#         send_KPIs(fileName=kpiFileName)
#         mainiIter+=1

#     print("The test is now bing terminated <<<<<<<<<<")
#     start_stop_exp(code='stop')





