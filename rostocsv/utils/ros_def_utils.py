import importlib
import json

import rosidl_runtime_py
from rosidl_runtime_py import get_interface_packages, get_message_interfaces, message_to_ordereddict
from rosidl_runtime_py.utilities import get_message


def save_ros_def_file():
    # Get all interface packages
    packages = get_interface_packages()
    msg_pkgs = get_message_interfaces(packages.keys())
    defs = {}
    for package_name, msg_list in msg_pkgs.items():
        print(f"\nPackage: {package_name}")
        for msg_path in msg_list:
            msg = get_message(f"{package_name}/{msg_path}").get_fields_and_field_types()
            defs[f"{package_name}/{msg_path}"] = msg

    json_file = json.dumps(defs)
    print(json_file)
    with open("ros_def_test.rosdef", 'w') as file:
        file.write(json_file)


save_ros_def_file()