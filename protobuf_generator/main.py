import subprocess
import os
import sys
import pathlib

from shutil import which
from .lib import utils
from .compile_schema import compile_schema
from .generators.utils_gen.utils_gen import generate_utils


def get_protoc_executable():
  if "PROTOC" in os.environ and os.path.exists(os.environ["PROTOC"]):
    protoc = os.environ["PROTO"]
  else:
    protoc = which("protoc")

  if not protoc:
    raise RuntimeError('Procol buffer not found, please install it using given requirements.txt')
  else:
    return protoc


def read_args(argv):
    # TODO: standardize
    if len(argv) != 4 or argv[1] in ["--help", "-h"]:
        raise ValueError("Usage: python3 main.py <networks_path> <id_path> <naked_path> <output_path>")

    networks_dir = pathlib.Path(argv[1])
    id_dir = pathlib.Path(argv[2])
    output_dir = pathlib.Path(argv[3])

    if not networks_dir.exists() or not networks_dir.is_dir():
        raise ValueError(f"Path {networks_dir} does not exist or it is not a directory")

    if not id_dir.exists() or not id_dir.is_dir():
        raise ValueError(f"Path {id_dir} does not exist or it is not a directory")

    if output_dir.is_file():
        raise ValueError(f"Path {output_dir} is a file")

    return networks_dir, id_dir, output_dir


def main():
    print("====== flatbuf-generator ======")
    print("")

    networks_dir, id_dir, output_dir = read_args(sys.argv)
    networks = utils.load_networks(networks_path=networks_dir, ids_path=id_dir)

    for network in networks:
        proto_dir = output_dir / "dev"
        output_dir_network = output_dir / "gen" / network.name
        utils_dir_network = output_dir_network

        schema = compile_schema(network, proto_dir)
        compile_proto_files(proto_dir, output_dir_network, network.name)

        generate_utils(schema, network, network.name, utils_dir_network)

        print("")



def compile_proto_files(proto_dir, output_dir_network, network_name):
  python_dir_network = output_dir_network / "python"
  utils.create_subtree(python_dir_network)
  
  cpp_dir_network = output_dir_network / "cpp"
  utils.create_subtree(cpp_dir_network)
  
  if subprocess.call([get_protoc_executable(), "--proto_path", str(proto_dir) ,"--python_out", str(python_dir_network), str(f"{network_name}.proto")]) != 0:
    raise RuntimeError("Proto compilation failed for Python")
  else:
    print(f"Generated {network_name}_pb2.py for Python into {python_dir_network}")
  
  if subprocess.call([get_protoc_executable(), "--proto_path", str(proto_dir) ,"--cpp_out", str(cpp_dir_network), str(f"{network_name}.proto")]) != 0:
    raise RuntimeError("Proto compilation failed for C++")
  else:
    print(f"Generated {network_name}.pb.h and {network_name}.pb.cc for C++ into {cpp_dir_network}")


if __name__ == "__main__":
  main()