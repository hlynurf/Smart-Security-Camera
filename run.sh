#!/bin/bash

set -e

export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1

python main.py
