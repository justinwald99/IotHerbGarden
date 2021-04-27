"""Module to configure all loggers for the project."""
import logging

import colorama
from colorama import Fore

# Init color engine
colorama.init()

logging.basicConfig(
    level="INFO", format=f"{Fore.CYAN}%(asctime)s {Fore.RESET}%(name)s {Fore.YELLOW}%(levelname)s {Fore.RESET}%(message)s")

# Logging setup
sample_logger = logging.getLogger(Fore.GREEN + "sample_log")
mqtt_logger = logging.getLogger(Fore.MAGENTA + "mqtt_log")
config_logger = logging.getLogger(Fore.BLUE + "config_log")
pump_logger = logging.getLogger(Fore.BLUE + "pump_log")
