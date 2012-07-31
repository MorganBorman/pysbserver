import struct
import collections

class CubeDataStream(object):
    def __init__(self, strdata=""):
        self.data = bytearray(map(ord, strdata))
        
    @staticmethod
    def pack_format(fmt, data):
        cds = CubeDataStream()
        
        i = 0
        for f in fmt:
            if f == "i":
                cds.putint(data[i])
            elif f == "u":
                cds.putuint(data[i])
            elif f == "f":
                cds.putfloat(data[i])
            elif f == "s":
                cds.putstring(data[i])
            elif f == "r":
                cds.write(data[i])
            i += 1
            
        return cds
    
    def write(self, data):
        if isinstance(data, collections.Iterable):
            self.data.extend(data)
        elif isinstance(data, CubeDataStream):
            self.data.extend(data.data)
        else:
            self.data.append(data)
        
    def clear(self):
        self.data = bytearray()
        
    def empty(self):
        return len(self.data) == 0
        
    def __str__(self):
        return str(self.data)
    
    def __len__(self):
        return len(self.data)
    
    def read(self, n, peek=False):
        try:
            if n == 1:
                return self.data[0]
            else:
                return self.data[:n]
        finally:
            if not peek: del self.data[:n]
            
    def putint(self, i):
        i = int(i)
        if -127 < i and i < 128:
            self.write(i&0xFF)
        elif -0x8000 < i and i < 0x8000 :
            self.write(0x80)
            self.write(i&0xFF)
            self.write(i>>8&0xFF)
        else:
            self.write(0x81)
            self.write(i&0xFF)
            self.write((i>>8)&0xFF)
            self.write((i>>16)&0xFF)
            self.write((i>>24)&0xFF)

    def putuint(self, n):
        n = long(n)
        if(n < 0 or n >= (1<<21)):
            self.write(0x80 | (n & 0x7F))
            self.write(0x80 | ((n >> 7) & 0x7F))
            self.write(0x80 | ((n >> 14) & 0x7F))
            self.write(n >> 21)
        elif(n < (1<<7)):
            self.write(n)
        elif(n < (1<<14)):
            self.write(0x80 | (n & 0x7F))
            self.write(n >> 7)
        else:
            self.write(0x80 | (n & 0x7F))
            self.write(0x80 | ((n >> 7) & 0x7F))
            self.write(n >> 14)
        
    def putfloat(self, f):
        f = float(f)
        self.write(bytearray(map(ord, struct.pack('<f', f))))
        
    def putstring(self, s):
        self.write(bytearray(map(ord, s)))
        self.write(0)
        
    def getint(self, peek=False):
        c = self.read(1, peek)
        
        if c == 0x80:
                t = str(self.read(3 if peek else 2, peek))
                if peek: t = t[1:]
                return struct.unpack('h', t)[0]
        elif c == 0x81:
                t = str(self.read(5 if peek else 4, peek))
                if peek: t = t[1:]
                return struct.unpack('i', t)[0]
        else:
                return struct.unpack('b', chr(c))[0]
        
    def getuint(self, peek=False):
        n = self.read(1)
        if(n & 0x80):
            n += (self.read(1, peek) << 7) - 0x80;
            if(n & (1<<14)):
                n += (self.read(1, peek) << 14) - (1<<14)
            if(n & (1<<21)): 
                n += (self.read(1, peek) << 21) - (1<<21)
            if(n & (1<<28)): 
                n |= -1<<28
        return n;
        
    def getfloat(self, peek=False):
        return struct.unpack('<f', str(self.read(4, peek)))[0]
        
    def getstring(self, peek=False):
        try:
            return str(self.read(self.data.index(chr(0)), peek))
        finally:
            self.read(1, peek) # Throw away the null terminator
        
import unittest

class TestCubeDataStreams(unittest.TestCase):

    def setUp(self):
        pass

    def test_integers(self):
        cds = CubeDataStream("")
        for i in range(-10000, 10000, 7):
            cds.putint(i)
            self.assertEqual(cds.getint(), i)
        
    def test_unsigned_integers(self):
        cds = CubeDataStream("")
        for i in range(0, 20000, 7):
            cds.putuint(i)
            self.assertEqual(cds.getuint(), i)
            
    def test_strings(self):
        cds = CubeDataStream("")
        animals = ["cat", "dog", "rabbit", "hamster", "frog"]
        
        order = []
        
        for animal in animals:
            cds.putstring(animal)
            order.append(animal)
            
        while len(order) > 0:
            animal = cds.getstring()
            self.assertEqual(animal, order.pop(0))
            
    def test_floats(self):
        cds = CubeDataStream("")
        
        # Not all floats will encode to IEEE 754 and back and be equal
        floats = [-355.3233947753906, 352332.09375, 323333.90625]
        
        order = []
        
        for f in map(float, floats):
            cds.putfloat(f)
            order.append(f)
            
        while len(order) > 0:
            f = cds.getfloat()
            self.assertEqual(f, order.pop(0))
        

if __name__ == '__main__':
    unittest.main()

        
