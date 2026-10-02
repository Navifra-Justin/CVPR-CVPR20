#!/bin/bash
cd /media/hdd8/justin/my_project/CVPR20
D=experiments/e70_1mpx/gate; SL=experiments/e70_1mpx/gate/seqlist.txt
for SH in 0 2; do ./run_e70_arm.sh 0 ssm base - 0 $SH 1 $D $SL; done
for SH in 0 2; do ./run_e70_arm.sh 0 rvtc s carry 0 $SH 1 $D $SL; ./run_e70_arm.sh 0 rvtc s reset 1 $SH 1 $D $SL; done
echo GATE_DUMPS_END
