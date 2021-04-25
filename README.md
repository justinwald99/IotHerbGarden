# iot_herb_garden

## Installation / Environment Settings
In order prepare your environment to run the IoT Herb Garden System, first install python and the following python packages using the command "pip install {package name}" on both the computer and Rasperry Pi used for your system. The versions listed in the table are those that we ran the project with, but many packages will work with later versions.

| Package | Version |
|-------------------------| -------|
| Brotli                    | 1.0.9 |
| click                     | 7.1.2 |
| colorama                  | 0.4.4 |
| dash                      | 1.19.0 |
| dash-bootstrap-components | 0.12.0 |
| dash-core-components      | 1.15.0 |
| dash-html-components      | 1.1.2 |
| dash-renderer             | 1.9.0 |
| dash-table                | 4.11.2 |
| Flask                     | 1.1.2 |
| Flask-Compress            | 1.9.0 |
| future                    | 0.18.2 |
| greenlet                  | 1.0.0 |
| itsdangerous              | 1.1.0 |
| Jinja2                    | 2.11.3 |
| MarkupSafe                | 1.1.1 |
| numpy                     | 1.20.2 |
| paho-mqtt                 | 1.5.1 |
| pandas                    | 1.2.3 |
| pip                       | 20.2.3 |
| plotly                    | 4.14.3 |
| python-dateutil           | 2.8.1 |
| pytz                      | 2021.1 |
| retrying                  | 1.3.3 |
| setuptools                | 49.2.1 |
| six                       | 1.15.0 |
| SQLAlchemy                | 1.4.9 |
| Werkzeug                  | 1.0.1 |

You will also need a working MQTT broker, and a wireless network to run the local system on. We used `mosquitto`, accessible from https://mosquitto.org/ . Mosquitto configuration file needs to contain the settings:
```
listener 1883
allow_anonymous true
```

Next, assemble the hardware following the schematic in `docs/iot_herb_garden_schematic_bb.png` using the parts list in `docs/report.pdf` or other compatable parts.

## Running IoT_Herb_Garden / How to Run the Code

Three programs must be run to operate the IoT_Herb_Garden system: `garden_manager.py`, `garden_monitor.py`, and `garden_web_server.py`, as well as the MQTT broker.

When running the system, `garden_monitor.py` must be run on the Raspberry Pi. We recommended that `garden_manager.py` and `garden_web_server.py` be run on a separate computer to increase performance, but they can be run from the Pi if you chose (note that both manager and web server must be run on the same machine due to requiring direct database access).

To start the system, first start the MQTT server. If using mosquittor, run the following command from the mosquitto directory:
```
mosquitto -c "{address of the config file}"
```

Next start `garden_manager.py` using the command:
```
python garden_manager.py {ip of MQTT broker}
```

Next start `garden_web_server.py` using the command:
```
python garden_web_server.py {ip of MQTT broker}
```

Next start `garden_monitor.py` using the command:
```
python garden_monitor.py {ip of MQTT broker}
```

At this point all portions of the system should be online. The web server can be accessed through most browsers using `localhost:{port}` where port can be found in the command line output of `garden_web_server.py`. Each program can be stopped individually without impacting the rest of the system, other than the MQTT broker, which when closed would require a full system restart.

## Operations / How to Interpret the Results

To view the status of the system and manage sensor and plant settings, use the web server as described in the previous section. Through Overview and History, you can view the past sensor data and pump operations of the system. Controls can be used to manually operate the water pumps. Configurations can be used to change system settings on plant and sensor names, sensor sample rates, plant watering durations and soil humidity targets, and assign sensors and pumps to plants.

## Sample Input Files

Provided in the source code is a databse with data from our setup and testing. This data can be used through the web server to view how your data would look and test setting database values. Without any historical data, the system will generate a blank databse with default entries for plants and sensors. 

## Extra Information

This system was designed for a specific setup of four plants, but with minor alterations, many portions of the system could be extrapolated for larger or smaller setups. In order to understand the control flow and operations, we recommend reading the report found in `docs/`. 
