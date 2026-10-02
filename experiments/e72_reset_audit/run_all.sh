#!/bin/bash
# E72 audit of all available checkpoints, CPU, two chains in parallel. setsid nohup experiments/e72_reset_audit/run_all.sh > logs_e72.log 2>&1 < /dev/null &
cd /media/hdd8/justin/my_project/CVPR20
R=experiments/e72_reset_audit
chain() { for M in "$@"; do set -- $M; [ -s $R/audit-$( [ $1 = rvt ] && echo rvt-$2 || { [ $1 = ssm ] && echo s5vit-$2 || echo evrtdetr-$2; } ).json ] && continue
  for t in 1 2 3; do CPUS=8 $R/run_audit_cpu.sh $1 $2 3 3 > $R/log-$1-$2.txt 2>&1 && break; done; done; }
chain "evrt r18" "rvt t" "rvt b" &
chain "ssm small" "ssm base" "rvt s" &
wait; echo E72_ALL_DONE
