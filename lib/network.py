import os
import pathlib

from . import utils


def load_network(path):
    if not os.path.exists(path):
        return {}
    return Network(path, path.split("/")[-2])


class Network:
    def __init__(
        self,
        name: str,
        path: pathlib.Path = None,
        validation_schema: str = None,
        ids_path: str = None,
        ids_validation_schema: str = None,
    ):
        self.path = None
        self.ids_path = None
        self.name = name
        self.messages = {}
        self.types = {}
        self.topics = {}
        self.name_index = {}
        self.frequencies = {}
        self.version = None
        self.max_payload_size = None

        if path:
            self.load(path, validation_schema)

        if ids_path:
            self.load_ids(ids_path, ids_validation_schema)

    def load(self, path: pathlib.Path, validation_schema: str = None):
        self.path = path
        network = utils.load_json(self.path, validation_schema)
        self.version = network["network_version"]
        self.max_payload_size = network["max_payload_size"]

        self.types = network["types"] if "types" in network else {}

        for message in network["messages"]:
            message_name = message.pop("name")
            split_senders = message.get("split_senders", False)
            sending_devices = message["sending"]
            message_frequency = message.get("frequency", -1)
            self.frequencies[message_name] = message_frequency
            if "topic" in message:
                self.topics[message["topic"]] = None
            else:
                self.topics["FIXED_IDS"] = None
                message["topic"] = "FIXED_IDS"
            if split_senders and len(sending_devices) > 1:
                for device_id, device_name in enumerate(sending_devices):
                    msg = message.copy()
                    msg["sending"] = [device_name]
                    generated_msg_name = f"{message_name}_{device_id}"
                    self.messages[generated_msg_name] = msg
            else:
                self.messages[message_name] = message

    def load_ids(self, path: str, validation_schema: str = None):
        self.ids_path = path
        network_ids = utils.load_json(self.ids_path)  # , validation_schema) # TODO: fix
        assert (
            network_ids["network_version"] == self.version
        ), f"Version mismatch between {self.path} and {self.ids_path}"

        for topic_name, topic_contents in sorted(network_ids["topics"].items()):
            # sorted() NEEDED for consistency across runs
            if "id" in topic_contents:
                self.topics[topic_name] = topic_contents["id"]
            else:
                self.topics[topic_name] = None
            for message_name, message_contents in sorted(
                topic_contents["messages"].items()
            ):
                # sorted() NEEDED for consistency across runs
                self.messages[message_name]["id"] = message_contents["id"]

    def merge_with(self, network: "Network"):
        if isinstance(network, Network):
            for m1 in network.contents:
                m2 = self.get_message_by_name(m1["name"])
                if m2:  # message name conflict
                    print(
                        "Message with same name {0} found in networks {1} and {2}".format(
                            m1["name"], self.name, network.name
                        )
                    )
                    print(
                        "Checking if the two messages are actually the same message..."
                    )
                    for (_, m1value), (_, m2value) in zip(m1.items(), m2.items()):
                        # check if messages are actually the same one
                        if m1value != m2value:
                            raise Exception(
                                "Found two incompatible messages with same name {0} in networks {1}, {2}".format(
                                    m1["name"], self.name, network.name
                                )
                            )
                    print("Messages found to be the same, the merge will continue")
            self.messages += network.contents
        else:
            raise Exception("Parameter network isn't a Network instance")
        self.name = self.name + "_" + network.name

    def get_messages(self) -> {}:
        return self.messages

    def get_topics(self) -> {}:
        return self.topics

    def get_messages_by_topic(self, topic):
        """
        Very resource-heavy, can be optimized with index
        """
        messages = {}
        for message_name, message_contents in self.messages.items():
            if message_contents["topic"] != topic:
                continue
            messages[message_name] = message_contents

        return messages

    def get_messages_with_fixed_id(self) -> {}:
        """
        Very resource-heavy, can be optimized with index
        """
        messages = {}
        for message_name, message_contents in self.messages.items():
            if "fixed_id" in message_contents:
                messages[message_name] = message_contents

        return messages

    def get_reserved_ids(self) -> {}:
        """
        Very resource-heavy, can be optimized with index
        """
        ids = {}
        for message_name, message_contents in self.get_messages_with_fixed_id().items():
            ids[message_name] = message_contents["fixed_id"]

        return ids

    def get_message_id(self, name) -> {}:
        try:
            return self.messages[name]
        except KeyError:
            return {}

    def get_types(self):
        return self.types

    def get_name(self):
        return self.name

    def get_frequencies(self):
        return self.frequencies
