# Protobuf Generator

Sadly, compilated .proto files depends on the protoc compiler version used to compile them.
So, you need to compile it manually, because the protoc version that could be used may differ from yours.

## Compile .proto files

### C++ code generation:

```protoc --proto_path <source-folder> --cpp_out <destination-folder> [network-name].proto```

### Python CODE generation:

```protoc --proto_path <source-folder> --python_out <destination-folder> [network-name].proto```

## TODO:
- [ ] Complete docs