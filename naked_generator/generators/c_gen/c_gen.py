import os
import random

from numpy import append
import jinja2 as j2

from ... import sanitized_config as c
from ...lib import utils
from ... import schema

__TEMPLATE_C = os.path.dirname(__file__) + "/template.c.j2"
__TEMPLATE_H = os.path.dirname(__file__) + "/template.h.j2"
__TEST_TEMPLATE_C = os.path.dirname(__file__) + "/test_template.c.j2"

def generate(filename: str, schema: schema.Schema, output_path: str):
    """
    Generates the source files in the specified output path
    
    Args:
        schema:
        output_path:
        filename:
    """
    enums, bitsets = __parse_schema(schema.types, filename)

    utils.create_subtree(output_path)

    with open(f"{output_path}/{filename}.h", "w") as f:
        f.write(__generate_h(filename, schema.messages, schema.messages_size, enums, bitsets))

    with open(f"{output_path}/test.c", "w") as f:
        f.write(__generate_test_c(filename, schema.messages, enums, bitsets))


def __generate_h(filename, messages, messages_size, enums, bitsets):
    """
    Generates C header file
    """
    endianness_tag = "LITTLE_ENDIAN" if c.IS_LITTLE_ENDIAN else "BIG_ENDIAN"

    with open(__TEMPLATE_H, "r") as f:
        template_h = f.read()

    code = j2.Template(template_h).render(
        bitsets=bitsets,
        enums=enums,
        messages=messages,
        messages_size=messages_size,
        endianness_tag=endianness_tag,
        filename=filename,
        casts=__casts,
        fields_serialization=__fields_serialization,
        fields_deserialization=__fields_deserialization,
        utils=utils,
    )

    return code


def __generate_test_c(filename, messages, enums, bitsets):
    """
    Generates C source file for tests
    """
    with open(__TEST_TEMPLATE_C, "r") as f:
        test_template_c = f.read()

    code = j2.Template(test_template_c).render(
        messages=messages,
        filename=filename,
        len=len,
        printf_cast=__printf_cast,
        printf_arguments_cast=__printf_arguments_cast,
        random_values=__random_values,
        utils=utils,
        buffer_size=__buffer_size,
    )

    return code


def __parse_schema(types, prefix):
    """
    Parses generic schema to a more C friendly one
    
    The actions performed on the schema are the following:
    - Prefixing structs and enums' name to avoid conflicts with other libraries
    
    Args:
        schema:
        prefix:
        
    Returns:
        The structs and other custom types distilled from the schema
    """
    bitsets = []
    enums = []
    for type_name, custom_type in types.items():
        if isinstance(custom_type, schema.Enum):
            custom_type.name = f"{prefix}_{type_name}"
            enums.append(custom_type)

        if isinstance(custom_type, schema.BitSet):
            custom_type.name = f"{prefix}_{type_name}"
            bitsets.append(custom_type)

    return enums, bitsets


