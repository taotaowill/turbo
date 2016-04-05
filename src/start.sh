#!bin/bash

MASTER_PID=`ps xf | grep "python master/master.py" | awk '{print $1}'`
WORKER_PID=`ps xf | grep "python worker/worker.py" | awk '{print $1}'`
kill -9 $MASTER_PID
kill -9 $WORKER_PID

export PYTHONPATH=./:$PYTHONPATH
nohup python master/master.py >/dev/null 2>master.err &
sleep 1
nohup python worker/worker.py >/dev/null 2>worker.err &

