import time, random
from Constants import * #@UnusedWildImport
import ServerWriteHelper as swh

class Item(object):
    index = 0
    type = 0
    spawntime = -1
    announced = False
    
    @staticmethod
    def spawn_delay(item_type, playercount):
        if item_type in [item_types.I_GREENARMOUR, item_types.I_YELLOWARMOUR, item_types.I_BOOST, item_types.I_QUAD]:
            return Item.respawn_delay(item_type, playercount)
        else:
            return -1
    
    @staticmethod
    def respawn_delay(item_type, playercount):
        base = playercount
        
        if playercount < 3:
            base = 4
        elif playercount in [3, 4]:
            base = 3
        elif playercount > 4:
            base = 2
            
        if item_type >= item_types.I_SHELLS and item_type <= item_types.I_CARTRIDGES:
            secs = base*4
        elif item_type == item_types.I_HEALTH:
            secs = base*5
        elif item_type == item_types.I_GREENARMOUR or item_type == item_types.I_YELLOWARMOUR:
            secs = 20
        elif item_type == item_types.I_BOOST or item_type == item_types.I_QUAD:
            secs = random.randint(40, 80)
        else:
            secs = 0
            
        return secs

    def __init__(self, index, item_type, delay):
        self.index = index
        self.type = item_type
        if delay != -1:
            self.spawntime = time.time() + delay
        
    @property
    def spawned(self):
        return self.spawntime == -1
        
    def update(self, room):
        if self.spawntime == -1: return
        
        if self.spawntime < time.time():
            
            with room.broadcastbuffer(1, True) as cds: 
                swh.put_itemspawn(cds, self)
                
            self.spawntime = -1
            return
        
        if self.type in [item_types.I_QUAD, item_types.I_BOOST] and (self.spawntime - time.time()) < 10 and not self.announced:
            
            with room.broadcastbuffer(1, True) as cds: 
                swh.put_announce(cds, self)
                
            self.announced = True
        
    def pickup(self, room, client):
        if self.spawntime != -1: return
        client.state.pickup_item(self.type)
        
        with room.broadcastbuffer(1, True) as cds: 
            swh.put_itemacc(cds, self, client)
            
        playercount = len(room.clients)
        self.spawntime = time.time() + Item.respawn_delay(self.type, playercount)
        self.announced = False