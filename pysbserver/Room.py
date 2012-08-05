import time, traceback, random
from Constants import * #@UnusedWildImport
from CubeDataStream import CubeDataStream
import ServerWriteHelper as swh #@UnresolvedImport
import contextlib

from Vector import vec #@UnresolvedImport

from Item import Item #@UnresolvedImport

from gamemodes import gamemodes #@UnresolvedImport

class Room(object):
    "A room holds the current match state for a collection of engine clients."
    name = ""
    clients = []
    
    mode_num = 0
    gamemode = gamemodes[mode_num]()
    map_name = None
    match_end_time = None
    hasitems = False
    haspwd = False
    pausedtime = None
    
    worldstates = []
    lastsend = None
    
    items = {}
    
    def __init__(self, name):
        self.clients = {}
        self.name = name
        
        self.mode_num = 0
        self.map_name = None
        self.match_end_time = None
        self.intermission_end_time = None
        self.hasitems = False
        self.haspwd = False
        
        self.items = []
        
    @property
    def hasmap(self):
        return self.map_name != None
        
    def update_room(self):
        if len(self.clients) <= 0: return
        
        map(lambda i: i.update, self.items)
        
        self.gamemode.update(self)
        
        if self.intermission_end_time is not None:
            if time.time() > self.intermission_end_time:
                
                with self.broadcastbuffer(1, True) as cds:
                    swh.put_mapreload(cds)
                    
                self.intermission_end_time = None
        elif self.match_end_time is not None and self.gamemode.timed:
            if time.time() > self.match_end_time:
                
                with self.broadcastbuffer(1, True) as cds:
                    swh.put_timeup(cds, 0)
                    
                self.match_end_time = None
                self.intermission_end_time = time.time() + INTERMISSIONLEN
    
    def sendpackets(self, force=False):
        if len(self.clients) == 0:
            return False
        if self.lastsend is not None:
            curtime = (time.time() - self.lastsend)
            if curtime < .033 and not force:
                return False
        flush = self.send_room_state()
        self.lastsend = time.time()
        return flush
    
    def send_room_state(self):
        flush = False
        
        for client in self.clients.values():
            if client.isai: continue
            
            room_positions = CubeDataStream()
            room_messages = CubeDataStream()
            
            for ci in self.clients.values():
                if ci == client: continue
                if ci.isai and ci.owner == client: continue
                
                ci.writestate(room_positions, room_messages)
            
            if not room_positions.empty():
                client.send(0, room_positions, False)
                flush = True
                    
            if not room_messages.empty():
                client.send(1, room_messages, True)
                flush = True
        
        return flush
        
    def broadcast(self, channel, data, reliable=False, exclude=[]):
        for client in exclude[:]:
            if client.isai:
                exclude.append(client.owner)
        
        for client in self.clients.values():
            if not client in exclude and not client.isai:
                client.send(channel, str(data), reliable)
                
    @contextlib.contextmanager
    def broadcastbuffer(self, channel, reliable=False, exclude=[]):
        cds = CubeDataStream()
        yield cds
        self.broadcast(channel, cds, reliable, exclude)
            
    def buildf(self, fmt, data_items):
        fmt = list(fmt)
        
        try:
            ic = fmt.index('c')
            while ic >= 0:
                fmt[ic] = 'i'
                data_items[ic] = data_items[ic].cn
                ic = fmt.index('c')
        except ValueError:
            pass
        
        return CubeDataStream.pack_format(fmt, data_items)
            
    def broadcastf(self, channel, fmt, data_items, reliable=False, exclude=[]):
        data = self.buildf(fmt, data_items)
        self.broadcast(channel, data, reliable, exclude)
        
    def add_client(self, client):
        try:
            existing_clients = self.clients.values()
            
            self.clients[client.cn] = client
            
            self.gamemode.on_client_connected(self, client)
            
            # Connect up all the client signals
            client.connect_all_instance_signals(self, "on_client_")
            
            # Tell the client about the status of the room
            with client.sendbuffer(1, True) as cds: 
                swh.put_welcome(cds, self.hasmap)
                
                if self.map_name != None:
                    swh.put_mapchange(cds, self.map_name, self.mode_num, self.hasitems)
                    
                    if self.gamemode.timed and self.match_end_time is not None:
                        swh.put_timeup(cds, self.timeleft)
                        
                if self.gamemode.hasitems and self.hasitems:
                    swh.put_itemlist(cds, self.items)
                
                swh.put_resume(cds, existing_clients)
                swh.put_initclients(cds, existing_clients)
            
            # Tell the other clients about the newcomer
            with self.broadcastbuffer(1, True, [client]) as cds:
                swh.put_resume(cds, [client])
                swh.put_initclients(cds, [client])
            
            if len(existing_clients) > 0:
                client.send_spawn_state(self.gamemode)
            
        except:
            traceback.print_exc()
            
    @property
    def timeleft(self):
        return self.match_end_time - time.time()
    
    @timeleft.setter
    def timeleft(self, value):
        self.match_end_time = time.time() + value
        with self.broadcastbuffer(1, True) as cds:
            swh.put_timeup(cds, self.timeleft)
            
    def change_map_mode(self, map_name, mode_num):
        if not mode_num in gamemodes.keys():
            return
        
        self.gamemode = gamemodes[mode_num]()
        
        self.hasitems = False
        self.items = []
        
        self.map_name = map_name
        self.mode_num = mode_num
        with self.broadcastbuffer(1, True) as cds:
            swh.put_mapchange(cds, self.map_name, self.mode_num, self.hasitems)
        
        for client in self.clients.values():
            client.send_spawn_state(self.gamemode)
        
        if self.gamemode.timed:
            self.timeleft = self.gamemode.timeout
        
    def on_client_disconnected(self, client):
        if client.cn in self.clients.keys():
            del self.clients[client.cn]
            with self.broadcastbuffer(1, True) as cds:
                swh.put_cdis(cds, client)
            self.gamemode.on_client_disconnected(self, client)
                
    def on_client_ping(self, client):
        pass
        
    def on_client_mapvote(self, client, map_name, mode_num):
        self.change_map_mode(map_name, mode_num)
        
    def on_client_mapcrc(self, client, mapcrc):
        pass
        
    def on_client_suicide(self, client):
        with self.broadcastbuffer(1, True) as cds:
            swh.put_died(cds, client, client)
        client.state.state = client_states.CS_DEAD
        
    def on_client_tryspawn(self, client):
        pass
    
    def on_client_spawn(self, client):
        pass
        
    def on_client_jumppad(self, client, jumppad):
        with self.broadcastbuffer(1, True, [client]) as cds:
            swh.put_jumppad(cds, client, jumppad)
        
    def on_client_teleport(self, client, teleport, teledest):
        with self.broadcastbuffer(1, True, [client]) as cds:
            swh.put_teleport(cds, client, teleport, teledest)
        
    def on_client_pickup(self, client, item_index):
        if item_index < len(self.items) and item_index >= 0:
            self.items[item_index].pickup(self, client)
            
    def on_client_takeflag(self, client, flag, version):
        pass
    
    def on_client_trydropflag(self, client):
        pass
    
    def on_client_replenishammo(self, client):
        pass
            
    def on_client_shoot(self, client, shot_id, gun, fx, fy, fz, tx, ty, tz, hits):
        if client.state.lastshot == -1:
            wait = time.time() - client.state.lastshot
        else:
            wait = client.state.gunwait
        
        pfrom = vec(fx, fy, fz).div(DMF)
        pto = vec(tx, ty, tz).div(DMF)
        
        if not client.state.alive or wait < client.state.gunwait: return
        if gun < weapon_types.GUN_FIST or gun > weapon_types.GUN_PISTOL: return
        if client.state.ammo[gun] <= 0: return
        if guns[gun].range and (pfrom.dist(pto) > guns[gun].range + 1): return
        
        if gun != weapon_types.GUN_FIST:
            client.state.ammo[gun] -= 1
            
        client.state.lastshot = time.time()
        client.state.gunwait = float(guns[gun].attackdelay)/1000.0
        
        with self.broadcastbuffer(1, True, [client]) as cds:
            swh.put_shotfx(cds, client, gun, shot_id, fx, fy, fz, tx, ty, tz)
        
        if gun == weapon_types.GUN_RL:
            client.state.rockets[shot_id] = gun
        elif gun == weapon_types.GUN_GL:
            client.state.grenades[shot_id] = gun
        else:
            for hit in hits:
                self.on_client_hit(client, gun, **hit)
        
    def on_client_explode(self, client, cmillis, gun, explode_id, hits):
        if gun == weapon_types.GUN_RL:
            if not explode_id in client.state.rockets.keys(): return
            del client.state.rockets[explode_id]
        elif gun == weapon_types.GUN_GL:
            if not explode_id in client.state.grenades.keys(): return
            del client.state.grenades[explode_id]
            
            
        with self.broadcastbuffer(1, True, [client]) as cds:
            swh.put_explodefx(cds, client, gun, explode_id)
        
        if gun == weapon_types.GUN_SG:
            max_rays = SGRAYS
        else:
            max_rays = 1
            
        total_rays = 0
            
        for hit in hits:
            total_rays += hit['rays']
            if total_rays > max_rays:
                break
            self.on_client_hit(client, gun, **hit)
            
    def on_client_hit(self, client, gun, target, lifesequence, distance, rays, dx, dy, dz):
        if target in self.clients.keys():
            target = self.clients[target]
            
            damage = guns[gun].damage
            
            if not gun in [weapon_types.GUN_RL, weapon_types.GUN_GL]:
                damage *= rays
            
            if client.state.quadexpiry > time.time():
                damage *= 4
                
            if gun in [weapon_types.GUN_RL, weapon_types.GUN_GL]:
                damage *= (1 - ((distance/DMF)/RL_DISTSCALE)/RL_DAMRAD)
                
            if gun == weapon_types.GUN_RL and target == client:
                damage /= RL_SELFDAMDIV
            
            self.damage_client(target, client, damage, gun, dx, dy, dz)
            
    def damage_client(self, target, client, damage, gun, dx, dy, dz):
        v = vec(dx, dy, dz).div(DMF).rescale(DNF)
        
        target.state.receive_damage(damage)
        
        with self.broadcastbuffer(1, True) as cds:
            swh.put_damage(cds, target, client, damage)
            
            if target == client:
                #target.state.setpushed()
                pass
            elif not v.iszero():
                if target.state.health <= 0:
                    swh.put_hitpush(cds, target, gun, damage, v)
                else:
                    with target.sendbuffer(1, True) as cds:
                        swh.put_hitpush(cds, target, gun, damage, v)
                #target.state.setpushed()
                
            if target.state.health < 1:
                target.state.state = client_states.CS_DEAD
                
                target.state.deaths += 1
                client.state.frags += 1
                
                swh.put_died(cds, target, client)
    
    def on_client_itemlist(self, client, item_list):
        if not self.hasitems:
            self.items = []
            i = 0
            for item_dict in item_list:
                n = item_dict['item_index']
                while i < n:
                    self.items.append(Item(i, 0, -1))
                    i += 1
                
                spawndelay = Item.spawn_delay(item_dict['item_type'], len(self.clients))
                
                self.items.append(Item(n, item_dict['item_type'], spawndelay))
                i += 1
                
            self.hasitems = True
            
    def on_client_flaglist(self, client, flag_list):
        pass
    
    def on_client_baselist(self, client, base_list):
        pass
            
    def on_client_trysetteam(self, client, target_cn, oldteam, team):
        pass
    
    def on_client_setspectator(self, client, target_cn, value):
        pass