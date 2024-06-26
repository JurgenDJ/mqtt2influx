
# MQTT to Influx feeder

## MOVE TO DOCKER CONTAINER

motivation: easier to install, including the automatic starting after server reboot

- split source code to seperate subdirectory
- split config to seperate subdirectory
- build dockerfile

### building the image

``` sh
docker build -t mqtt2influx .
```
or use the script **rebuild_image.sh**

### checking the image

``` sh
docker run -it --rm mqtt2influx /bin/bash
```

### running the image

use the **run_mqtt2influx.sh** script

### checking the live output from the deamon

``` sh
docker attach --sig-proxy=false mqtt2influx
```

using the sig-proxy flag, you can exit from attached mode with **ctrl-c** without killing the entire process

or go in the docker container to check the logs:
``` sh
docker exec -it mqtt2influx sh

cd /app/log
more mqtt2influx.log

exit
```


## Installation

Make sure Python 3.6 or above is installed on the system.
installation is done by cloning the git repository, creating a virtual environment and installing the required packages

### On Linux

``` sh
git clone http:// <to be completed>
cd mqtt2influx
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### On Windows

``` cmd
git clone http:// <to be completed>
cd mqtt2influx
python3 -m venv venv
./venv/scripts/activate
pip install -r requirements.txt
```

## Configuration

Create a mapping.yaml and serverconfig.yaml file in the directory
(rename/copy the included .example files)

### testing the configuration

The mapping configuration can be tested using the test_logger script.
It will read the tests.yaml file and process each test, and report on (un)succesfull matches.

``` sh
python test_logger.py
```

The mapping.yaml configuration file can be updated while the deamon is running. look at the the mqtt2influx.log file to see if an updated mapping.yaml was successfully loaded

```sh
tail -f mqtt2influx.log
```

## Running the deamon

Activate the virtual environment and then start the deamon:

``` sh
cd <yourfolder>
source ./venv/bin/activate
nohup python mqtt2influx.py 2>/dev/null 1>/dev/null &
```

Checking the logs, for any **warnings**, typically from errors in the configuration,or **errors**, a problem in the application:

```sh
egrep 'WARNING|ERROR' mqtt2influx.log
```

## Still TODO

- make it possible to split up the configuration in more seperate files instead of one big one
- add an optional condition expression, to decide if logging is necessary for a received message
- create .sh file for starting the deamon, add bat file for starting the deamon
- add paramter for the location (and level) of the logfile

### done

- setup GIT repository, including ignore file
- make example file for the serverconfig
- create a requirements file
- let mqtt2influx use the servierconfig credentials
- add decent logging (info vs error logging, auto cleaunup of logs, ...)
- use colors in feedback of test_logger

## Development guidelines

### updating the requirements.txt file

```cmd
pip3 freeze > requirements.txt
```
