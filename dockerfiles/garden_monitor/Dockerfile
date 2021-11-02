FROM python:3

WORKDIR /usr/src/iot_herb_garden

# Install Python packages
COPY requirements/garden_monitor/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Configure broker address
ENV MQTT_BROKER_HOST=192.168.1.232

# Copy source
COPY . .

CMD [ "python", "./garden_monitor.py"]