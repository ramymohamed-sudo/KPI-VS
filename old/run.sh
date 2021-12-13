#!/bin/bash

nohup python ./start_stop_exp.py &
nohup python ./send_kpis.py &
echo lastLine
