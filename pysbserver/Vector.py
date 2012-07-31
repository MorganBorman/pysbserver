import math

class vec(object):
    @staticmethod
    def from_yaw_pitch(yaw, pitch):
        x = (-math.sin(yaw)*math.cos(pitch)) 
        y = (math.cos(yaw)*math.cos(pitch))
        z = (math.sin(pitch))
        return vec(x, y, z)
    
    def __init__(self, x, y, z):
        self.v = [x, y, z]
        
    def copy(self):
        return vec(self.x, self.y, self.z)
        
    @property
    def x(self):
        return self.v[0]
    
    @x.setter
    def x(self, value):
        self.v[0] = value
        
    @property
    def y(self):
        return self.v[1]
    
    @y.setter
    def y(self, value):
        self.v[1] = value
        
    @property
    def z(self):
        return self.v[2]
    
    @z.setter
    def z(self, value):
        self.v[2] = value
        
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
        
    def dist(self, vector):
        t = self.copy().sub(vector)
        return t.magnitude()
        
    def mul(self, f):
        self.x *= f
        self.y *= f
        self.z *= f
        return self
    
    def div(self, d):
        self.x /= d
        self.y /= d
        self.z /= d
        return self
    
    def iszero(self):
        return self.x == 0 and self.y == 0 and self.z == 0
    
    def rescale(self, f):
        mag = self.magnitude()
        if mag > math.exp(-6.0):
            self.mul(f / mag)
        return self
    
    def sub(self, value):
        if isinstance(value, vec):
            self.x -= value.x
            self.y -= value.y
            self.z -= value.z
        else:
            self.x -= value
            self.y -= value
            self.z -= value
        return self