
import websocket
import json
import sys
import pandas as pd
from time import sleep
from datetime import datetime, timedelta, date
import sys
import requests
import pprint
import os.path
from os import path
import math
import csv


""" timestamp column - issues 1- snr in cell 1 only not 2  2- ul_mcs in cell 2 only and sometimes it did not appear ?
3- revise why the old code was always giving ul-mcs and dl-mcs ??> (which cell - maybe use js?) (maybe bkz the router
was in use not the samsung phone )"""

startDate = date.today()
now = datetime.now()
startTime = now.strftime("%H:%M:%S")
startDatetime = now.strftime("%Y-%m-%d %H:%M:%S")
isFirstRun= True
webSocketUri = "ws://9.161.154.25:9001/"
msg = '{"message": "ue_get","stats":true}'    # ""                msg = '{"message": "stats"}'  ,"stats": true
isDataReceived =  False
kpiVsAuthorize = 'Basic bGwzdWM0RGF0YUNvbGxlY3RvclVzZXI6bGwzdWM0RGF0YUNvbGxlY3RvclVzZXI='
kpiVsUrl = 'https://ingress.kpivs-5gsolutions.eu/5gsolutions/data-collector/'
selecSetOfKpis = ['Timestamp','ue_id','Status','cell_id','dl_bitrate','ul_bitrate',
                    'pucch1_snr','dl_mcs','ul_mcs']      # ran_ue_id for 5G     'ue_id'    'test',  'mssjjjs'
# datfr = pd.read_csv('netw_kpis1.csv')

""" Notification to KPI-VS with the start/stop of experiment"""
def start_stop_exp(code):
    global isFirstRun
    # code ="start" if isFirstRun else "stop"   """ code not used"""
    json = {
        "ll_id": 3,
        "uc_id": 4,
        "timestamp": 0,
        "status": code,
        "test_case_id":  1,
        "tuid":  ""}
    r = requests.post(kpiVsUrl+'notification',json=json,headers={'Authorization': kpiVsAuthorize})
    x = r.json()
    pprint.pprint(r.json())
    isFirstRun = False

""" Send the KPI data """
def send_KPIs():
    # file = {'file':open(fileName,'rb')}
    file = {'file':open('2020-11-30.csv','rb')}
    r = requests.post(kpiVsUrl+'livinglab/LL3/usecase/UC4/uploadNet',
           files=file,
           headers={'Authorization': kpiVsAuthorize})
    x = r.json()
    pprint.pprint(r.json())

""" TBD Later: send batch file to the BS - 1- authenticate 2- Service lte start ????? - for this, the NAN values
in the pandas/csv file will be pre-processed before sending to the KPI server"""

def initializedData():   # """ i think it is not needed as you type them static """
     if len(sys.argv) >= 2:
         print("arg",sys.argv[1])
         global msg
         global webSocketUri
         webSocketUri = sys.argv[1]
         msg = sys.argv[2]
         print("input",msg)

def on_message(ws, message):
    global isDataReceived
    if isDataReceived==True:
        receivedData = json.loads(message)
        parseData(receivedData)
        ws.close()
    if isDataReceived==False:
        isDataReceived = True
        msg = '{"message":"ue_get","stats":true}'     # '{"message": "ue_get",}'  #   '{"message": "stats", "message_id": "id#1" }'
        ws.send(msg)

def parseData(jsonData,kpis=selecSetOfKpis):        #
    # print("0-received data in parseData method:\n",jsonData)
    df = pd.DataFrame.from_dict(jsonData)
    dfUeList = df.from_dict(df.iloc[0:2]['ue_list'])          # df_rf_cpu.head()       we need index 0
    ue_index_from_0_to_ = 0     #"""was 1 for RAN __________________________ """
    kpiFromBsForUe = dfUeList.iloc[ue_index_from_0_to_]['ue_list']           # iloc[1] for the ue_2, i.e., 5G
    # print("kpiFromBsForUe['cells'][1].keys()",kpiFromBsForUe['cells'][1].keys())

    for key in kpiFromBsForUe['cells'][0].keys():
         kpiFromBsForUe[key] = kpiFromBsForUe['cells'][0][key]
    del kpiFromBsForUe['cells']

    hours_added = timedelta(hours = 1)  # for CET time
    current_date_and_time_CET = datetime.now() + hours_added
    kpiFromBsForUe['Timestamp']  = current_date_and_time_CET.strftime("%Y-%m-%d %H:%M:%S")
    kpiFromBsForUe['Status']  = 'Active'
    kpiFromBsForUe['ue_id'] = kpiFromBsForUe.pop('enb_ue_id') if kpiFromBsForUe.get('enb_ue_id',0) else kpiFromBsForUe.pop('ran_ue_id')
    kpiFromBsForUe['dl_bitrate'] = kpiFromBsForUe['dl_bitrate']/(10**6)           # rate from bps to Mbps
    kpiFromBsForUe['ul_bitrate'] = kpiFromBsForUe['ul_bitrate']/(10**6)

    kpisCopy = kpis.copy()
    [ kpis.remove(key) for key in kpisCopy if key not in kpiFromBsForUe.keys() ]      #       """ - error here """
    # print(".....kpis",kpis)

    slected_kpis_from_BS_dict_ue_row = [ kpiFromBsForUe[key] for key in  kpis if key in kpiFromBsForUe.keys()]   # kpiFromBsForUe.keys()
    print("Selected kpis to be sent to the KPI-VS are:\n",slected_kpis_from_BS_dict_ue_row)


    kpiFileName = str(startDate)+'.csv'
    if not path.exists(kpiFileName):      # guru99.csv
        print("File does not exists:")
        with open(kpiFileName, 'x') as create_kpi_file:
            kpi_writer = csv.writer(create_kpi_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            kpisNamed = ['Timestamp','UE ID','Status','Cell ID','Downlink bitrate','Uplink bitrate','PUCCH SNR','Downlink MCS','Uplink MCS']
            kpi_writer.writerow(kpis)  #
    else:
        print("File exists")
        with open(kpiFileName, mode='a+') as kpi_file:
            kpi_writer = csv.writer(kpi_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            kpi_writer.writerow(slected_kpis_from_BS_dict_ue_row)

def on_error(ws, error):
 print (error)

def on_close(ws):
 print ("\n### ---------closed ###")

def on_open(ws):
    print ("### opened ###")
    global msg
    ws.send(msg)

def main():
    # turn_on_off_BS(code)  # maybe wait sometime till the UEs are attached to the BS
    initializedData()
    ws = websocket.WebSocketApp(webSocketUri,on_message = on_message,
        on_error = on_error,
        on_close = on_close)
    ws.on_open = on_open

    """ Collecting KPIs from the BS -       o/p is appended to the dataframe """
    future_datetime_after_3_mins = datetime.now() + timedelta(seconds = 6)
    i=1
    while datetime.now() < future_datetime_after_3_mins:
        print(f"collecting date for iter no {i}")
        # ws.on_open = on_open
        ws.run_forever()
        # # df = ws.on_message()
        i+=1
        sleep(2)

if __name__ == "__main__":
    # print("main")
    print("Now the test is started")
    start_stop_exp(code='start')
    main()
    print("-- and now the file is being sent . . . .")
    send_KPIs()
    print("The test is now terminated")
    start_stop_exp(code='stop')



#

