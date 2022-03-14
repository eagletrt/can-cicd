from .lib import utils
from .schema import Schema
from .generators.proto_gen import generate

def compile_schema(schema_path, output_path):
    # Load schema
    schema = Schema(schema=utils.load_json(schema_path))
    
    file_name = schema_path.parent.name.lower()

    if True: # Generate proto
        generate(schema, file_name, output_path)
        print(f"Generated {file_name}.proto for Protocol Buffers into {output_path}")