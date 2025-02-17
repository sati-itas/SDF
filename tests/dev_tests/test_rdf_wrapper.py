import os
import sys
import timeit

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)


from core.sdf_core import OType
from core.rdf_wrapper import RDFWrapper

# from tests.env_sets.hanoi_sceanario import *
# from tests.env_sets.hanoi_predicates_actions import hanoi_predicates, actions_simple
from tests.env_sets.road_test_scenarios import *
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple


def test_gen_rdf_graph():

    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_30(predicates, actions)


    print(CurrentScene)
    rdf_wrapper = RDFWrapper(OType, CurrentScene)
    graph = rdf_wrapper.gen_rdf_graph()
    print(graph)
    rdf_wrapper.serialize_rdf_graph()



    print(f'\ngraph_processing_time: {rdf_wrapper.gen_rdf_graph_processing_time*1000}ms')


if __name__ == "__main__":

    test_gen_rdf_graph()
