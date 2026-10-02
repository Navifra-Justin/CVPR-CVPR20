#!/bin/bash
# waits for the five E71 dumps, then runs the evaluation (CPU, nice 19). setsid nohup ./run_e71_final.sh > logs_e71_final.log 2>&1 < /dev/null &
cd /media/hdd8/justin/my_project/CVPR20
for m in rvt-t rvt-s rvt-b s5vit-small s5vit-base; do
  until [ -s experiments/e71_h4080/dets-$m.npz ]; do sleep 120; done
done
nice -n 19 env B=200 python3 src/e71_eval.py | tee experiments/e71_h4080/eval.log
echo E71_EVAL_DONE
