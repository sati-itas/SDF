# Situation Description Framework - SDF
### Overview
The **Situation Description Framework (SDF)** is a semantic-based framework for situation-aware modeling, representation, and planning in dynamic environments. It combines classical planning approaches with semantic technologies, particularly RDF (Resource Description Framework) and OWL (Web Ontology Language), and follows the approaches for semantic graph-based planning with or without Background Knowledge.

A central component of the framework is a structured class architecture that describes a situation at a conceptual level. This structure enables domain-independent representation of relevant entities, their properties, and their relationships to one another.

The framework serves as a mapping layer between data and semantic instance graphs while maintaining the underlying background knowledge. This forms the basis for situation-based querying and reasoning using technologies such as:

* SPARQL for queries over the RDF data model
* Rules for deriving implicit information
* Basic RDFS rewriting

Based on the semantic instance graph, SDF applies classical graph search algorithms (DFS, BFS, UCS, and A*) to RDF data.Actions, their preconditions, and their effects are described semantically and determined at runtime through rule-based or query-based mechanisms.

---
### Installation

SDF can be installed as a Python Package: ```pip install .```

Creating a virtual environment is recommented, for instance:

```
python -m venv .venv
```
After the activation of environment, install the requiered packages:

```
pip install -r requirements.txt
```
---

### Examples
#### Solve the Hanoitower
To solve the hanoi tower with simple Graph-based planning, see:
```
python tests/run_tests/test_solver_hanoi_scenario.py
```

#### Solve Simple Driving Domain 
Without Background Knowledge, see the test ```test_scenario20()``` in:
```
python tests/run_tests/test_solver_road_scenarios.py
```

With Background Knowledge, see the test ```test_scenario_KN()``` in: 
```
python tests/run_tests/test_solver_road_scenarios.py
```

---
### In the development phase
This repository is under development and no documentation exists. For any questions, remarks or issues feel free to create an [issue](https://github.com/sati-itas/SDF/issues) or open a [discussion](https://github.com/sati-itas/SDF/discussions).
