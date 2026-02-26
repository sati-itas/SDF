import os
import sys
import timeit
import pytest
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from sdf.core.rdf_wrapper import RDFWrapper
from sdf.core.sdf_core import Predicate 
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple, actions_light, predicates_simple, actions_simple
from tests.env_sets.road_test_scenarios import scenario_20, scenario_30, scenario_5gen
from sdf.core.rdf_wrapper import RDFUtils

SDOBJECT_TEMPLATE = [
    "id",
    "object_type",
    "name",
    "x",
    "y",
    #"width",
    #"speed",
    #"acceleration",
    #"lane_assignment",
    # ...
]

def test_sdf_init_rdf_wrapper_C2():

    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_30(predicates, actions)

    test_data_dir = Path(__file__).resolve().parents[1] / "tests_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    # Case 2 with knowledge graph
    knowledge_graph_file_1 = 'sdf/data/situation_tbox_rdfs_v1.1.ttl'
    rdf_wrapper = RDFWrapper(CurrentScene)
    loaded_graph_1 = rdf_wrapper.load_knowledge_graph(knowledge_graph_file_1)
    attributes, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    rdf_wrapper.generate_data_graph(object_attributes=attributes)
    # assert rdf_wrapper.data_graph is not None
    # assert len(rdf_wrapper.data_graph) > 0
    # serialize directly to a test_data_dir file (avoid wrapper path assumptions)
    out_file = test_data_dir / "output_test_sdf_init_rdf_wrapper_case2.ttl"
    rdf_wrapper.data_graph.serialize(destination=str(out_file), format="turtle")

def test_sdf_init_rdf_wrapper_C3():

    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_30(predicates, actions)

    test_data_dir = Path(__file__).resolve().parents[1] / "tests_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    # Case 3 with template and predicates
    rdf_wrapper = RDFWrapper(CurrentScene)
    rdf_wrapper.generate_graph(object_template=SDOBJECT_TEMPLATE, predicates=predicates)
    # assert rdf_wrapper.data_graph is not None
    # assert len(rdf_wrapper.data_graph) > 0
    # serialize directly to a test_data_dir file (avoid wrapper path assumptions)
    out_file = test_data_dir / "output_test_sdf_init_rdf_wrapper_case3.ttl"
    rdf_wrapper.abox.serialize(destination=str(out_file), format="turtle")


def test_rdf_sdscene_generation_and_query_processing_KN():
    rdf_wrapper = RDFWrapper()

    # parse KN graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/situation_tbox_rdfs_v1.1.ttl')

    attr, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    predicate_dict = Predicate.gen_predicates(predicates)
    
    actions = actions_light(predicate_dict)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)

    rdf_wrapper.load_scene(CurrentScene)
    graph = rdf_wrapper.generate_data_graph(attr)
    # print(graph.serialize(format='turtle'))

    # SPARQL proof
    query1 = """
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o .
    }
    """
    query2 = """SELECT ?lane ?predecessor WHERE {
        ?lane <http://example.org/Situ#hasPredecessor> ?predecessor .
        }
    """

    query3 = """SELECT ?lane WHERE {
        <http://example.org/data#ego> <http://example.org/Situ#isOnLane> ?lane .
        }
    """
    results = graph.query(query1)
    for row in results:
        print(row)

    # action proof
    for act in action_list:
        act.init_action_with_rdf(rdf_wrapper)
        print(act.name)
        act.precondition
        pre = graph.query(act.precondition)
        for row in pre:
            print(row)

        # TEST check_precondition
        print(f'{act.name}.check_precondition_improve() => {act.check_precondition_on_rdf(rdf_wrapper.data_graph)}\n')

        # TEST execute_select_dict_list_improve
        print(f'{act.name}.execute_select_dict_list_improve() => {act.execute_action_on_rdf(rdf_wrapper.data_graph)}\n')

def test_sdf_actions_rdfscene():


    # predicates = hanoi_predicates()
    # actions = actions_simple(predicates)
    # CurrentScene, GoalScene, action_list = hanoi_classic(predicates, actions)


    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)

    # Test the RDFWrapper Scene Initialization
    #initialize the RDFWrapper with the current scene
    rdf_wrapper = RDFWrapper(CurrentScene)
    start_time = timeit.default_timer()
    print(f'Generating RDF graph for CurrentScene: {CurrentScene.name}')
    graph = rdf_wrapper.generate_graph()
    generation_time = timeit.default_timer() - start_time
    print(f'RDF graph generation time: {generation_time:.6f} seconds')

    rdf_wrapper= CurrentScene.init_rdf_wrapper()
    print(f'graphs are equal: {RDFUtils.is_equal(graph, rdf_wrapper.data_graph)}')
    CurrentScene_graph = rdf_wrapper.data_graph

    # SPARQL proof
    for act in action_list:
        act.init_action_with_rdf(rdf_wrapper)

        # Test action query
        # Measure timing for raw query
        start_time = timeit.default_timer()
        pre = graph.query(act.precondition)
        raw_query_time = timeit.default_timer() - start_time
        print(f"Raw query time: {raw_query_time:.6f} seconds")
        for row in pre:
            print(row)
        # Measure timing for prepared query
        start_time = timeit.default_timer()
        pre = graph.query(act.prep_query)
        prepared_query_time = timeit.default_timer() - start_time
        print(f"Prepared query time: {prepared_query_time:.6f} seconds")
        for row in pre:
            print(row)

        # TEST check_precondition
        print(f'{act.name}.check_precondition_improve() => {act.check_precondition_on_rdf(CurrentScene_graph)}\n')

        # TEST execute_select_dict_list_improve
        print(f'{act.name}.execute_select_dict_list_improve() => {act.execute_action_on_rdf(CurrentScene_graph)}\n')
        # Expected results for scenario_20:
        # LANE_CHANGE_RIGHT.check_precondition(): False
        # LANE_CHANGE_LEFT.check_precondition(): True
        # LANE_KEEPING.check_precondition(): True

if __name__ == "__main__":
    # with loading knowledge graph (check namespace self.KN default)
    test_sdf_init_rdf_wrapper_C2()
    test_rdf_sdscene_generation_and_query_processing_KN()
    
    ## without loading knowledge graph (check namespace self.KN default)
    test_sdf_init_rdf_wrapper_C3()
    test_sdf_actions_rdfscene()
    
