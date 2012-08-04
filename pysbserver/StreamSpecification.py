import traceback

DEBUG = False

if DEBUG: import Constants

class Field(object):
    def __init__(self, name="", type="int"):
        self.name = name
        self.type = type

    def read(self, stream_object, type_method_mapping, peek=False):
        if DEBUG: print "\tReading field:", self.name
        
        "Returns a tuple ('field name', field_data)"
        try:
            value = type_method_mapping[self.type](stream_object, peek)
            if DEBUG: print "\t\tRead value:", value
            return (self.name, value)
        except:
            print "Exception occurred while reading field '%s'" % self.name
            raise
    
class RawField(object):
    def __init__(self, name="", size=1):
        self.name = name
        self.size = size
        
    def read(self, stream_object, type_method_mapping):
        return (self.name, type_method_mapping['stream_data'](stream_object, self.size))
        
class FieldCollection(object):
    def __init__(self, *fields):
        self.fields = fields

    def read(self, stream_object, type_method_mapping):
        "Returns a dictionary {'field_name': field_data}"
        message_datum = {}
    
        for field in self.fields:
            if isinstance(field, ConditionalFieldCollection):
                field_data = field.read(stream_object, type_method_mapping)
                message_datum.update(field_data)
            else:
                field_name, field_datum = field.read(stream_object, type_method_mapping)
                message_datum[field_name] = field_datum
            
        return message_datum
        
class IteratedFieldCollection(object):
    def __init__(self, name, count, field_collection):
        self.name = name
        self.count = count
        self.field_collection = field_collection

    def read(self, stream_object, type_method_mapping):
        "Returns a tuple ('field name', [{from field collection},])"
        if isinstance(self.count, Field):
            _, field_count = self.count.read(stream_object, type_method_mapping)
        else:
            field_count = int(self.count)
            
        field_data = []
        
        for fc in range(field_count): #@UnusedVariable
            field_data.append(self.field_collection.read(stream_object, type_method_mapping))
            
        return (self.name, field_data)

class TerminatedFieldCollection(object):
    def __init__(self, name, terminator_field, terminator_comparison, field_collection):
        self.name = name
        self.terminator_field = terminator_field
        self.terminator_comparison = terminator_comparison
        self.field_collection = field_collection

    def read(self, stream_object, type_method_mapping):
        "Returns a tuple ('field name', field_data)"
        
        field_data = []
        
        _, term_value = self.terminator_field.read(stream_object, type_method_mapping, peek=True)
        while(self.terminator_comparison(term_value)):
            field_data.append(self.field_collection.read(stream_object, type_method_mapping))
            _, term_value = self.terminator_field.read(stream_object, type_method_mapping, peek=True)
            
        # throw away the terminator once it is found
        _, term_value = self.terminator_field.read(stream_object, type_method_mapping, peek=False)
            
        return (self.name, field_data)
    
class ConditionalFieldCollection(object):
    def __init__(self, predicate, predicate_comparison, consequent, alternative, peek_predicate=False):
        self.predicate = predicate
        self.predicate_comparison = predicate_comparison
        self.consequent = consequent
        self.alternative = alternative
        self.peek_predicate = peek_predicate
        
    def read(self, stream_object, type_method_mapping):
        "Returns a dictionary {'field_name': field_data}"
        
        _, value = self.predicate.read(stream_object, type_method_mapping, peek=self.peek_predicate)
        if self.predicate_comparison(value):
            return self.consequent.read(stream_object, type_method_mapping)
        else:
            return self.alternative.read(stream_object, type_method_mapping)
        
class MessageType(FieldCollection):
    def __init__(self, message_name, *fields):
        self.message_name = message_name
        FieldCollection.__init__(self, *fields)
        
    def read(self, stream_object, type_method_mapping):
        "Returns a tuple ('message_name', {from field collection})"
        try:
            return (self.message_name, FieldCollection.read(self, stream_object, type_method_mapping))
        except:
            print "Exception occurred in MessageType '%s'" % self.message_name
            raise
    
class StreamStateModifierType(FieldCollection):
    def __init__(self, *fields):
        FieldCollection.__init__(self, *fields)
    
    def read(self, stream_object, type_method_mapping, stream_state):
        stream_state.update(FieldCollection.read(self, stream_object, type_method_mapping))
    
class StreamSpecification(object):
    message_types = {}
    container_types = {}
    state_modifier_types = {}
    
    StreamClass = object
    type_method_mapping = {}
    default_state = {}
    message_type_id_type = ""

    def __init__(self, StreamClass, type_method_mapping, default_state, message_type_id_type):
        self.StreamClass = StreamClass
        self.type_method_mapping = type_method_mapping
        self.default_state = default_state
        self.message_type_id_type = message_type_id_type
        
        # indexed by message type identifier
        self.message_types = {}
        self.container_types = {}
        self.state_modifier_types = {}
        
    def add_message_type(self, message_type_id, message_type):
        self.message_types[message_type_id] = message_type
        
    def add_container_type(self, message_type_id, container_type):
        self.container_types[message_type_id] = container_type
        
    def add_state_modifier_type(self, message_type_id, state_modifier_type):
        self.state_modifier_types[message_type_id] = state_modifier_type
        
    def read(self, raw_stream, initial_state):
        state = {}
        state.update(self.default_state)
        state.update(initial_state)
    
        read_data = []
        
        stream_object = self.StreamClass(raw_stream)
        
        while(not stream_object.empty()):
            message_type_id = self.type_method_mapping[self.message_type_id_type](stream_object)
            
            if DEBUG: print "Reading message:", Constants.message_types.by_value(message_type_id)
            
            if message_type_id in self.message_types.keys():
                message_name, datum = self.message_types[message_type_id].read(stream_object, self.type_method_mapping)
                datum.update(state)
                if DEBUG: print (message_name, datum)
                read_data.append((message_name, datum))
            elif message_type_id in self.container_types.keys():
                data = self.container_types[message_type_id].read(stream_object, self.type_method_mapping, state)
                read_data.extend(data)
            elif message_type_id in self.state_modifier_types.keys():
                self.state_modifier_types[message_type_id].read(stream_object, self.type_method_mapping, state)

        return read_data

class StreamContainerType(StreamSpecification):
    def __init__(self, StreamClass, type_method_mapping, default_state, message_type_id_type, field_collection, length_field):
        StreamSpecification.__init__(self, StreamClass, type_method_mapping, default_state, message_type_id_type)
        self.field_collection = field_collection
        self.length_field = length_field
        
    def read(self, stream_object, type_method_mapping, initial_state):
        state = {}
        state.update(initial_state)
        state.update(self.field_collection.read(stream_object, type_method_mapping))
        
        _, stream_length = self.length_field.read(stream_object, type_method_mapping)
        
        stream_data = type_method_mapping['stream_data'](stream_object, stream_length)
        
        return StreamSpecification.read(self, stream_data, state)

