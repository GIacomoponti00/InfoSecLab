import os
from time import sleep
from sys import argv

if len(argv) < 2 or (argv[1] != "1" and argv[1] != "2"):
    print("Usage : python run.py {1 or 2}")
    exit(1)

os.system("python -u dma_engine.py &")
sleep(0.1)
os.system("python -u hypervisor.py &")
sleep(0.1)
os.system("python -u gpu.py &")
sleep(0.1)
os.system("python -u guest.py "+argv[1])

os.system("pkill -f 'python -u dma_engine.py'")
os.system("pkill -f 'python -u gpu.py'")
os.system("pkill -f 'python -u hypervisor.py'")