def __printf_arguments_cast(message, name: str):
    fields = []
    for field in message.fields:
        if not isinstance(field.type, schema.BitSet):
            fields.append(f"{utils.to_camel_case(message.name,'_')}_{name}.{field.name}")
        else:
            for i in range(0, field.bit_size // 8):
                fields.append(f"{utils.to_camel_case(message.name,'_')}_{name}.{field.name}[{i}]")
    return fields


def __fields(struct):
    return [field_name for field_name, field_type in struct.fields.items() if not isinstance(field_type, s.Padding)]


def __convert(field, index):
    return [f"(data[{index+number_index+1}] << {8*(number_index+1)})" for number_index in range(field.bit_size // 8 - 1)]


def __params(fields):
    return [ f"msg->{field.name} << {field.shift}" if field.shift != 0 else f"msg.{field.name}" for field in fields ]


def __random_values(fields):
    values = []

    for field in fields:
        if isinstance(field.type, schema.BitSet):
            values.append(f"{{ {', '.join([str(random.randint(0, 255)) for _ in range((field.bit_size // 8))])} }}")
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


def __casts(name: str):
    match name:
        case 'uint8':
            return 'uint8_t'
        case 'uint16':
            return 'uint16_t'
        case 'uint32':
            return 'uint32_t'
        case 'uint64':
            return 'uint64_t'
        case 'int8':
            return 'int8_t'
        case 'int16':
            return 'int16_t'
        case 'int32':
            return 'int32_t'
        case 'int64':
            return 'int64_t'
        case 'float32':
            return 'float'
        case 'float64':
            return 'double'
        case 'bool':
            return 'bool'
        case _:
            return utils.to_camel_case(name,"_")


def __printf_cast(fields):
    casts = []
    for field in fields:
        if isinstance(field.type, schema.Number):
            match field.type.name:
                case 'float32':
                    casts.append('%f')
                case 'float64':
                    casts.append('%lf')
                case 'int8':
                    casts.append('%hhd')
                case 'int16':
                    casts.append('%hd')
                case 'int32':
                    casts.append('%d')
                case 'int64':
                    casts.append('%ld')
                case 'uint8':
                    casts.append('%hhu')
                case 'uint16':
                    casts.append('%hu')
                case 'uint32':
                    casts.append('%u')
                case 'uint64':
                    casts.append('%lu')
                case 'bool':
                    casts.append('%d')
        elif isinstance(field.type, schema.Enum):
            casts.append("%d")
        elif isinstance(field.type, schema.BitSet):
            casts.append(".".join(["%hhx"] * (field.bit_size // 8)))
    return casts


def __float_deserialize(field, index):
    return [f"data[{index+byte_index}]" for byte_index in range(field.bit_size // 8)]


def __fields_serialization(index, fields):
    serializated_fields = []

    if fields:
        if len(fields) == 1 and fields[0].bit_size >= 8:
            field = fields[0]
            if isinstance(field.type, schema.BitSet):
                for bitset_index in range(field.bit_size // 8):
                    serializated_fields.append(f"data[{index+bitset_index}] = msg->{field.name}[{bitset_index}];")
            elif isinstance(field.type, schema.Number) and (field.type.name == 'float32' or field.type.name == 'float64'):
                for byte_index in range(field.bit_size // 8):
                    serializated_fields.append(f"data[{index+byte_index}] = (({__casts(field.type.name)}_t) msg->{field.name}).bytes[{byte_index}];")
            elif field.bit_size > 8:
                serializated_fields.append(f"data[{index}] = msg->{field.name} & 255;")
                for number_index in range(1, field.bit_size // 8):
                    serializated_fields.append(f"data[{index+number_index}] = (msg->{field.name} >> {number_index*8}) & 255;")
            else:
                serializated_fields.append(f"data[{index}] = msg->{field.name};")
        else:
            serializated_fields.append(f"data[{index}] = {' | '.join(__params(fields))};")

    return serializated_fields


def __fields_deserialization(index, fields):
    deserializated_fields = []

    if fields:
        if len(fields) == 1 and fields[0].bit_size >= 8:
            field = fields[0]
            if isinstance(field.type,schema.BitSet):
                for bitset_index in range(field.bit_size // 8):
                    deserializated_fields.append(f"msg->{field.name}[{bitset_index}] = data[{index+bitset_index}];")
            elif isinstance(field.type, schema.Number) and (field.type.name == 'float32' or field.type.name == 'float64'):
                deserializated_fields.append("msg->{} = ((float_t) {}).value;".format(field.name,"{"+str(', '.join(__float_deserialize(field, index)))+"}"))
            elif field.bit_size > 8:
                deserializated_fields.append(f"msg->{field.name} = data[{index}] | {' | '.join(__convert(field, index))};")
            else:
                deserializated_fields.append(f"msg->{field.name} = data[{index}];")
        else:
            for field in fields:
                if field.type.name != "bool":
                    deserializated_fields.append(f"msg->{field.name} = ({__casts(field.type.name)}) ((data[{index}] & {field.bit_mask}) >> {field.shift});")
                else:
                    deserializated_fields.append(f"msg->{field.name} = (data[{index}] & {field.bit_mask}) >> {field.shift};")

    return deserializated_fields


def __buffer_size(message_name):
    return utils.to_snake_case(f"{message_name}_size").upper()