!#/bin/bash

#  --restart always \

docker run -d \
  --name mqtt2influx \
  --restart always \
  -e TZ=Europe/Brussels \
  -v /apps/mqtt2influx/config:/app/config \
  -v /apps/mqtt2influx/log:/app/log \
  mqtt2influx
