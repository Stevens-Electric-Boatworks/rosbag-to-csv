import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import yaml
from mcap_ros2.reader import read_ros2_messages

class ROSAnalysisResult:

    def __init__(self, topics):
        self

def get_bag_file(bag_file_dir) -> tuple:
    try:
        with open(f'{bag_file_dir}/metadata.yaml', 'r') as file:
            metadata = yaml.safe_load(file)
        return metadata['rosbag2_bagfile_information']['relative_file_paths'][0]

    except FileNotFoundError:
        print("Error: config.yaml not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")


def analyse(bag_file_dir):
    ros_topics = []

    bag_file = f"{bag_file_dir}/{get_bag_file(bag_file_dir)}"

    for msg in read_ros2_messages(bag_file):
        ros_msg = msg.ros_msg

        msg_data = dir(ros_msg)

        for data in msg_data:
            datas = ()
            if data.startswith("_"):
                continue
            datas += (data, )
        ros_topics.append((msg.channel.topic, msg_data))

    return ROSAnalysisResult(ros_topics)
