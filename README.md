## Situation Description Framework -- SDF

Situation Description Framework (SDF), a framework to describe situations and plan task in context of mobile robotics. This approach includes a class structure to describe dynamic environments (scenes) and actions. It also includes simple planner like BFS and DFS. The knowledge based environment description is modeled via semantic representations and with the abbility of dynamic numeric measurement data. Action templates are inspired by PDDL and preconditions can be queried with SPARQL.

### Basic Usage

#### project installation

The following description gives you a view on how to setup a basic test run. 

Creating a virtual environment is recommented, for instance:

```
python -m venv .virtenv
```

After the activation of environment, install the requiered packages:

```
pip install -r requirements.txt
```

#### start a test run
To start a simple test of a simple street scenario:
```
python tests/run_tests/test_solver_road_scenarios.py
```
### In the development phase
This repository is under development and no documentation currently exists. For any questions, remarks or issues feel free to create an [issue](https://github.com/sati-itas/SDF/issues) or open a [discussion](https://github.com/sati-itas/SDF/discussions).
