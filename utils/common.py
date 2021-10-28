"""Common methods for reuse."""
import json


def connection_message(broker_ip, rc):
    """Let the client know that a connection has been made."""
    return f"Connected to {broker_ip} with return code {rc}"


def parse_json_payload(msg):
    """Parse raw MQTT payload into a Python primitives."""
    return json.loads(msg.payload.decode())
