"""
An extremely simple synchonous signal/slot handler system.
"""

class Signal(object):
    def __init__(self):
        self.slots = []
        
    def connect(self, slot):
        if not slot in self.slots:
            self.slots.append(slot)
        
    def disconnect(self, slot):
        if slot in self.slots:
            self.slots.remove(slot)
        
    def emit(self, *args, **kwargs):
        for slot in self.slots:
            slot(*args, **kwargs)

class SignalObject(object):
    __class_signals = {}
    __instance_signals = {}
    
    def __init__(self):
        "Initialize each attribute signal."
        for key in dir(self):
            val = self.__getattribute__(key)
            if type(val) == type and issubclass(val, Signal):
                sig = Signal()
                self.__setattr__(key, sig)
                self.__instance_signals[key] = sig
            elif isinstance(val, Signal):
                self.__class_signals[key] = val
                
    def connect_all_instance_signals(self, object_with_slots, prefix="on_"):
        for key, val in self.__instance_signals.items():
            if isinstance(val, Signal):
                expected_slot_name = prefix+key
                
                try:
                    slot = object_with_slots.__getattribute__(expected_slot_name)
                    val.connect(slot)
                except AttributeError:
                    print "Could not connect signal '%s' expected slot '%s' not found." %(key, expected_slot_name)
                    
    def disconnect_all_instance_signals(self, object_with_slots, prefix="on_"):
        for key, val in self.__instance_signals.items():
            if isinstance(val, Signal):
                expected_slot_name = prefix+key
                
                try:
                    slot = object_with_slots.__getattribute__(expected_slot_name)
                    val.disconnect(slot)
                except AttributeError:
                    pass
                    #print "Could not disconnect signal '' expected slot '' not found." %(key, expected_slot_name)
        
import unittest

class TestSignals(unittest.TestCase):

    class TestListModel(SignalObject):
    
        update = Signal
    
        def __init__(self):
            SignalObject.__init__(self)
            self.data_list = []

        def add(self, datum):
            self.data_list.append(datum)
            self.update.emit(self.data_list[:])
            
    class TestListView(object):
        def __init__(self, model):
            self.model = model
            self.model.update.connect(self.on_model_update)
            self.data_cache = []
            
        def on_model_update(self, data_list):
            self.data_cache = data_list

    def setUp(self):
        self.test_model = self.TestListModel()
        self.test_view = self.TestListView(self.test_model)

    def test_signals(self):
        self.test_model.add('foo')
        self.assertEqual(self.test_view.data_cache, ['foo'])
        self.test_model.add('bar')
        self.assertEqual(self.test_view.data_cache, ['foo', 'bar'])
        self.test_model.add('baz')
        self.assertEqual(self.test_view.data_cache, ['foo', 'bar', 'baz'])
        
        self.test_model.update.disconnect(self.test_view.on_model_update)
        
        self.test_model.add('zan')
        self.assertEqual(self.test_view.data_cache, ['foo', 'bar', 'baz'])

if __name__ == '__main__':
    unittest.main()
