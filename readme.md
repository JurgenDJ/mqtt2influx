
# MQTT to Influx feeder

## Installation

Make sure Python 3.6 or above is installed on the system.
installation is done by cloning the git repository, creating a virtual environment and installing the required package

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

Create a mapping.yaml and servercong.yaml file in the directory (rename/copy the included .example files)

### testing the configuration

The mapping configuration can be tested using the test_logger script.
It will read the tests.yaml file and process each test, and report on (un)succesfull matches.

``` sh
python test_logger.py
```

## Running the deamon

Activate the virtual environment and then start the deamon:

``` sh
source ./venv/bin/activate
nohup python mqtt2influx.py 2>/dev/null 1>/dev/null &
```

## Still TODO

- make it possible to split up the configuration in more seperate files instead of one big one
- setup GIT repository, including ignore file
- add an optional condition expression, to decide if logging is necessary for a received message
- create .sh file for starting the deamon, add bat file for starting the deamon
- add paramter for the location (and level) of the logfile

### done

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
