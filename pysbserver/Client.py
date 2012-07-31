import enet #@UnresolvedImport

from util import filtertext #@UnresolvedImport

import traceback, time

from Signals import SignalObject, Signal

from CubeDataStream import CubeDataStream
from SauerbratenStreamSpecification import sauerbraten_stream_spec

from Constants import * #@UnusedWildImport

class PingBuffer(object):
    BUFFERSIZE = 15
    pings = []
    
    def __init__(self):
        self.pings = []
    
    def add(self, ping):
        self.pings.append(ping)
        if len(self.pings) > self.BUFFERSIZE:
            self.pings.pop(0)

class ClientState(object):
    state = client_states.CS_ALIVE
    frags = 0
    deaths = 0
    flags = 0
    quadexpiry = 0
    lifesequence = -1
    health = 100
    maxhealth = 100
    armour = 0
    armourtype = armor_types.A_BLUE
    gunselect = 6
    ammo = [0 for n in range(weapon_types.NUMGUNS)]
    
    lastshot = -1
    gunwait = -1
    
    rockets = {}
    grenades = {}
    
    messages = CubeDataStream()
    position = None
    
    def __init__(self):
        self.messages = CubeDataStream()
        self.position = None
        
        self.reset()
        
    @property
    def alive(self):
        return self.state == client_states.CS_ALIVE
    
    @property
    def spectator(self):
        return self.state == client_states.CS_SPECTATOR
        
    def respawn(self):
        self.lifesequence = (self.lifesequence + 1)&0x7F
        self.quadexpiry = -1
        self.health = self.maxhealth
        self.armour = 0
        self.armourtype = armor_types.A_BLUE
        self.gunselect = weapon_types.GUN_PISTOL
        self.ammo = [0 for n in range(weapon_types.NUMGUNS)] #@UnusedVariable
        
        self.ammo[weapon_types.GUN_PISTOL] = 40
        
        self.position = None
        
    def reset(self):
        self.state = client_states.CS_ALIVE
        self.frags = 0
        self.deaths = 0
        self.flags = 0
        self.quadexpiry = -1
        self.lifesequence = -1
        self.health = 100
        self.maxhealth = 100
        self.armour = 0
        self.armourtype = armor_types.A_BLUE
        self.gunselect = weapon_types.GUN_PISTOL
        self.ammo = [0 for n in range(weapon_types.NUMGUNS)] #@UnusedVariable
        
        self.ammo[weapon_types.GUN_PISTOL] = 40
        
        self.lastshot = -1
        self.gunwait = -1
        
        self.rockets = {}
        self.grenades = {}
        
        self.messages.clear()
        self.position = None
        
    def receive_damage(self, damage):
        ad = damage*(self.armourtype+1)*(25.0/100.0) # let armour absorb when possible
        if ad > self.armour:
            ad = self.armour
        self.armour -= ad
        damage -= ad;
        self.health -= damage
        return damage
    
    def pickup_item(self, item_type):
        if item_type < item_types.I_SHELLS or item_type > item_types.I_QUAD: 
            return
        
        itemstat = itemstats[item_type-item_types.I_SHELLS]
        
        if item_type == item_types.I_BOOST: # boost also adds to health
            self.maxhealth = min(self.maxhealth+itemstat.add, itemstat.max)
        
        if item_type in (item_types.I_BOOST, item_types.I_HEALTH):
                self.health = min(self.health+itemstat.add, self.maxhealth)

        elif item_type in [item_types.I_GREENARMOUR, item_types.I_YELLOWARMOUR]:
            self.armour = min(self.armour+itemstat.add, itemstat.max)
            self.armourtype = itemstat.info
        elif item_type == item_types.I_QUAD:
            if self.quadexpiry < time.time():
                self.quadexpiry = time.time() + float(itemstat.add)/1000.0
            else:
                self.quadexpiry = time.time() + min((self.quadexpiry - time.time()) + float(itemstat.add)/1000.0, float(itemstat.max)/1000.0)
        else: # is an ammo
            self.ammo[itemstat.info] = min(self.ammo[itemstat.info]+itemstat.add, itemstat.max)
    
