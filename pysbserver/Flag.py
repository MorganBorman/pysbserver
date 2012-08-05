

class Flag(object):
    id = 0
    version = 0
    spawn = 0
    owner = None
    drop_location = None
    
    def __init__(self):
        pass
    
    @property
    def dropped(self):
        return self.owner is None and self.drop_location is not None