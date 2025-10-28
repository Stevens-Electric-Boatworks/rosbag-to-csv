import yaml
from mcap.exceptions import DecoderNotFoundError
from mcap.reader import make_reader
from mcap_ros2.reader import read_ros2_messages
from rosidl_runtime_py.utilities import get_message


class ROSAnalysisResult:

    def __init__(self, topics):
        self.topics = topics

def _get_bag_mcap_file(bag_file_dir) -> tuple:
    try:
        with open(f'{bag_file_dir}/metadata.yaml', 'r') as file:
            metadata = yaml.safe_load(file)
        return metadata['rosbag2_bagfile_information']['relative_file_paths'][0]

    except FileNotFoundError:
        print("Error: config.yaml not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")

def get_topics(bag_file_dir):
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
                msg = get_message(type_str).get_fields_and_field_types()
                result[name] = msg
            except Exception as e:
                print(f"Could not load {type_str}: {e}")
        return result
    except FileNotFoundError:
        print("Error: config.yaml not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")



def export(bag_file_dir, topics_list, export_dir):
    return ROSAnalysisResult(ros_topics)