class ClientBase(SignalObject):
    cn = -1
    name = "unnamed"
    team = "evil"
    state = None
    playermodel = 0
    ping_buffer = None
    isai = False
    
    cn_pool = []
    
    spawn = Signal
    jumppad = Signal
    teleport = Signal
    pickup = Signal
    itemlist = Signal
    shoot = Signal
    explode = Signal
    
    def __init__(self):
        SignalObject.__init__(self)
        
        self.state = ClientState()
        self.cn = self.cn_pool.pop(0)
    
    def writestate(self, pos_cds, msg_cds):
        if self.state.position is not None:
            pos_cds.write(self.state.position)
            self.state.position = None
            
        if not self.state.messages.empty():
            msg_cds.putint(message_types.N_CLIENT)
            msg_cds.putint(self.cn)
            msg_cds.putuint(len(self.state.messages.data))
            msg_cds.write(self.state.messages.data)
            self.state.messages.clear()
    
class AiClient(ClientBase):
    isai = True
    owner = None
    aiskill = -1
    aitype = -1
    
    def __init__(self, ping_buffer):
        ClientBase.__init__(self)
        
        self.ping_buffer = ping_buffer
        
    def send(self, *args, **kwargs):
        if self.owner is None: return
        self.owner.send(*args, **kwargs)
        
    def sendf(self, *args, **kwargs):
        if self.owner is None: return
        self.owner.sendf(*args, **kwargs)
        
class InvalidClientNumberReference(Exception):
    '''Invalid cn Reference'''
    def __init__(self, value=''):
        Exception.__init__(self, value)

