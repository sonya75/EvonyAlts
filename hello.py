import os
os.system("sudo mount -o remount,rw /")
os.system("wget https://www.torproject.org/dist/tor-0.2.9.8.tar.gz")
os.system("tar xzf tor-0.2.9.8.tar.gz; cd tor-0.2.9.8")
os.system("./configure && make")
