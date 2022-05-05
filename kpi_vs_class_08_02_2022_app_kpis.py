import websocket
# import json
# import sys
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, date
import sys
import requests
import pprint
import os
# import math
import csv
import websocketToBasestation

# here, we need active data from the sensors - 
sens_features = {"name": "cycle2-09",
                 "batt_lvl": 71,
                 "hrs_since_ful_chrg": 0.17349416666666664,
                 "chrg_status": "NOT_PRESENT",
                 "timestamp_ms": 1644581257627,
                 "tx_pwr": 1.0,
                 "iot_mode": "m",
                 "cpu_temp": 63.7,
                 "cpu_util": "2.6",
                 "ram_util": 120.4,
                 "disk_perc": 8.0,
                 "wifi": True,
                 "chrg_cycle":1}

# df_sens_features = pd.DataFrame(sens_features, index=[0])
# print(df_sens_features.head())


class KpiVsObject():
    def __init__(self, selectSetOfKpis, netw=True, ue_index=0):
        self.startDate = date.today()
        self.now = datetime.now()
        self.startTime = self.now.strftime("%H:%M:%S")
        self.startDatetime = self.now.strftime("%Y-%m-%d %H:%M:%S")
        self.kpiVsAuthorize = 'Basic bGwzdWM0RGF0YUNvbGxlY3RvclVzZXI6bGwzdWM0RGF0YUNvbGxlY3RvclVzZXI='
        self.kpiVsUrl = 'https://ingress.kpivs-5gsolutions.eu/5gsolutions/data-collector/'
        self.selectSetOfKpis = selectSetOfKpis
        self.netw = netw
        self.code = 'start'
        self.ll_id = 3
        self.uc_id = 4
        self.time_diff_to_greece = 1*60*60  # 2 or 1 ?
        self.hours_added = timedelta(hours=1)  # for CET time
        self.ue_index = ue_index  # check manually if it is 0 or 1 for SA/NSA
        self.kpiFileName = str(self.startDate)+'.csv'
        # self.millis =
        # datfr = pd.read_csv('netw_kpis1.csv')

    """ Notification to KPI-VS with the start/stop of experiment """
    def start_stop_exp(self):
        # self.millis = int(round((time.time() + (self.time_diff_to_greece)) * 1000))
        self.millis = round(time.time() * 1000)
        print("code is: ", self.code, "self.millis", self.millis)
        json = {
            "ll_id": self.ll_id,
            "uc_id": self.uc_id,
            "timestamp": self.millis,
            "status": self.code,  # need to invert to stop when leaves this fn
            "test_case_id":  1,
            "tuid":  ""}
        r = requests.post(self.kpiVsUrl+'notification',json=json,headers={'Authorization': self.kpiVsAuthorize})
        # x = r.json()
        pprint.pprint(r.json())

    def send_KPIs(self):
        file = {'file': open(self.kpiFileName, 'rb')}
        
        if self.netw:
            local_url = self.kpiVsUrl+'livinglab/LL3/usecase/UC4/uploadNet'
            print("The network file is being sent now ....")
        else:
            local_url = self.kpiVsUrl+'livinglab/LL3/usecase/UC4/upload'
            print("The application file is being sent now ....")

        r = requests.post(
            local_url,
            files=file,
            headers={'Authorization': self.kpiVsAuthorize}
            )
        # x = r.json()
        pprint.pprint(r.json())

    def rest_api_attributes(self):
        pass

    def collect_netw_kpi_from_BS(self):
        pass

    def send_kpi_to_KpiVs(self):
        pass


    def parseData(self, df_from_ws_jsonData='', df_from_sensor=''):
        current_date_and_time_CET = datetime.now() + self.hours_added
        kpis_row_to_csv_file = dict()
        kpis_row_to_csv_file['Timestamp'] = current_date_and_time_CET.strftime("%Y-%m-%d %H:%M:%S")
        kpis = self.selectSetOfKpis[:]

        if self.netw:
            # nework KPIs parsing
            df = df_from_ws_jsonData
            dfUeList = df.from_dict(df.iloc[0:2]['ue_list'])
            kpiFromBsForUe = dfUeList.iloc[self.ue_index]['ue_list']  # iloc[1] for the ue_2, i.e., 5G
            kpiFromBsForUe.update(kpiFromBsForUe['cells'][0])
            del kpiFromBsForUe['cells']

            kpis_row_to_csv_file['UE ID'] = kpiFromBsForUe['enb_ue_id'] if kpiFromBsForUe.get('enb_ue_id',0) else kpiFromBsForUe['ran_ue_id']
            kpis_row_to_csv_file['Status'] = 'Active'
            kpis_row_to_csv_file['Cell ID'] = kpiFromBsForUe['cell_id']
            kpis_row_to_csv_file['Downlink bitrate'] = kpiFromBsForUe['dl_bitrate']/(10**3)  # kbps not Mbps
            kpis_row_to_csv_file['Uplink bitrate'] = kpiFromBsForUe['ul_bitrate']/(10**3)   # kbps not Mbps
            kpis_row_to_csv_file['PUCCH SNR'] = kpiFromBsForUe['pucch1_snr'] if kpiFromBsForUe.get('pucch1_snr',0) else kpiFromBsForUe['pusch_snr']
            kpis_row_to_csv_file['Downlink MCS'] = kpiFromBsForUe['dl_mcs'] if kpiFromBsForUe.get('dl_mcs',0) else np.nan
            kpis_row_to_csv_file['Uplink MCS'] = kpiFromBsForUe['ul_mcs'] if kpiFromBsForUe.get('ul_mcs',0) else np.nan

            print("kpis_row_to_csv_file \n", kpis_row_to_csv_file)

            # kpiFromBsForUe['Cell ID'] = kpiFromBsForUe.pop('cell_id')
            # kpiFromBsForUe['Downlink bitrate'] = kpiFromBsForUe.pop('dl_bitrate')
            # kpiFromBsForUe['Uplink bitrate'] = kpiFromBsForUe.pop('ul_bitrate')
            # kpiFromBsForUe['PUCCH SNR'] = kpiFromBsForUe.pop('pucch1_snr')
            # kpiFromBsForUe['Downlink MCS'] = kpiFromBsForUe.pop('dl_mcs')
            # kpiFromBsForUe['Uplink MCS'] = kpiFromBsForUe.pop('ul_mcs')
            print("self.kpiFileName", self.kpiFileName)
        
        else:
            # application KPIs parsing
            df = df_from_sensor     # To be replaced with dataframe of application KPIs
            kpis_row_to_csv_file['UE ID'] = self.ue_index
            kpis_row_to_csv_file['Battery level'] = 90.0    # Float
            kpis_row_to_csv_file['Expected lifespan'] = "Long"    # String
            time_next_servc = datetime.now() + timedelta(hours=24)
            kpis_row_to_csv_file['Next servicing needed by'] = time_next_servc     # Date
            kpis_row_to_csv_file['Positioning accuracy'] =  1.3     # Float
            kpis_row_to_csv_file['Service availability'] = 99.1     # Float
            # sens_features should be calculated/updated here before added to the kpis_row_to_csv_file
            # maybe another subscriber collect data 
            kpis_row_to_csv_file.update(sens_features) 

            def map_sens_id_netw_to_app_kpi(self):
                pass


        if not os.path.exists(self.kpiFileName):
            print("File does not exists:")
            with open(self.kpiFileName, 'x') as create_kpi_file:
                kpi_writer = csv.writer(create_kpi_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                kpi_writer.writerow(kpis)
                kpi_writer.writerow(kpis_row_to_csv_file.values())
                print("kpis_row_to_csv_file.keys()", kpis_row_to_csv_file.keys())
        else:
            print("File exists")
            with open(self.kpiFileName, mode='a+') as kpi_file:
                kpi_writer = csv.writer(kpi_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                kpi_writer.writerow(kpis_row_to_csv_file.values())
                print("kpis_row_to_csv_file.keys()", kpis_row_to_csv_file.keys())


ws = websocket.WebSocketApp(
    url=websocketToBasestation.webSocketUri,
    on_message=websocketToBasestation.on_message,
    on_error=websocketToBasestation.on_error,
    on_close=websocketToBasestation.on_close,
    on_open=websocketToBasestation.on_open
        )
# websocket.enableTrace(True)
netw_kpis = ["Timestamp", "UE ID", "Status", "Cell ID", "Downlink bitrate",
        "Uplink bitrate", "PUCCH SNR", "Downlink MCS", "Uplink MCS"]
app_kpis = ["Timestamp", "UE ID","Battery level", "Expected lifespan",
            "Next servicing needed by", "Positioning accuracy", "Service availability"]

app_kpis = app_kpis + list(sens_features.keys())

netw = False
# kpi_vs = KpiVsObject(netw_kpis, netw=netw)
kpi_vs = KpiVsObject(app_kpis, netw=False, ue_index=0)


def main():
    # initializedData()
    # ws = websocket.WebSocketApp(webSocketUri,on_message = on_message,
    #     on_error = on_error,
    #     on_close = on_close)
    # ws.on_open = on_open
    max_no_of_iter = 30   # 30 iterations (5 mins - one every 10 sec)
    i= 1

    if netw:
        """ Collecting network KPIs from the BS
        o/p is appended to the dataframe """
        while i <= max_no_of_iter:  # datetime.now() < future_datetime_after_3_mins:
            print(f"++++++++++++++++++++++ collecting network data for iter no {i}")
            ws.run_forever()
            df = websocketToBasestation.df
            # check first df is non-empty - otherwise wait 10 sec
            if not df.empty:
                kpi_vs.parseData(df_from_ws_jsonData=df)
            if i <= max_no_of_iter-1:
                time.sleep(10)  # 10 seconds
            i += 1
        
    else:
        """ Collecting application KPIs from the sensors """
        while i <= max_no_of_iter:
            print(f"++++++++++++++++++++++collecting application data for iter no {i}")
            df = pd.DataFrame([1, 2, 3])    # to be updated
            # check first df is non-empty - otherwise wait 10 sec
            if not df.empty:
                kpi_vs.parseData(df_from_ws_jsonData=df)
            if i <= max_no_of_iter-1:
                time.sleep(10)  # 10 seconds
            i += 1


conn_open = False
if __name__ == "__main__":
    if conn_open:
        kpi_vs.code = 'stop'
        kpi_vs.start_stop_exp()
    else:
        print("Now the test is started ....")
        kpi_vs.start_stop_exp()
        kpi_vs.code = 'stop'
        mainiIter = 1
        while mainiIter < 2:        # was 13    # to be while 1
            print("Main iteration loop number {}".format(mainiIter))
            if os.path.exists(kpi_vs.kpiFileName):
                os.remove(kpi_vs.kpiFileName)

            main()

            if os.path.exists(kpi_vs.kpiFileName):
                kpi_vs.send_KPIs()
                pass
            mainiIter += 1
        print("The test is now terminated <<<<<<<<<<")
        kpi_vs.start_stop_exp()