class Client(ClientBase):
    connected = False
    peer = None
    isai = False
    disc = False
    
    # class signals
    Connected = Signal()
    
    # instance signals
    Disconnected = Signal
    ping = Signal
    mapvote = Signal
    suicide = Signal
    trysetteam = Signal
    setspectator = Signal
    
    #indexed by cn
    bots = {}
    
    def __init__(self, peer):
        ClientBase.__init__(self)
        
        self.peer = peer
        self.bots = {}
        self.ping_buffer = PingBuffer()
        
        self.send_server_info(False, "Test Server")
        
    def getclient(self, cn):
        if cn == self.cn or cn == -1:
            return self
        elif cn in self.bots.keys():
            return self.bots[cn]
        else:
            raise InvalidClientNumberReference(cn)
        
    def send(self, channel, data, reliable=False):
        if self.disc:
            return
        
        if reliable:
            flags = enet.PACKET_FLAG_RELIABLE
        else:
            flags = 0
            
        #print "Sending: '%s' to client cn: %d" %(repr(str(data)), self.cn)
        
        packet = enet.Packet(str(data), flags)
        status = self.peer.send(channel, packet)
        if status < 0:
            print("%s: Error sending packet!" % self.peer.address)
            self.on_disconnect()
            
    def sendf(self, channel, fmt, data_items, reliable=False):
        fmt = list(fmt)
        
        try:
            ic = fmt.index('c')
            while ic >= 0:
                fmt[ic] = 'i'
                data_items[ic] = data_items[ic].cn
                ic = fmt.index('c')
        except ValueError:
            pass
            
        self.send(channel, CubeDataStream.pack_format(fmt, data_items), reliable)
        
    def on_disconnect(self):
        self.disc = True
        self.Disconnected.emit(self)
        self.peer.disconnect(disconnect_types.DISC_NONE)
        self.cn_pool.append(self.cn)
        self.cn_pool.sort()
        
    def on_receive_event(self, channel, data):
        if len(data) <= 0:
            pass
        
        try:
            if channel == 0:
                try:
                    cds = CubeDataStream(data)
                    message_type = cds.getint()
                    cn = cds.getint()
                    self.getclient(cn).state.position = data
                except:
                    traceback.print_exc()
            elif channel == 1:
                messages = sauerbraten_stream_spec.read(data, {'aiclientnum': -1})
                
                for message_type, message in messages:
                    if (not self.connected) and message_type != "N_CONNECT":
                        self.peer.disconnect(disconnect_types.DISC_TAGT) #@UndefinedVariable
                        return
                    
                    elif self.connected and message_type == "N_CONNECT":
                        self.peer.disconnect(disconnect_types.DISC_TAGT) #@UndefinedVariable
                        return
                    
                    elif message_type == "N_CONNECT":
                        self.connected = True
                        self.name = filtertext(message['name'], False, MAXNAMELEN)
                        self.pwdhash = message['pwdhash']
                        self.playermodel = message['playermodel']
                        
                        self.Connected.emit(self)
                        
                    elif message_type == "N_SWITCHNAME":
                        name = filtertext(message['name'], False, MAXNAMELEN)
                        if len(name) <= 0:
                            name = "unnamed"
                            
                        if name != self.name:
                            self.name = name
                            self.state.messages.putint(message_types.N_SWITCHNAME)
                            self.state.messages.putstring(self.name)
                        
                    elif message_type == "N_SWITCHTEAM":
                        team = filtertext(message['team'], False, MAXTEAMLEN)
                        if team != self.team:
                            self.trysetteam.emit(self, self.cn, self.team, team)
                            
                    elif message_type == "N_SPECTATOR":
                        self.setspectator.emit(self, message['target_cn'], message['value'] != 0)
                        
                    elif message_type == "N_PING":
                        self.sendf(1, 'ii', [message_types.N_PONG, message['cmillis']], False)
                        
                    elif message_type == "N_CLIENTPING":
                        self.ping_buffer.add(message['ping'])
                        
                        self.ping.emit(self)
                        
                        self.state.messages.putint(message_types.N_CLIENTPING)
                        self.state.messages.putint(message['ping'])
                        
                    elif message_type == "N_MAPVOTE":
                        self.mapvote.emit(self, message['map_name'], message['mode_num'])
                        
                    elif message_type == "N_MAPCHANGE":
                        self.mapvote.emit(self, message['map_name'], message['mode_num'])
                        
                    elif message_type == "N_ITEMLIST":
                        self.itemlist.emit(self, message['items'])
                        
                    elif message_type == "N_SPAWN":
                        client = self.getclient(message['aiclientnum'])
                        
                        client.state.state = client_states.CS_ALIVE
                        client.lifesequence = message['lifesequence']
                        client.gunselect = message['gunselect']
                        
                        client.state.messages.write(client.build_spawnstate())
                        
                    elif message_type == "N_TRYSPAWN":
                        self.send_spawn_state()
                        
                    elif message_type == "N_SHOOT":
                        message['client'] = self.getclient(message['aiclientnum'])
                        del message['aiclientnum']
                        self.shoot.emit(**message)
                        
                    elif message_type == "N_EXPLODE":
                        message['client'] = self.getclient(message['aiclientnum'])
                        del message['aiclientnum']
                        self.explode.emit(**message)
                        
                    elif message_type == "N_SUICIDE":
                        self.suicide.emit(self.getclient(message['aiclientnum']))
                        
                    elif message_type == "N_JUMPPAD":
                        cn = message['clientnum']
                        self.jumppad.emit(self.getclient(cn), message['jumppad'])
                        
                    elif message_type == "N_TELEPORT":
                        cn = message['clientnum']
                        self.teleport.emit(self.getclient(cn), message['teleport'], message['teledest'])
                        
                    elif message_type == "N_GUNSELECT":
                        mcds = self.getclient(message['aiclientnum']).state.messages
                        mcds.putint(message_types.N_GUNSELECT)
                        mcds.putint(message['gunselect'])
                        self.state.gunselect = message['gunselect']
                        
                    elif message_type == "N_SOUND":
                        mcds = self.getclient(message['aiclientnum']).state.messages
                        mcds.putint(message_types.N_SOUND)
                        mcds.putint(message['sound'])
                        
                    elif message_type == "N_ITEMPICKUP":
                        self.pickup.emit(self.getclient(message['aiclientnum']), message['item_index'])
                        
                    else:
                        print message_type, message
                
            else: #channel == 2:
                pass
        except InvalidClientNumberReference:
            return
        except:
            traceback.print_exc()
            
    def send_server_info(self, haspwd, description):
        self.sendf(1, 'iiiiis', 
                   [message_types.N_SERVINFO, self.cn, PROTOCOL_VERSION, 
                    id(self), 1 if haspwd else 0 , description], True)
        
    def build_spawnstate(self):
        data_items = [
                        message_types.N_SPAWN,
                        self.state.lifesequence,
                        self.state.health,
                        self.state.maxhealth,
                        self.state.armour,
                        self.state.armourtype,
                        self.state.gunselect,
                        weapon_types.GUN_PISTOL-weapon_types.GUN_SG+1
                    ]
        
        data_items.extend(self.state.ammo[weapon_types.GUN_SG:weapon_types.GUN_PISTOL+1])
        
        fmt = 'i'*len(data_items)
        
        return CubeDataStream.pack_format(fmt, data_items)
        
    def send_spawn_state(self):
        self.state.respawn()
        
        data_items = [
                        message_types.N_SPAWNSTATE, 
                        self.cn, 
                        self.state.lifesequence,
                        self.state.health,
                        self.state.maxhealth,
                        self.state.armour,
                        self.state.armourtype,
                        self.state.gunselect,
                        weapon_types.GUN_PISTOL-weapon_types.GUN_SG+1
                    ]
        
        data_items.extend(self.state.ammo[weapon_types.GUN_SG:weapon_types.GUN_PISTOL+1])
        
        self.sendf(1, 'i'*len(data_items), data_items, True)