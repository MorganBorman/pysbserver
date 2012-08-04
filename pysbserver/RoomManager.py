from Room import Room

class RoomManager(object):
    """The room manager keeps track of the current rooms, moving players between rooms,
    and the creation of new rooms."""
    
    # The lobby is a room which always exists and to which new players are added
    lobby = Room("lobby")
    
    rooms = {'lobby': lobby}
    
    def __init__(self):
        pass
    
    def on_client_connected(self, client):
        #TODO: consider logic here to use the pwdhash to select a room to join
        self.lobby.add_client(client)
        
    def update_rooms(self):
        for room in self.rooms.values():
            room.update_room()
            
    def sendpackets(self, force=False):
        flush = False
        for room in self.rooms.values():
            flush = room.sendpackets(force) and flush
        return flush