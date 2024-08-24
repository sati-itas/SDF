# SDF

Situation Description Framework (SDF) a Framework to describe situations in context of cognitive robotics and automated driving. This includes a class structure to describe dynamic environment (scenes) and actions. Automated Planner like BFS ,DFS and A*. The knowledge based environment description is modeled via semantic representations and with the abbility of dynamic numeric measurement data. Action templates are inspired by PDDL and preconditions can be queried with SPARQL.

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
