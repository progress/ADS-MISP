import argparse
import base64
import json


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--options", action='store')
    parser.add_argument("--data", action="store")
    arguments = vars(parser.parse_args())
    return arguments


def decode_arguments(arguments):
    options = json.loads(arguments["options"])
    data = base64.b64decode(arguments["data"]).decode('utf-8')
    data_lines = data.split('<delimiter>')
    ads_event = {"id": data_lines[0], "detect_date": data_lines[1].split(" ")[0], "detect_time": data_lines[1].split(" ")[1],
              "first_flow_date": data_lines[2].split(" ")[0], "first_flow_time": data_lines[2].split(" ")[1],
              "event_type": data_lines[3], "event_type_long": data_lines[4], "perspective": data_lines[5],
              "severity": data_lines[6], "description": data_lines[7], "ports": data_lines[8],
              "protocols": data_lines[9], "source": data_lines[10], "target": data_lines[12]}
    return options, ads_event
    
    
def load_input_data():
    arguments = parse_arguments()
    options, ads_event = decode_arguments(arguments)
    return options, ads_event
