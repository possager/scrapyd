from twisted.internet import reactor,protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.application.service import Service
import sqlalchemy


class spiderInfoColletorService(Service):
    name = "spider_info_collector"
    def __init__(self):
        self.spider_living = {}

    def startService(self):
        pass

    def stopService(self):
        pass


class spider_info:
    def __init__(self):
        self.spider_atived = []


    def install(self):
        pass



# class spiderInfoListener(protocol.Protocol):
#     def connectionMade(self):
        