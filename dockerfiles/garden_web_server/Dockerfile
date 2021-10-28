FROM python:3

WORKDIR /usr/src/iot_herb_garden


# Install Python packages
COPY requirements/garden_web_server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

CMD [ "python", "./garden_web_server.py" ]