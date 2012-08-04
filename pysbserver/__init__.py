__version__ = "0.0.1"

import enet #@UnresolvedImport
import sys
import traceback

from Client import ClientBase, Client
from RoomManager import RoomManager

class Engine(object):
    clients = {}
    room_manager = None
    _running = False
    _enet_host = None
    
    def __init__(self, host, port, maxclients, maxdown, maxup):
        
        self.room_manager = RoomManager()
        Client.connected.connect(self.room_manager.on_client_connected)
        
        if port == "*":
            use_port = 0
        else:
            use_port = int(port)
            
        if host == "*":
            use_host = None
        else:
            use_host = host
            
        address = enet.Address(use_host, use_port)
        maxclients = int(maxclients)
        maxdown = int(maxdown)
        maxup = int(maxup)
            
        self._enet_host = enet.Host(address, maxclients, 3, maxdown, maxup)
        
        ClientBase.cn_pool.extend(list(range(maxclients)))
        
        self.clients = {}
        
        self._running = True
        
    def stop(self):
        self._running = False
        
    def getpeerid(self, event):
        return (event.peer.address.host, event.peer.address.port)
        
    def service_host(self):
        try:
            event = self._enet_host.service(5)
        except KeyboardInterrupt:
            raise
        
        if event.type == enet.EVENT_TYPE_CONNECT:
            print("%s: CONNECT" % event.peer.address)
            self.clients[self.getpeerid(event)] = Client(event.peer)
            
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            print("%s: DISCONNECT" % event.peer.address)
            
            if self.getpeerid(event) in self.clients.keys():
                client = self.clients[self.getpeerid(event)]
                del self.clients[self.getpeerid(event)]
                client.on_disconnect()
                
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            if self.getpeerid(event) in self.clients.keys():
                self.clients[self.getpeerid(event)].on_receive_event(event.channelID, event.packet.data)
        
    def run(self):
        while self._running:
            try:
                self.room_manager.update_rooms()
                self.service_host()
                if self.room_manager.sendpackets():
                    self._enet_host.flush()
            except:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                if exceptionType == KeyboardInterrupt:
                    print ""
                    return
                
                print "Uncaught exception occurred in server engine mainloop."
                print traceback.format_exc()