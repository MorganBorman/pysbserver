from CubeDataStream import CubeDataStream

type_method_mapping = {
                            'stream_data': CubeDataStream.read,
                            'int': CubeDataStream.getint, 
                            'uint': CubeDataStream.getuint,
                            'string': CubeDataStream.getstring, 
                            'float': CubeDataStream.getfloat
                        }

from StreamSpecification import Field, FieldCollection, IteratedFieldCollection, TerminatedFieldCollection
from StreamSpecification import MessageType, StreamStateModifierType, StreamSpecification
from StreamSpecification import StreamContainerType, RawField

sauerbraten_stream_spec = StreamSpecification(CubeDataStream, type_method_mapping, {}, "int")

from Constants import message_types

mt = MessageType("N_CONNECT", 
        Field(name="name", type="string"),
        Field(name="pwdhash", type="string"),
        Field(name="playermodel", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_CONNECT, mt)


mt = MessageType("N_TELEPORT", 
        Field(name="clientnum", type="int"),
        Field(name="teleport", type="int"),
        Field(name="teledest", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_TELEPORT, mt)

mt = MessageType("N_JUMPPAD", 
        Field(name="clientnum", type="int"),
        Field(name="jumppad", type="int"))
sauerbraten_stream_spec.add_message_type(   message_types.N_JUMPPAD, mt)

mt = MessageType("N_CHECKMAPS")
sauerbraten_stream_spec.add_message_type(message_types.N_CHECKMAPS, mt)

mt = MessageType("N_EDITMODE",
        Field(name="value", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_EDITMODE, mt)

mt = MessageType("N_PING",
        Field(name="cmillis", type="int"))
sauerbraten_stream_spec.add_message_type(   message_types.N_PING, mt)

mt = MessageType("N_TRYSPAWN")
sauerbraten_stream_spec.add_message_type(message_types.N_TRYSPAWN, mt)

sm = StreamStateModifierType(Field(name="aiclientnum", type="int"))
sauerbraten_stream_spec.add_state_modifier_type(message_types.N_FROMAI, sm)
                            
mt = MessageType("N_SHOOT",
        Field(name="shot_id", type="int"),
        Field(name="gun", type="int"),
        Field(name="fx", type="int"),
        Field(name="fy", type="int"),
        Field(name="fz", type="int"),
        Field(name="tx", type="int"),
        Field(name="ty", type="int"),
        Field(name="tz", type="int"),
        
        IteratedFieldCollection(
                name="hits",
                count=Field(type="int"),
                field_collection=FieldCollection(
                                Field(name="target", type="int"),
                                Field(name="lifesequence", type="int"),
                                Field(name="distance", type="int"),
                                Field(name="rays", type="int"),
                                Field(name="dx", type="int"),
                                Field(name="dy", type="int"),
                                Field(name="dz", type="int")
                )))
sauerbraten_stream_spec.add_message_type(message_types.N_SHOOT, mt)

mt = MessageType("N_EXPLODE",
        Field(name="cmillis", type="int"),
        Field(name="gun", type="int"),
        Field(name="explode_id", type="int"),
        
        IteratedFieldCollection(
                name="hits",
                count=Field(type="int"),
                field_collection=FieldCollection(
                                Field(name="target", type="int"),
                                Field(name="lifesequence", type="int"),
                                Field(name="distance", type="int"),
                                Field(name="rays", type="int"),
                                Field(name="dx", type="int"),
                                Field(name="dy", type="int"),
                                Field(name="dz", type="int")
                )))
sauerbraten_stream_spec.add_message_type(message_types.N_EXPLODE, mt)

mt = MessageType("N_GUNSELECT",
        Field(name="gunselect", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_GUNSELECT, mt)

mt = MessageType("N_SPAWN",
        Field(name="lifesequence", type="int"),
        Field(name="gunselect", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_SPAWN, mt)

mt = MessageType("N_SUICIDE")
sauerbraten_stream_spec.add_message_type(message_types.N_SUICIDE, mt)

mt = MessageType("N_CLIENTPING",
        Field(name="ping", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_CLIENTPING, mt)

mt = MessageType("N_MAPCRC",
        Field(name="map_name", type="string"),
        Field(name="mapcrc", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_MAPCRC, mt)

mt = MessageType("N_INITFLAGS",
                IteratedFieldCollection(
                name="flags",
                count=Field(type="int"),
                field_collection=FieldCollection(Field(name="team", type="int"),
                                                 Field(name="x", type="int"),
                                                 Field(name="y", type="int"),
                                                 Field(name="z", type="int"))))
sauerbraten_stream_spec.add_message_type(message_types.N_INITFLAGS, mt)

mt = MessageType("N_TRYDROPFLAG")
sauerbraten_stream_spec.add_message_type(message_types.N_TRYDROPFLAG, mt)

mt = MessageType("N_TAKEFLAG",
        Field(name="flag", type="int"),
        Field(name="version", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_TAKEFLAG, mt)

mt = MessageType("N_BASES",
                IteratedFieldCollection(
                name="bases",
                count=Field(type="int"),
                field_collection=FieldCollection(Field(name="ammotype", type="int"),
                                                 Field(name="x", type="int"),
                                                 Field(name="y", type="int"),
                                                 Field(name="z", type="int"))))
sauerbraten_stream_spec.add_message_type(message_types.N_BASES, mt)

mt = MessageType("N_REPAMMO")
sauerbraten_stream_spec.add_message_type(message_types.N_REPAMMO, mt)

mt = MessageType("N_ITEMLIST",
        TerminatedFieldCollection(name="items",
                                    terminator_field=Field(type="int"),
                                    terminator_comparison=lambda t: t >= 0,
                                    field_collection=FieldCollection(
                                                                 Field(name="item_index", type="int"),
                                                                 Field(name="item_type", type="int")))
                 )
sauerbraten_stream_spec.add_message_type(message_types.N_ITEMLIST, mt)

mt = MessageType("N_SOUND",
        Field(name="sound", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_SOUND, mt)

mt = MessageType("N_ITEMPICKUP",
        Field(name="item_index", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_ITEMPICKUP, mt)

mt = MessageType("N_TEXT",
        Field(name="text", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_TEXT, mt)

mt = MessageType("N_SAYTEAM",
        Field(name="text", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_SAYTEAM, mt)

mt = MessageType("N_SWITCHNAME",
        Field(name="name", type="string"))
sauerbraten_stream_spec.add_message_type(message_types.N_SWITCHNAME, mt)

mt = MessageType("N_SWITCHMODEL",
        Field(name="playermodel", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_SWITCHMODEL, mt)

mt = MessageType("N_SWITCHTEAM",
        Field(name="team", type="string"))
sauerbraten_stream_spec.add_message_type(message_types.N_SWITCHTEAM, mt)

mt = MessageType("N_MAPCHANGE",
        Field(name="map_name", type="string"),
        Field(name="mode_num", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_MAPCHANGE, mt)

mt = MessageType("N_MAPVOTE",
        Field(name="map_name", type="string"),
        Field(name="mode_num", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_MAPVOTE, mt)

mt = MessageType("N_MASTERMODE",
        Field(name="mastermode", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_MASTERMODE, mt)

mt = MessageType("N_KICK",
        Field(name="target_cn", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_KICK, mt)

mt = MessageType("N_CLEARBANS")
sauerbraten_stream_spec.add_message_type(message_types.N_CLEARBANS, mt)

mt = MessageType("N_SPECTATOR",
        Field(name="target_cn", type="int"),
        Field(name="value", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_SPECTATOR, mt)

mt = MessageType("N_SETTEAM",
        Field(name="target_cn", type="int"),
        Field(name="team", type="string"))
sauerbraten_stream_spec.add_message_type(message_types.N_SETTEAM, mt)

mt = MessageType("N_RECORDDEMO",
        Field(name="value", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_RECORDDEMO, mt)

mt = MessageType("N_CLEARDEMOS",
        Field(name="demonum", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_CLEARDEMOS, mt)

mt = MessageType("N_LISTDEMOS")
sauerbraten_stream_spec.add_message_type(message_types.N_LISTDEMOS, mt)

mt = MessageType("N_GETDEMO",
        Field(name="demonum", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_GETDEMO, mt)

mt = MessageType("N_GETMAP")
sauerbraten_stream_spec.add_message_type(message_types.N_GETMAP, mt)

mt = MessageType("N_NEWMAP",
        Field(name="size", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_NEWMAP, mt)

mt = MessageType("N_SETMASTER",
        Field(name="value", type="int"),
        Field(name="pwdhash", type="string"))
sauerbraten_stream_spec.add_message_type(message_types.N_SETMASTER, mt)

mt = MessageType("N_AUTHTRY",
        Field(name="domain", type="string"),
        Field(name="name", type="string"))
sauerbraten_stream_spec.add_message_type(message_types.N_AUTHTRY, mt)

mt = MessageType("N_AUTHANS",
        Field(name="domain", type="string"),
        Field(name="authid", type="int"),
        Field(name="answer", type="string"))
sauerbraten_stream_spec.add_message_type(message_types.N_AUTHANS, mt)

mt = MessageType("N_DELBOT")
sauerbraten_stream_spec.add_message_type(message_types.N_DELBOT, mt)

mt = MessageType("N_BOTLIMIT",
        Field(name="limit", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_BOTLIMIT, mt)

mt = MessageType("N_BOTBALANCE",
        Field(name="balance", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_BOTBALANCE, mt)

mt = MessageType("N_PAUSEGAME",
        Field(name="value", type="int"))
sauerbraten_stream_spec.add_message_type(message_types.N_PAUSEGAME, mt)



