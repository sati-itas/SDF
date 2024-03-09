# SDF

SituationDescriptionFramework: class structure to describe environments and actions in context of automated driving and robotics. Environment is modeled via knowledge based approach and semantic representations. actions/action templates are inspired by PDDL.

## Basic Usage

### project installation

The following description gives a you a view on how to setup a basic test run. 'symbolic_decision_making' should be root directory.
Creating a virtual environment is recommented, for instance:

```
python -m venv .virtenv
```

After the activation of your environment, install the requiered packages:

```
pip install -r requirements.txt
```

### MQTT Usage

For using MQTT instead of ZeroMQ, you need to install a (local) MQTT broker - Mosquitto is suggested. Befor starting the `main.py` file you need to start up the broker. The communication is currently set up for a local Mosquitto broker but can easily adapted to any other broker by eventually changing the host and port of the `connect()` methods of each client.
