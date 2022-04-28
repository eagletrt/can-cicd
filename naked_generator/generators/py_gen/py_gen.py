from fileinput import isfirstline
import os
import random
import math

from numpy import isin

from ... import schema as s
import jinja2 as j2
from ...lib import utils
from ... import sanitized_config as c
from ... import schema

__TEMPLATE_PY = os.path.dirname(__file__) + "/template.py.j2"
__TEST_TEMPLATE_PY = os.path.dirname(__file__) + "/test_template.py.j2"

schema_msgs = {}

def generate(filename: str, schema: schema.Schema, output_path: str):
    enums, bitsets = __parse_schema(schema.types, filename)
    # frequencies = __frequencies(network)

    utils.create_subtree(output_path)

    with open(f"{output_path}/{filename}.py", "w") as f:
        f.write(__generate_py(filename, schema.messages, schema.messages_size, enums, bitsets))

    with open(f"{output_path}/test.py", "w") as f:
        f.write(__generate_py_test(filename, schema.messages, schema.messages_size, enums, bitsets))

def __generate_py(filename, messages, messages_size, enums, bitsets):
    endianness_tag = "<" if c.IS_LITTLE_ENDIAN else ">"
    with open(__TEMPLATE_PY, "r") as f:
        skeleton_py = f.read()

    code = j2.Template(skeleton_py).render(
        filename=filename,
        enums=enums,
        bitsets=bitsets,
        messages=messages,
        messages_size=messages_size,
        len=len,
        endianness_tag=endianness_tag,
        params=__params,
        python_type_name=python_type_name,
        utils=utils,
        isinstance=isinstance,
        Number=schema.Number,
        fields_deserialization = __fields_deserialization,
        fields_serialization = __fields_serialization
    )

    return code


def __generate_py_test(filename, messages, messages_size, enums, bitsets):
    endianness_tag = "<" if c.IS_LITTLE_ENDIAN else ">"
    with open(__TEST_TEMPLATE_PY, "r") as f:
        skeleton_py = f.read()

    code = j2.Template(skeleton_py).render(
        filename=filename,
        messages=messages,
        len=len,
        params=__params,
        random_values=__random_values,
        args=__args,
        utils=utils,
    )

    return code


"""
    Utility functions used for template rendering
"""

def __parse_schema(types, prefix):
    """
    Parses generic schema to a more Python friendly one

    The actions performed on the schema are the following:
    - Renaming structs and enums to camel case

    Args:
        schema:

    Returns:
        The structs and other custom types distilled from the schema
    """
    bitsets = []
    enums = []
    for type_name, custom_type in types.items():
        if isinstance(custom_type, schema.Enum):
            custom_type.name = utils.to_camel_case(f"{prefix}_{type_name}",'_')
            enums.append(custom_type)

        if isinstance(custom_type, schema.BitSet):
            custom_type.name = utils.to_camel_case(f"{prefix}_{type_name}" ,'_')
            bitsets.append(custom_type)

    return enums, bitsets


def __packing_schema(name, msg):
    global schema_msgs
    schema_msgs[name] = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    schema = "<" if c.IS_LITTLE_ENDIAN else ">"
    for index, items in msg.items():
        if len(items) > 1:
            schema += "B"
        elif len(items) == 1:
            item = items[0]
            schema += __struct_schema(item)
        schema_msgs[name][index] = schema

    return schema


def __struct_schema(field: schema.Field):
    if isinstance(field.type, schema.BitSet):
        return "B"*math.ceil(field.type.size/8)
    else:
        return __struct_format(field.type)


def __struct_format(number):
    if isinstance(number, schema.Enum):
        return "B"
    elif isinstance(number, schema.Number):
        match number.name:
            case "uint8":
                return "B"
            case "uint16":
                return "H"
            case "uint32":
                return "I"
            case "uint64":
                return "Q"
            case "int8":
                return "b"
            case "int16":
                return "h"
            case "int32":
                return "i"
            case "int64":
                return "q"
            case "float32":
                return "f"
            case "float64":
                return "d"
            case "bool":
                return "B"
            case _:
                raise NotImplementedError(f"Can't convert {number.name} to format for python's pack unpack functions")

def __args(message: schema.Message, variable: str):
    attributes = []
    for field in message.fields:
        attributes.append(f"{{{utils.to_camel_case(message.name,'_')}_{variable}.{field.name}}}")
    return attributes


