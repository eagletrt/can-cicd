import sys

# from .get_data import get_data_from_network
from .schema import Schema
from .generate_code import generate_code
from . import sanitized_config as c
from .lib import utils


def main():
    print("====== naked-generator ======")
    print("")

    networks_dir, output_dir = utils.read_args(sys.argv)
    networks = utils.load_networks(networks_dir, c.NETWORK_VALIDATION_SCHEMA)

    for network in networks:
        output_dir_network = output_dir / network.name

        schema = Schema(network)
        generate_code(network.name, schema, output_dir_network)


if __name__ == "__main__":
    main()
