FROM python:3

WORKDIR /usr/src/iot_herb_garden

# Install Python packages
COPY requirements/garden_manager/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

CMD [ "python", "./garden_manager.py"]