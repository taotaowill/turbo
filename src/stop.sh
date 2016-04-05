#!bin/bash

MASTER_PID=`ps xf | grep "python master/master.py" | awk '{print $1}'`
WORKER_PID=`ps xf | grep "python worker/worker.py" | awk '{print $1}'`
kill -9 $MASTER_PID
kill -9 $WORKER_PID

