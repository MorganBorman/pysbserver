from abc import ABCMeta, abstractmethod, abstractproperty

class GameModeABC(object):
    __metaclass__ = ABCMeta
    
    def __init__(self):
        pass
    
    ##################################################
    ################ Update methods ##################
    ##################################################
    
    @abstractmethod
    def new_match(self, room):
        """Called at the start of each match in this mode."""
        pass
    
    @abstractmethod
    def update(self, room):
        """Called on every server update."""
        pass
    
    @abstractmethod
    def on_client_connected(self, room, client):
        pass
    
    @abstractmethod
    def on_client_disconnected(self, room, client):
        pass
    
    ##################################################
    ########### General mode properties ##############
    ##################################################
    """
    Provide general details used by the room.
    """
    @abstractproperty
    def clientmodenum(self):
        "The mode number which the client should get sent."
        pass
    
    @abstractproperty
    def timed(self):
        pass
    
    @abstractproperty
    def timeout(self):
        pass
    
    @abstractproperty
    def hasitems(self):
        pass
    
    @abstractproperty
    def hasflags(self):
        pass
    
    @abstractproperty
    def hasteams(self):
        pass
    
    @abstractproperty
    def spawnarmour(self):
        pass
    
    @abstractproperty
    def spawnarmourtype(self):
        pass
    
    @abstractproperty
    def spawnhealth(self):
        pass
    
    @abstractproperty
    def hasbases(self):
        pass
    
    @abstractproperty
    def spawnammo(self):
        pass
    
    @abstractproperty
    def spawngunselect(self):
        pass
    
    ##################################################
    ######### client event policy handlers ###########
    ##################################################
    """
    Perform whatever actions are required specifically for this
    game mode and return a boolean indicating whether the generic
    room processing for this event should occur.
    """
    
    @abstractmethod
    def on_client_ping(self, room, client):
        pass
    
    @abstractmethod
    def on_client_mapvote(self, room, client, map_name, mode_num):
        pass
    
    @abstractmethod
    def on_client_mapcrc(self, room, client, mapcrc):
        pass
    
    @abstractmethod
    def on_client_suicide(self, room, client):
        pass
    
    @abstractmethod
    def on_client_tryspawn(self, room, client):
        pass
    
    @abstractmethod
    def on_client_spawn(self, room, client):
        pass
    
    @abstractmethod
    def on_client_jumppad(self, room, client, jumppad):
        pass
    
    @abstractmethod
    def on_client_teleport(self, room, client, teleport, teledest):
        pass
    
    @abstractmethod
    def on_client_pickup(self, room, client, item_index):
        pass
    
    @abstractmethod
    def on_client_takeflag(self, room, client, flag, version):
        pass
    
    @abstractmethod
    def on_client_trydropflag(self, room, client):
        pass
    
    @abstractmethod
    def on_client_replenishammo(self, room, client):
        pass
    
    @abstractmethod
    def on_client_shoot(self, room, client, shot_id, gun, fx, fy, fz, tx, ty, tz, hits):
        pass
    
    @abstractmethod
    def on_client_explode(self, room, client, cmillis, gun, explode_id, hits):
        pass
    
    @abstractmethod
    def on_client_hit(self, room, client, gun, target, lifesequence, distance, rays, dx, dy, dz):
        pass
    
    @abstractmethod
    def on_client_itemlist(self, room, client, item_list):
        pass
    
    @abstractmethod
    def on_client_flaglist(self, room, client, flag_list):
        pass
    
    @abstractmethod
    def on_client_baselist(self, room, client, base_list):
        pass
    
    @abstractmethod
    def on_client_trysetteam(self, room, client, target_cn, oldteam, team):
        pass
    
    @abstractmethod
    def on_client_setspectator(self, room, client, target_cn, value):
        pass