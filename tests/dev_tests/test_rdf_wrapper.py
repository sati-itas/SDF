import os
import sys
import timeit

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from sdf.core.rdf_wrapper import RDFWrapper
from sdf.data.otype import OType 

# from tests.env_sets.hanoi_sceanario import *
# from tests.env_sets.hanoi_predicates_actions import hanoi_predicates, actions_simple
from tests.env_sets.road_test_scenarios import *
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple

from tests.env_sets.gen_road_scenario import actions_light, scenario_5gen
from sdf.core.gen_data import DataGenerator

def test_gen_rdf_graph():

    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_30(predicates, actions)
    print(CurrentScene)

    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.gen_rdf_graph()
    print(graph)
    rdf_wrapper.serialize_rdf_graph('output_test_gen_rdf_graph')

    print(f'\ngraph_processing_time: {rdf_wrapper.gen_rdf_graph_processing_time*1000}ms')

def test_gen_rdf_graph_from_gen_data():

    generator = DataGenerator('test_scene.ttl')
    predicate_dict = generator.gen_predicates('gen_pred_list2.txt')
    for key,value in predicate_dict.items():
        print(f'{key}: {value}')

    generator.rdf_wrapper.get_base_uri(generator._graph_datagen)
    base_uri = generator.rdf_wrapper.base_uri

    actions = actions_light(predicate_dict, base_uri)

    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)

    print(CurrentScene)

    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.gen_rdf_graph(debug=False)
    print(graph)
    for act in action_list:
        print(act.name)
        act.precondition
        pre = graph.query(act.precondition)
        for row in pre:
            print(row)
    
    rdf_wrapper.serialize_rdf_graph('out_test_gen_rdf_graph_from_gen_data')

    print(f'\ngraph_processing_time: {rdf_wrapper.gen_rdf_graph_processing_time*1000}ms')


def test_gen_from_data_graph():
    rdf_wrapper = RDFWrapper(base_uri='http://example.org/Env')
    print(rdf_wrapper.base_uri)

    # parse graph with rdflib
    graph = rdf_wrapper.load_rdf_graph('test_scene.ttl', 'ttl')
    rdf_wrapper.get_base_uri(graph)
    print(rdf_wrapper.base_uri)

    # generate enum for types
    class_type = 'DomainTypes'
    subclasses = rdf_wrapper.get_subclasses(graph, f'{rdf_wrapper.base_uri}#{class_type}') #http://example.org/Scene#LaneType
    print(subclasses)

    # generate predicates_str  from data
    predicates = rdf_wrapper.get_predicates(graph)
    for pred in predicates:
        print("object-property:", pred)

if __name__ == "__main__":

    test_gen_rdf_graph()
    test_gen_rdf_graph_from_gen_data()
    test_gen_from_data_graph()
