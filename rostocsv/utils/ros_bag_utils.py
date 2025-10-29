import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import yaml
from mcap.exceptions import DecoderNotFoundError
from mcap.reader import make_reader
from mcap_ros2.reader import read_ros2_messages
from rosidl_runtime_py.utilities import get_message


class ROSAnalysisResult:

    def __init__(self, topics):
        self.topics = topics

def _get_bag_mcap_file(bag_file_dir):
    try:
        with open(f'{bag_file_dir}/metadata.yaml', 'r') as file:
            metadata = yaml.safe_load(file)
        return metadata['rosbag2_bagfile_information']['relative_file_paths'][0]

    except FileNotFoundError:
        print("Error: config.yaml not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")

def get_topics(bag_file_dir, use_cache_file) -> ROSAnalysisResult:
    try:
        with open(f'{bag_file_dir}/metadata.yaml', 'r') as file:
            metadata = yaml.safe_load(file)
        result = {}
        for t in metadata['rosbag2_bagfile_information']['topics_with_message_count']:
            name = t['topic_metadata']['name']
            type_str = t['topic_metadata']['type']
            if name in ("/events/write_split", "/parameter_events"):
                continue
            try:
                if not use_cache_file:
                    print("Attempting to load from the ROS workspace")
                    msg = get_message(type_str).get_fields_and_field_types()
                else:
                    file = open("utils/ros_def_test.json", 'r')
                    data = json.load(file)
                    msg = data[type_str]
                result[name] = msg
            except Exception as e:
                print(f"Could not load {type_str}: {e}")
        return ROSAnalysisResult(topics=result)
    except FileNotFoundError:
        print("Error: config.yaml not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")



def export(bag_file_dir, topics, export_dir) -> str:
    records = []
    bag_file = f"{bag_file_dir}/{_get_bag_mcap_file(bag_file_dir)}"
    t = datetime.now()
    csv_file = f"{export_dir}/{t.month}_{t.day}_{t.year}__{t.hour}_{t.minute}_{t.second}.csv"
    ros_topics = list(map(lambda x: x.split(".")[0], topics))
    for msg in read_ros2_messages(bag_file, topics=ros_topics):
        ros_msg = msg.ros_msg
        for attr in topics:
            topic = attr.split(".")[0]
            topic_data = attr.split(".")[1]
            if not msg.channel.topic == topic:
                continue

            data = getattr(ros_msg, topic_data, None)
            if data is not None:
                ts_ns = msg.publish_time_ns
                ts_sec = ts_ns / 1e9
                ts_str = datetime.fromtimestamp(ts_sec, tz=ZoneInfo("America/New_York")).strftime(
                    "%m/%d/%y | %I:%M:%S %p")

                records.append({
                    "timestamp_ns": ts_ns,
                    "timestamp_sec": ts_sec,
                    "timestamp": str(ts_str),
                    attr: data,
                })

    # Build DataFrame
    df = pd.DataFrame(records)

    if df.empty:
        print("⚠️ No relevant messages found.")
    else:
        # Floor timestamps to the nearest second
        df["timestamp_sec_floor"] = df["timestamp_sec"].astype(int)

        # Group by floored second and take the mean of each value
        agg = {
            "timestamp": "first"
        }
        for attr in topics:
            agg[attr] = "mean"
        grouped = df.groupby("timestamp_sec_floor").agg(agg).reset_index()
        grouped.to_csv(csv_file, index=False)

        print(f"Wrote {len(grouped)} grouped records to {csv_file}")
    return csv_file