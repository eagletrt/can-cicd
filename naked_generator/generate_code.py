import pathlib

from .generators.py_gen import py_gen
from .generators.c_gen import c_gen
from .lib.network import Network

def generate_code(file_name, schema, output_dir_network: pathlib.Path):

    if True:  # Generate python
        output_path_py = output_dir_network / "py"
        py_gen.generate(file_name, schema, output_path_py)
        print(f"Generated Python code into {output_path_py}")

    if True:  # Generate c
        output_path_c = output_dir_network / "c"
        c_gen.generate(file_name, schema, output_path_c)
        print(f"Generated C code into {output_path_c}")

    print("")