from enum import enum

PROTOCOL_VERSION = 258

# match constants
MATCHLEN = 600
INTERMISSIONLEN = 10

# player detail constants
MAXNAMELEN = 15
MAXTEAMLEN = 4
MAXAUTHNAMELEN = 100

# math constants
PI = 3.1415927
SQRT2 = 1.4142136
SQRT3 = 1.7320508
RAD = PI / 180.0

# network quantization scale
DMF = 16.0                # for world locations
DNF = 100.0               # for normalized vectors
DVELF = 1.0               # for playerspeed based velocity vectors

# weapon detail constants
SGRAYS = 20
SGSPREAD = 4
RL_DAMRAD = 40
RL_SELFDAMDIV = 2
RL_DISTSCALE = 1.5

# cubescript identity types
cs_id_types = enum('ID_VAR', 'ID_FVAR', 'ID_SVAR', 'ID_COMMAND', 'ID_CCOMMAND', 'ID_ALIAS')

client_states = enum('CS_ALIVE', 'CS_DEAD', 'CS_SPAWNING', 'CS_LAGGED', 'CS_EDITING', 'CS_SPECTATOR')

weapon_types = enum('GUN_FIST', 'GUN_SG', 'GUN_CG', 'GUN_RL', 'GUN_RIFLE', 'GUN_GL', 'GUN_PISTOL', 'GUN_FIREBALL', 'GUN_ICEBALL', 'GUN_SLIMEBALL', 'GUN_BITE', 'GUN_BARREL', 'NUMGUNS')

item_types = enum(  NOTUSED=0,
                    I_SHELLS=8, I_BULLETS=9, I_ROCKETS=10, I_ROUNDS=11, I_GRENADES=12, I_CARTRIDGES=13,
                    I_HEALTH=14, I_BOOST=15,
                    I_GREENARMOUR=16, I_YELLOWARMOUR=17,
                    I_QUAD=18)

sounds = enum(
    'S_JUMP', 'S_LAND', 'S_RIFLE', 'S_PUNCH1', 'S_SG', 'S_CG',
    'S_RLFIRE', 'S_RLHIT', 'S_WEAPLOAD', 'S_ITEMAMMO', 'S_ITEMHEALTH',
    'S_ITEMARMOUR', 'S_ITEMPUP', 'S_ITEMSPAWN', 'S_TELEPORT', 'S_NOAMMO', 'S_PUPOUT',
    'S_PAIN1', 'S_PAIN2', 'S_PAIN3', 'S_PAIN4', 'S_PAIN5', 'S_PAIN6',
    'S_DIE1', 'S_DIE2',
    'S_FLAUNCH', 'S_FEXPLODE',
    'S_SPLASH1', 'S_SPLASH2',
    'S_GRUNT1', 'S_GRUNT2', 'S_RUMBLE',
    'S_PAINO',
    'S_PAINR', 'S_DEATHR',
    'S_PAINE', 'S_DEATHE',
    'S_PAINS', 'S_DEATHS',
    'S_PAINB', 'S_DEATHB',
    'S_PAINP', 'S_PIGGR2',
    'S_PAINH', 'S_DEATHH',
    'S_PAIND', 'S_DEATHD',
    'S_PIGR1', 'S_ICEBALL', 'S_SLIMEBALL',
    'S_JUMPPAD', 'S_PISTOL',

    'S_V_BASECAP', 'S_V_BASELOST',
    'S_V_FIGHT',
    'S_V_BOOST', 'S_V_BOOST10',
    'S_V_QUAD', 'S_V_QUAD10',
    'S_V_RESPAWNPOINT',

    'S_FLAGPICKUP',
    'S_FLAGDROP',
    'S_FLAGRETURN',
    'S_FLAGSCORE',
    'S_FLAGRESET',

    'S_BURN',
    'S_CHAINSAW_ATTACK',
    'S_CHAINSAW_IDLE',

    'S_HIT')

class GunInfo(object):
    sound, attackdelay, damage, projspeed, kickamount, range, name = [0]*7
    
    def __init__(self, sound, attackdelay, damage, projspeed, kickamount, gunrange, name):
        self.sound = sound
        self.attackdelay = attackdelay
        self.damage = damage
        self.projspeed = projspeed
        self.kickamount = kickamount 
        self.range = gunrange
        self.name = name

