import os
import sys
import timeit

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from core.sdf_def_predicates_actions import actions_simple, predicates_simple
from core.sdf_core import OType, RDFWrapper

from tests.env_sets.road_test_scenarios import *


def test_gen_rdf_graph():

    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_5(predicates, actions)

    start_generate_graph = timeit.default_timer()
    print(CurrentScene)
    Wrapper = RDFWrapper(OType, CurrentScene)
    graph = Wrapper.gen_rdf_graph()

    end_generate_graph = timeit.default_timer()
    graph_processing_time = end_generate_graph - start_generate_graph

    print(f'\ngraph_processing_time: {graph_processing_time*1000}ms')


if __name__ == "__main__":

    test_gen_rdf_graph()
