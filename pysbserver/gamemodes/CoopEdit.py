from GameModeABC import GameModeABC #@UnresolvedImport
from pysbserver.Constants import weapon_types, armor_types

class CoopEdit(GameModeABC):
    ##################################################
    ################ Update methods ##################
    ##################################################

    def new_match(self, room):
        """Called at the start of each match in this mode."""
        pass

    def update(self, room):
        """Called on every server update."""
        pass
    
    def on_client_connected(self, room, client):
        pass
    
    def on_client_disconnected(self, room, client):
        pass
    
    ##################################################
    ########### General mode properties ##############
    ##################################################
    """
    Provide general details used by the room.
    """
    clientmodenum = 1
    timed = False
    timeout = 0
    hasitems = False
    hasflags = False
    hasbases = False
    hasteams = False
    spawnarmour = 100
    spawnarmourtype = armor_types.A_GREEN
    spawnhealth = 100
    
    @property
    def spawnammo(self):
        ammo = [0 for n in range(weapon_types.NUMGUNS)]
        ammo[weapon_types.GUN_PISTOL] = 40
        return ammo
    
    spawngunselect = weapon_types.GUN_PISTOL
    
    ##################################################
    ######### client event policy handlers ###########
    ##################################################
    """
    Perform whatever actions are required specifically for this
    game mode and return a boolean indicating whether the generic
    room processing for this event should occur.
    """
    
    def on_client_ping(self, room, client):
        return True
    
    def on_client_mapvote(self, room, client, map_name, mode_num):
        return True
    
    def on_client_mapcrc(self, room, client, mapcrc):
        return True
    
    def on_client_suicide(self, room, client):
        return True
    
    def on_client_tryspawn(self, room, client):
        return True
    
    def on_client_spawn(self, room, client):
        return True
    
    def on_client_jumppad(self, room, client, jumppad):
        return True
    
    def on_client_teleport(self, room, client, teleport, teledest):
        return True
    
    def on_client_pickup(self, room, client, item_index):
        return True
    
    def on_client_takeflag(self, room, client, flag, version):
        return True
    
    def on_client_trydropflag(self, room, client):
        return True

    def on_client_replenishammo(self, room, client):
        return True

    def on_client_shoot(self, room, client, shot_id, gun, fx, fy, fz, tx, ty, tz, hits):
        return True

    def on_client_explode(self, room, client, cmillis, gun, explode_id, hits):
        return True

    def on_client_hit(self, room, client, gun, target, lifesequence, distance, rays, dx, dy, dz):
        return True

    def on_client_itemlist(self, room, client, item_list):
        return True

    def on_client_flaglist(self, room, client, flag_list):
        return True

    def on_client_baselist(self, room, client, base_list):
        return True

    def on_client_trysetteam(self, room, client, target_cn, oldteam, team):
        return True

    def on_client_setspectator(self, room, client, target_cn, value):
        return True