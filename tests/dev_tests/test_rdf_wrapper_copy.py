import os
import sys
import timeit

from sdf.core.sdf_core import Predicate

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from sdf.core.rdf_wrapper import RDFWrapper
from sdf.data.otype import OType

from tests.env_sets.road_test_scenarios import *
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple

from tests.env_sets.gen_road_scenario import actions_light, scenario_5gen

def ctest_gen_rdf_graph():

    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_30(predicates, actions)
    print(CurrentScene)

    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.generate_graph()
    print(graph)
    rdf_wrapper.serialize_rdf_graph('output_test_gen_rdf_graph')

    print(f'\ngraph_processing_time: {rdf_wrapper.gen_rdf_graph_processing_time*1000}ms')

def ctest_extract_rdf_components():
    rdf_wrapper = RDFWrapper(base_uri='http://example.org/Env')


    # parse knowledge graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/situation_tbox_rdfs_v1.1.ttl')

    # generate enum for types
    class_type = 'DomainTypes'
    subclasses = rdf_wrapper.get_subclasses(graph, f'{rdf_wrapper.base_uri}#{class_type}') #http://example.org/Scene#LaneType
    if subclasses:
        for subclass in subclasses:
            print("subclass of", class_type, ":", subclass)
    else:
        print("no subclasses found for", class_type)

    # generate properties_str  from data
    properties = rdf_wrapper.get_properties(graph)
    if properties:
        for prop in properties:
            print("property:", prop)
    else:
        print("no properties found")

    # generate predicates_str  from data
    predicates = rdf_wrapper.get_predicates(graph)
    if predicates:
        for pred in predicates:
            print("object-property:", pred)
    else:
        print("no predicates found")

    # generate attributes_str  from data
    attributes = rdf_wrapper.get_attributes(graph)
    if attributes:
        for attr in attributes:
            print("data-property:", attr)
    else:
        print("no attributes found")

def ctest_graph_preparation():
    test_file = os.path.abspath(__file__)
    tests_dir = os.path.dirname(os.path.dirname(test_file))
    test_data_dir = os.path.join(tests_dir, "tests_data")
    os.makedirs(test_data_dir, exist_ok=True)

    rdf_wrapper = RDFWrapper()

    # parse knowledge graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/situation_tbox_rdfs_v1.1.ttl')
    attr, predicates = rdf_wrapper.get_attrs_and_pred_kg()

    out_file = os.path.join(test_data_dir, "output_test_ctest_graph_preparation.ttl")
    rdf_wrapper.knowledge_graph.serialize(destination=str(out_file), format="turtle")

    # example triple addition to data graph subject-predicate-object subject is vehicle type
    knowledge_ns = rdf_wrapper.nsr.KN
    data_ns = rdf_wrapper.nsr.DATA
    subj = rdf_wrapper.to_uri(f'{data_ns}car1')
    pred = rdf_wrapper.to_uri(f'{knowledge_ns}{'hasValueS'}')
    obj = rdf_wrapper.to_literal(123)
    rdf_wrapper.data_graph.add((subj, pred, obj))

    print(f'Data graph: {rdf_wrapper.data_graph.serialize(format="turtle")}\n')
    out_file = os.path.join(test_data_dir, "output_test_ctest_graph_preparation_data_graph.ttl")
    rdf_wrapper.data_graph.serialize(destination=str(out_file), format="turtle")

def ctest_sdgraph_generation():
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)
    print(repr(CurrentScene))

    rdf_wrapper_scene = RDFWrapper(CurrentScene)
    rdf_graph1 = rdf_wrapper_scene.generate_graph()

    sd_scene1 = rdf_wrapper_scene.gen_sd_scene_from_rdf_database(rdf_graph1)
    print(repr(sd_scene1))

def ctest_sdgraph_generation_KN():
    rdf_wrapper = RDFWrapper()


    # parse knowledge graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/situation_tbox_rdfs_v1.1.ttl')
    attr, predicates = rdf_wrapper.get_attrs_and_pred_kg()

    predicates = Predicate.gen_predicates(predicates) #! convert to SD Predicates Dict
    actions = actions_light(predicates)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicates, actions) 

    rdf_wrapper.load_scene(CurrentScene)
    rdf_graph1 = rdf_wrapper.generate_data_graph(object_attributes=attr)

    sd_scene1 = rdf_wrapper.gen_sd_scene_from_rdf_database(rdf_graph1)
    print(repr(sd_scene1))

if __name__ == "__main__":

    ctest_extract_rdf_components()
    ctest_graph_preparation()
    ctest_sdgraph_generation_KN()