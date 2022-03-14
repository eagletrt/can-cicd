import os
import jinja2 as j2
from ..lib import utils
from ..schema import Schema, BitSet, Enum

__PROTO_TEMPLATE_ = os.path.dirname(__file__) + "/template.proto.j2"


def generate(schema: Schema, filename, output_path):
    bitsets, enums, structs = __parse_schema(schema)
    utils.create_subtree(output_path)
    with open(f"{output_path}/{filename}.proto", "w") as f:
        f.write(__generate_proto(filename, enums, bitsets, structs))

def __generate_proto(filename, enums, bitsets, structs):
    with open(__PROTO_TEMPLATE_, "r") as f:
        skeleton_py = f.read()

    code = j2.Template(skeleton_py).render(
        filename=filename,
        bitsets=bitsets,
        enums=enums,
        structs=structs,
        # isinstance=isinstance,
        # Type=Type,
        # enumerate=enumerate,
        # range=range,
        # zip=zip,
        # utils=utils
    )

    return code


def __parse_schema(schema: Schema):
    bitsets = [type for type in schema.types if isinstance(type, BitSet)]
    enums = [type for type in schema.types if isinstance(type, Enum)]
    structs = [struct for struct in schema.structs]
    
    return bitsets, enums, structs