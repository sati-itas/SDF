import os
import sys
import timeit

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple
from core.sdf_core import OType, RDFWrapper

from tests.env_sets.road_test_scenarios import *

# TODO test SPARQL Query -> check_precondition(scene, debug)

if __name__ == "__main__":
    pass
