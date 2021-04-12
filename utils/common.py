"""Common methods for reuse."""
import json
import sys
import re


def _usage_prompt(script_name):
    """Print a usage prompt for the user."""
    print(f"Usage: python {script_name.split('/')[-1]} [MQTT broker IP]")


def _arg_check(script_name):
    """Check whether the user has included the mqtt broker IP."""
    if (len(sys.argv) != 2):
        print("\nPlease include the MQTT broker IP as the only arg.\n")
        _usage_prompt(script_name)
        exit(1)

    if (not re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", sys.argv[1])):
        print("\nInvalid MQTT broker IP\n")
        _usage_prompt(script_name)
        exit(1)


def get_broker_ip(script_name):
    """Check that an MQTT broker was provided and return the IP."""
    _arg_check(script_name)
    return re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", sys.argv[1]).group()


def print_connection(broker_ip, rc):
    """Let the client know that a connection has been made."""
    print(f"Connected to {broker_ip} with return code {rc}")


def parse_json_payload(msg):
    """Parse raw MQTT payload into a Python primitives."""
    return json.loads(msg.payload.decode())