guns = [
    GunInfo(sounds.S_PUNCH1,        250,      50,         0,           0,      14,       "fist"),
    GunInfo(sounds.S_SG,            1400,     10,         0,           20,     1024,     "shotgun"),
    GunInfo(sounds.S_CG,            100,      30,         0,           7,      1024,     "chaingun"),
    GunInfo(sounds.S_RLFIRE,        800,      120,        80,          10,     1024,     "rocketlauncher"),
    GunInfo(sounds.S_RIFLE,         1500,     100,        0,           30,     2048,     "rifle"),
    GunInfo(sounds.S_FLAUNCH,       500,      75,         80,          10,     1024,     "grenadelauncher"),
    GunInfo(sounds.S_PISTOL,        500,      25,         0,           7,      1024,     "pistol"),
    GunInfo(sounds.S_FLAUNCH,       200,      20,         50,          1,      1024,     "fireball"),
    GunInfo(sounds.S_ICEBALL,       200,      40,         30,          1,      1024,     "iceball"),
    GunInfo(sounds.S_SLIMEBALL,     200,      30,         160,         1,      1024,     "slimeball"),
    GunInfo(sounds.S_PIGR1,         250,      50,         0,           1,      12,       "bite"),
]

armor_types = enum('A_BLUE', 'A_GREEN', 'A_YELLOW')

class ItemStat(object):
    add, max, info = [0]*3

    def __init__(self, a, m, i=0):
        self.add = a
        self.max = m
        self.info = i

itemstats = [
    ItemStat(10,    30,    weapon_types.GUN_SG),
    ItemStat(20,    60,    weapon_types.GUN_CG),
    ItemStat(5,     15,    weapon_types.GUN_RL),
    ItemStat(5,     15,    weapon_types.GUN_RIFLE),
    ItemStat(10,    30,    weapon_types.GUN_GL),
    ItemStat(30,    120,   weapon_types.GUN_PISTOL),
    ItemStat(25,    100),
    ItemStat(10,    1000),
    ItemStat(100,   100,   armor_types.A_GREEN),
    ItemStat(200,   200,   armor_types.A_YELLOW),
    ItemStat(20000, 30000),
]

disconnect_types = enum('DISC_NONE', 'DISC_EOP', 'DISC_CN', 'DISC_KICK', 'DISC_TAGT', 'DISC_IPBAN', 'DISC_PRIVATE', 'DISC_MAXCLIENTS', 'DISC_TIMEOUT', 'DISC_OVERFLOW', 'DISC_NUM')

message_types = enum('N_CONNECT', 'N_SERVINFO', 'N_WELCOME', 'N_INITCLIENT', 'N_POS', 'N_TEXT', 'N_SOUND', 'N_CDIS',
    'N_SHOOT', 'N_EXPLODE', 'N_SUICIDE',
    'N_DIED', 'N_DAMAGE', 'N_HITPUSH', 'N_SHOTFX', 'N_EXPLODEFX',
    'N_TRYSPAWN', 'N_SPAWNSTATE', 'N_SPAWN', 'N_FORCEDEATH',
    'N_GUNSELECT', 'N_TAUNT',
    'N_MAPCHANGE', 'N_MAPVOTE', 'N_ITEMSPAWN', 'N_ITEMPICKUP', 'N_ITEMACC', 'N_TELEPORT', 'N_JUMPPAD',
    'N_PING', 'N_PONG', 'N_CLIENTPING',
    'N_TIMEUP', 'N_MAPRELOAD', 'N_FORCEINTERMISSION',
    'N_SERVMSG', 'N_ITEMLIST', 'N_RESUME',
    'N_EDITMODE', 'N_EDITENT', 'N_EDITF', 'N_EDITT', 'N_EDITM', 'N_FLIP', 'N_COPY', 'N_PASTE', 'N_ROTATE', 'N_REPLACE', 'N_DELCUBE', 'N_REMIP', 'N_NEWMAP', 'N_GETMAP', 'N_SENDMAP', 'N_CLIPBOARD', 'N_EDITVAR',
    'N_MASTERMODE', 'N_KICK', 'N_CLEARBANS', 'N_CURRENTMASTER', 'N_SPECTATOR', 'N_SETMASTER', 'N_SETTEAM',
    'N_BASES', 'N_BASEINFO', 'N_BASESCORE', 'N_REPAMMO', 'N_BASEREGEN', 'N_ANNOUNCE',
    'N_LISTDEMOS', 'N_SENDDEMOLIST', 'N_GETDEMO', 'N_SENDDEMO',
    'N_DEMOPLAYBACK', 'N_RECORDDEMO', 'N_STOPDEMO', 'N_CLEARDEMOS',
    'N_TAKEFLAG', 'N_RETURNFLAG', 'N_RESETFLAG', 'N_INVISFLAG', 'N_TRYDROPFLAG', 'N_DROPFLAG', 'N_SCOREFLAG', 'N_INITFLAGS',
    'N_SAYTEAM',
    'N_CLIENT',
    'N_AUTHTRY', 'N_AUTHCHAL', 'N_AUTHANS', 'N_REQAUTH',
    'N_PAUSEGAME',
    'N_ADDBOT', 'N_DELBOT', 'N_INITAI', 'N_FROMAI', 'N_BOTLIMIT', 'N_BOTBALANCE',
    'N_MAPCRC', 'N_CHECKMAPS',
    'N_SWITCHNAME', 'N_SWITCHMODEL', 'N_SWITCHTEAM',
    'NUMSV')