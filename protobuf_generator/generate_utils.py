from .generators.utils_gen.utils_gen import generate

def generate_utils(network, schema, utils_dir_network):

    utils_dir_network = utils_dir_network / "cpp"

    file_name = network.name
    
    if True: # Generate utils
        generate(schema, network, file_name, utils_dir_network)
        print(f"Generated {file_name}_utils.h into {utils_dir_network}")