import importlib
import json
from datetime import datetime

import rosidl_runtime_py
from rosidl_runtime_py import get_interface_packages, get_message_interfaces, message_to_ordereddict
from rosidl_runtime_py.utilities import get_message


def save_ros_def_file(export_dir):
    t = datetime.now()
    file_name = f"{export_dir}/rosdef_export_{t.month}_{t.day}_{t.year}__{t.hour}_{t.minute}_{t.second}.rosdef"
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
    with open(file_name, 'w') as file:
        file.write(json_file)
    return file_name