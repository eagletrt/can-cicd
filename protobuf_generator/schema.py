import math
import abc


"""
    struct format = {
        "name": "struct_name",
        "fields": {
            "field_name": "field_type",
            ...
        }
        ...
    }
    
    enum format = {
        "name": "enum_name",
        "items": [ITEM_NAME, ...]
    }
"""

proto_types = {}

class Schema:
    def __init__(self, schema):

        global proto_types
        proto_types = {
            "bool": "bool",
            "float32": "float",
            "float64": "double",
            "int8": "int32",
            "int16": "int32",
            "int32": "int32",
            "int64": "int64",
            "uint8": "uint32",
            "uint16": "uint32",
            "uint32": "uint32",
            "uint64": "uint64"
        }

        self._types = []
        self._structs = []
        if schema is not None and isinstance(schema, dict):
            for type_name, type_descriptrion in schema["types"].items():
                if type_descriptrion["type"] == "enum":
                    self._types.append(Enum(type_name, type_descriptrion["items"]))
                elif type_descriptrion["type"] == "bitset":
                    self._types.append(BitSet(type_name, type_descriptrion["items"]))
                else:
                    raise Exception(f"{type_descriptrion['type'].capitalize()} type not yet supported")
            for struct_name, struct_descriptrion in schema["structs"].items():
                self._structs.append(Struct(struct_name, struct_descriptrion))
        else:
            raise Exception("Schema is either None or not a dict")

    @property
    def structs(self):
        return self._structs

    @property
    def types(self):
        return self._types


class Type(abc.ABC):
    def __init__(self, name, custom_type):
        self.name = name
        self.type = custom_type

    @abc.abstractmethod
    def add_to_proto_types(self, name, custom_type):
        pass


class Struct:
    def __init__(self, name, fields):
        self.name=name
        self.fields = [(field_index+1, field_name, proto_types[field_type]) for field_index, (field_name, field_type) in enumerate(fields.items())]


@Type.register
class Enum(Type):
    def __init__(self, name, custom_type: list):      
        enum_custom_type = [(item_name, item_index) for item_index, item_name in enumerate(custom_type)]
        self.add_to_proto_types(name, enum_custom_type)
        super().__init__(name, enum_custom_type)
    
    def add_to_proto_types(self, name, custom_type):
        global proto_types
        if name not in proto_types:
            proto_types[name] = name


class BitSet(Type):
    def __init__(self, name, custom_type: list):
        bitset_custom_type = proto_types["uint32"] if math.ceil(len(custom_type))/8 <= 4 else proto_types["uint64"]
        self.add_to_proto_types(name, bitset_custom_type)        
        super().__init__(name, bitset_custom_type)
    
    def add_to_proto_types(self, name, custom_type):
        global proto_types
        if name not in proto_types:
            proto_types[name] = custom_type


class Number(Type):
    def __init__(self, name, custom_type: str):
        number_custom_type = proto_types[custom_type]
        super().__init__(name, number_custom_type)