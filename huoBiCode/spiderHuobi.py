from multiprocessing import Process
import time
import random

class Piao(Process):
    def __init__(self,name):
        self.name=name
        super().__init__()
    def run(self):
        print('%s is piaoing' %self.name)
        time.sleep(1)
        print('%s is piao end' %self.name)


p=Piao('egon')
p.daemon=True
p.start()
#等待p停止,等0.0001秒就不再等了
print('开始')