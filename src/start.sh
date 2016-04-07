#!bin/bash

# stop
MASTER_PID=`ps xf | grep "python master/master.py" | grep -v grep | awk '{print $1}'`
WORKER_PID=`ps xf | grep "python worker/worker.py" | grep -v grep | awk '{print $1}'`
if [ -n "$MASTER_PID" ]; then
    kill -9 $MASTER_PID
fi
if [ -n "$WOKER_PID" ]; then
    kill -9 $WORKER_PID
fi
# start
export PYTHONPATH=./:$PYTHONPATH
nohup python master/master.py >/dev/null 2>master.err &
sleep 1
nohup python worker/worker.py >/dev/null 2>worker.err &

