FROM python:3.9
WORKDIR /app/source
COPY ./source/requirements.txt /app/source/requirements.txt
RUN python -m pip install --upgrade pip && pip install --no-cache-dir --upgrade -r /app/source/requirements.txt
COPY ./source /app/source
COPY ./config /app/config
CMD ["python", "mqtt2influx.py"]