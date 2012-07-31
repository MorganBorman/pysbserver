class Field(object):
    def __init__(self, name="", type="int"):
        self.name = name
        self.type = type

    def read(self, stream_object, type_method_mapping, peek=False):
        "Returns a tuple ('field name', field_data)"
        return (self.name, type_method_mapping[self.type](stream_object, peek))
    
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
            field_name, field_datum = field.read(stream_object, type_method_mapping)
            message_datum[field_name] = field_datum
            
        return message_datum
        
class IteratedFieldCollection(object):
    def __init__(self, name, count_field, field_collection):
        self.name = name
        self.count_field = count_field
        self.field_collection = field_collection

    def read(self, stream_object, type_method_mapping):
        "Returns a tuple ('field name', [{from field collection},])"
        _, field_count = self.count_field.read(stream_object, type_method_mapping)
        
        field_data = []
        
        for fc in range(field_count):
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
            
        return (self.name, field_data)
        
class MessageType(FieldCollection):
    def __init__(self, message_name, *fields):
        self.message_name = message_name
        FieldCollection.__init__(self, *fields)
        
    def read(self, stream_object, type_method_mapping):
        "Returns a tuple ('message_name', {from field collection})"
        return (self.message_name, FieldCollection.read(self, stream_object, type_method_mapping))
    
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
            
            if message_type_id in self.message_types.keys():
                message_name, datum = self.message_types[message_type_id].read(stream_object, self.type_method_mapping)
                datum.update(state)
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