def __pack_fields(msg: dict):
    fields = []
    for _, items in msg.items():
        if len(items) > 1:
            fields.append(" | ".join([f"self.{item.name} << {item.shift} & 255" for item in items]))
        elif len(items) == 1:
            item = items[0]
            if item.shift == 0:
                if isinstance(item.type, schema.BitSet):
                    for bytes in reversed(range(item.type.byte_size)):
                        fields.append(f"(int(self.{item.name},2) >> {bytes*8}) & 255")
                else:
                    fields.append(f"self.{item.name}")
            else:
                fields.append(f"self.{item.name} << {item.shift} & 255")
    return fields


def __lookup_msg_index(msg_name, field_name, messages_size):
    for index in range(8):
        if field_name in [field.name for field in messages_size[msg_name][index]]:
            return index


def __random_values(fields):
    values = []

    for field in fields:
        if isinstance(field.type, schema.BitSet):
            value = f"{random.randint(0, (2 ** (field.bit_size)-1))}"
            values.append(value)
        elif isinstance(field.type, schema.Enum):
            values.append(f"{random.randint(0, (2 ** (field.bit_size-1)))}")
        elif 'uint' in field.type.name:
            values.append(f"{random.randint(0, (2 ** field.bit_size) - 1)}")
        elif 'int' in field.type.name:
            values.append(f"{random.randint(-2 ** (field.bit_size-1), (2 ** (field.bit_size-1)) - 1)}")
        elif 'float' in field.type.name:
            values.append(f"{random.uniform(0, 1)}")
        else:
            values.append(f"{random.randint(0, 1)}")

    return values


def __custom_unpack_schema(msg_name, msg, field_name):
    schema = "<" if c.IS_LITTLE_ENDIAN else ">"
    max_index = 0
    for index, items in msg.items():
        if field_name in [item.name for item in items]:
            if len(items) > 1:
                schema+="B"
                max_index = index+2
            elif len(items) == 1:
                item = items[0]
                bytes = __struct_schema(item)
                schema+=bytes
                max_index = index+len(bytes)+1
        else:
            schema+='x'
    return schema[0:max_index]


def __params(fields):
    parameters = []
    parameters.append("self")
    for field in fields:
        parameters.append(f"{field.name}: {python_type_name(field)} = None")
    return parameters


def python_type_name(field: schema.Field):
    if 'int' in field.type.name:
        return 'int'
    elif field.type.name == 'float32' or field.type.name == 'float64':
        return 'float'
    elif isinstance(field.type, schema.BitSet):
        return 'bin'
    else:
        return field.type.name


def __bitset_unpack(msg_name, msg, field, index):
    deserialized = []
    bytes = range(field.type.byte_size)
    reversed_bytes = reversed(bytes)
    for (byte, reversed_byte) in zip(bytes, reversed_bytes):
        if isinstance(field.type, schema.BitSet):
            deserialized.append(f"(unpack(\"{ __custom_unpack_schema(msg_name, msg, field.name) }\", data[0:{ index+field.byte_size }])[{ byte }] << { reversed_byte*8 })")
        else:
            deserialized.append(f"{python_type_name(field)}((unpack(\"{ __custom_unpack_schema(msg_name, msg, field.name) }\", data[0:{ index+field.byte_size }])[{ byte }] << { byte*8 }))")
    return deserialized


def __fields_serialization(message, messages_size):
    serializated_fields = []

    if len(message.fields) != 0:
        serializated_fields.append("data = bytearray()")
        msg = messages_size[message.name]
        serializated_fields.append(f"data.extend(pack(\"{__packing_schema(message.name, msg)}\", {', '.join(__pack_fields(msg)) }))")
        serializated_fields.append("return data")
    else:
        serializated_fields.append("return bytearray()")

    return serializated_fields


def __fields_deserialization(message, messages_size):
    deserializated_fields = []

    if len(message.fields) != 0:
        for field in message.fields:
            msg = messages_size[message.name]
            index = __lookup_msg_index(message.name, field.name, messages_size)
            if isinstance(field.type, schema.BitSet):
                deserializated_fields.append(f"self.{field.name} = bin({' | '.join(__bitset_unpack(message.name, msg, field, index))})")
            elif field.shift == 0:
                deserializated_fields.append(f"self.{field.name} = {python_type_name(field)}(unpack(\"{__custom_unpack_schema(message.name, msg, field.name)}\", data[0:{index+field.byte_size}])[0])")
            else:
                deserializated_fields.append(f"self.{field.name} = {python_type_name(field)}((unpack(\"{__custom_unpack_schema(message.name, msg, field.name)}\", data[0:{index+field.byte_size}])[0] & {field.bit_mask}) >> {field.shift})")
    else:
        deserializated_fields.append("pass")

    return deserializated_fields