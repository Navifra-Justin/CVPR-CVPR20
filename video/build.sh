#!/bin/sh
# Encode each scene from its rendered frames, stretch it to its screen time, and concat.
# SRC: frame dir | output | slow-down factor (screen time = frames/30 * K)
set -e
cd "$(dirname "$0")"
enc() {  # $1 frames dir, $2 out, $3 K
  ffmpeg -y -loglevel error -framerate 30 -i "frames/$1/%04d.png" \
    -vf "setpts=$3*PTS" -r 30 -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p "$2"
}
enc v00 final/s0.mp4  1.0        # title
enc v02 final/s1.mp4  2.69       # predictor-side temporal support
enc v04 final/s2.mp4  2.611      # the mAP consequence, on one real frame
enc v08 final/s6.mp4  2.0        # the headline: mAP against chunk position
enc v01 final/s3.mp4  1.9        # events inside one published exposure
enc v07 final/s2b.mp4 12.857     # ceiling exposure against the daytime control
enc v05 final/s4.mp4  1.296      # the harmonic identification
enc v03 final/s1b.mp4 1.25       # five released checkpoints, one instrument
enc v06 final/s5.mp4  1.0        # closing
cat > final/list.txt <<EOF
file 's0.mp4'
file 's1.mp4'
file 's2.mp4'
file 's6.mp4'
file 's3.mp4'
file 's2b.mp4'
file 's4.mp4'
file 's1b.mp4'
file 's5.mp4'
EOF
ffmpeg -y -loglevel error -f concat -safe 0 -i final/list.txt -c copy CVPR20_paper_video.mp4
