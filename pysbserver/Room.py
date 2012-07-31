import time, traceback, random
from Constants import * #@UnusedWildImport
from CubeDataStream import CubeDataStream

from Vector import vec #@UnresolvedImport

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
            room.broadcastf(1, "ii", [message_types.N_ITEMSPAWN, self.index], True);
            self.spawntime = -1
            return
        
        if self.type in [item_types.I_QUAD, item_types.I_BOOST] and (self.spawntime - time.time()) < 10 and not self.announced:
            room.broadcastf(1, "ii", [message_types.N_ANNOUNCE, self.type], True)
            self.announced = True
        
    def pickup(self, room, client):
        if self.spawntime != -1: return
        client.state.pickup_item(self.type)
        room.broadcastf(1, "iii", [message_types.N_ITEMACC, self.index, client.cn], True);
        playercount = len(room.clients)
        self.spawntime = time.time() + Item.respawn_delay(self.type, playercount)
        self.announced = False

class Room(object):
    "A room holds the current match state for a collection of engine clients."
    name = ""
    clients = []
    
    mode_num = 0
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
        
    def update_room(self):
        if len(self.clients) <= 0: return
        
        map(lambda i: i.update, self.items)
        
        if self.intermission_end_time is not None:
            if time.time() > self.intermission_end_time:
                self.broadcastf(1, "i", [message_types.N_MAPRELOAD], True)
                self.intermission_end_time = None
        elif self.match_end_time is not None:
            if time.time() > self.match_end_time:
                self.broadcastf(1, "ii", [message_types.N_TIMEUP, 0], True)
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
            client.Disconnected.connect(self.on_client_disconnected)
            client.ping.connect(self.on_clientping)
            client.mapvote.connect(self.on_client_mapvote)
            client.suicide.connect(self.on_client_suicide)
            client.jumppad.connect(self.on_client_jumppad)
            client.teleport.connect(self.on_client_teleport)
            client.pickup.connect(self.on_client_pickup)
            client.itemlist.connect(self.on_clientitemlist)
            client.shoot.connect(self.on_client_shoot)
            client.explode.connect(self.on_client_explode)
            client.trysetteam.connect(self.on_client_trysetteam)
            
            cds = CubeDataStream()
            
            cds.write(self.build_welcome())
            
            if self.map_name != None:
                cds.write(self.build_map_change())
                if self.match_end_time is not None:
                    cds.write(self.build_timeup())
                    
            if self.hasitems:
                cds.putint(message_types.N_ITEMLIST)
                for item in self.items:
                    if item.spawned:
                        cds.putint(item.index)
                        cds.putint(item.type)
                cds.putint(-1)
            
            cds.write(self.build_resumeclients(existing_clients))
            cds.write(self.build_initclients(existing_clients))
            
            client.send(1, cds, True)
            
            self.broadcast(1, self.build_resumeclients([client]), True, [client])
            self.broadcast(1, self.build_initclients([client]), True, [client])
            
            if len(existing_clients) > 0:
                client.send_spawn_state()
            
        except:
            traceback.print_exc()
            
    @property
    def timeleft(self):
        return self.match_end_time - time.time()
    
    @timeleft.setter
    def timeleft(self, value):
        self.match_end_time = time.time() + value
        self.broadcast(1, self.build_timeup(), True)
            
    def change_map_mode(self, map_name, mode_num):
        self.hasitems = False
        self.items = []
        
        self.map_name = map_name
        self.mode_num = mode_num
        self.broadcast(1, self.build_map_change(), True)
        
        for client in self.clients.values():
            client.send_spawn_state()
        
        self.timeleft = MATCHLEN
        
    def on_client_disconnected(self, client):
        if client.cn in self.clients.keys():
            del self.clients[client.cn]
            self.broadcastf(1, "ii", [message_types.N_CDIS, client.cn], True)
                
    def on_clientping(self, client):
        pass
        
    def on_client_suicide(self, client):
        self.broadcastf(1, "iiii", [message_types.N_DIED, client.cn, client.cn, client.state.frags], True)
        client.state.state = client_states.CS_DEAD
        
    def on_client_mapvote(self, client, map_name, mode_num):
        self.change_map_mode(map_name, mode_num)
        
    def on_client_jumppad(self, client, jumppad):
        self.broadcastf(0, "iii", [message_types.N_JUMPPAD, client.cn, jumppad], True, [client])
        
    def on_client_teleport(self, client, teleport, teledest):
        self.broadcastf(0, "iiii", [message_types.N_TELEPORT, client.cn, teleport, teledest], True, [client])
        
    def on_client_pickup(self, client, item_index):
        if item_index < len(self.items) and item_index >= 0:
            self.items[item_index].pickup(self, client)
            
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
        
        self.broadcastf(1, 'i'*10, [message_types.N_SHOTFX, client.cn, gun, shot_id, fx, fy, fz, tx, ty, tz], 
                        exclude=[client])
        
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
            
            
        self.broadcastf(1, 'i'*4, [message_types.N_EXPLODEFX, client.cn, gun, explode_id], 
                        exclude=[client])
        
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
        self.broadcastf(1, 'i'*6, [message_types.N_DAMAGE, target.cn, client.cn, damage, target.state.armour, target.state.health], True)
        
        if target == client:
            #target.state.setpushed()
            pass
        elif not v.iszero():
            if target.state.health <= 0:
                self.broadcastf(1, 'i'*7, [message_types.N_HITPUSH, target.cn, gun, damage, v.x, v.y, v.z], True)
            else:
                target.sendf(1, 'i'*7, [message_types.N_HITPUSH, target.cn, gun, damage, v.x, v.y, v.z], True)
            #target.state.setpushed()
            
        if target.state.health < 1:
            target.state.state = client_states.CS_DEAD
            
            target.state.deaths += 1
            client.state.frags += 1
            
            self.broadcastf(1, 'i'*4, [message_types.N_DIED, target.cn, client.cn, client.state.frags], True)
    
    def on_clientitemlist(self, client, item_list):
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
            
    def on_client_trysetteam(self, client, target_cn, oldteam, team):
        pass
        
    def build_welcome(self):
        return self.buildf('ii', [message_types.N_WELCOME, 1 if self.map_name != None else 0])
        
    def build_map_change(self):
        return self.buildf('isii', [message_types.N_MAPCHANGE, self.map_name, self.mode_num, 0 if self.hasitems else 1])
        
    def build_timeup(self):
        return self.buildf('ii', [message_types.N_TIMEUP, int(self.timeleft)])
        
    def build_setspectator(self, client, value):
        return self.buildf('iii', [message_types.N_SPECTATOR, client.cn, 1 if value else 0])
    
    def build_initclients(self, clients):
        cds = CubeDataStream()
        
        for client in clients:
            if client.isai:
                cds.putint(message_types.N_INITAI)
                cds.putint(client.cn)
                cds.putint(client.owner.cn)
                cds.putint(client.aitype)
                cds.putint(client.aiskill)
                cds.putint(client.playermodel)
                cds.putstring(client.name)
                cds.putstring(client.team)
            else:
                cds.putint(message_types.N_INITCLIENT)
                cds.putint(client.cn)
                cds.putstring(client.name)
                cds.putstring(client.team)
                cds.putint(client.playermodel)
            
        return cds
        
    def build_resumeclients(self, clients):
        
        cds = CubeDataStream()
        
        cds.putint(message_types.N_RESUME)
        
        for client in clients:
            
            cds.putint(client.cn)
            cds.putint(client.state.state)
            cds.putint(client.state.frags)
            cds.putint(client.state.flags)
            cds.putint(client.state.quadexpiry)
            
            cds.putint(client.state.lifesequence)
            cds.putint(client.state.health)
            cds.putint(client.state.maxhealth)
            cds.putint(client.state.armour)
            cds.putint(client.state.armourtype)
            cds.putint(client.state.gunselect)
            
            for weapon_index in range(weapon_types.GUN_SG, weapon_types.GUN_PISTOL+1):
                cds.putint(client.state.ammo[weapon_index])
                
        cds.putint(-1)
        
        return cds