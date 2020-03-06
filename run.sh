#!/bin/bash

set -e

export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1

sudo modprobe w1–gpio
sudo modprobe w1-therm

python main.py
