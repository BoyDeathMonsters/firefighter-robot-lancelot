#!/bin/bash

python3 /home/victor/Capteurs/lora_senderV4.py &
python3 /home/victor/Capteurs/Humidity.py &
wait
