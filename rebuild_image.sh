docker stop mqtt2influx
docker rm mqtt2influx
docker image rm mqtt2influx
docker build -t mqtt2influx .