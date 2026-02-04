import os
import sys
import time
from owlrl import RDFSClosure, DeductiveClosure, RDFS_Semantics


from sdf.core.rdf_wrapper import RDFUtils, RDFWrapper, RDFSRewriter
from sdf.core.sdf_core import Predicate

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from sdf.core.gen_data import DataGenerator
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple, make_road_heuristic_sd, make_road_heuristic_rdf

from sdf.core.sdf_solver import Solver
from tests.env_sets.road_test_scenarios import *
from tests.env_sets.gen_road_scenario import actions_light, actions_rewrite, scenario_5gen

from tests.run_tests.test_base import TestBase
from rdflib import Graph

# set logger level to error to avoid too much output during tests
import logging
logging.getLogger('sdf.core.sdf_solver').setLevel(logging.ERROR)
logging.getLogger('sdf.core.rdf_wrapper').setLevel(logging.ERROR)
logging.getLogger('sdf.core.sdf_core').setLevel(logging.ERROR)

def test_dataset_closure_materialization():
    rdf_wrapper = RDFWrapper()

    # parse KN graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')

    attr, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    predicate_dict = Predicate.gen_predicates(predicates)
    
    actions = actions_light(predicate_dict)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)

    rdf_wrapper.load_scene(CurrentScene)
    graph = rdf_wrapper.generate_data_graph(attr)

    ds = rdf_wrapper.dataset
    tbox = rdf_wrapper.tbox
    abox = rdf_wrapper.abox
    union = abox + tbox
    
    #print((tbox).serialize(format='turtle'))
    query3 = """SELECT ?lane WHERE {
        <http://example.org/data#lane1> <http://example.org/Scene#hasLateralNeighbour> ?lane .
        }
    """
    results = union.query(query3)
    for row in results:
        print(row)
    start_time = time.time()
    # materialize RDFS closure on abox
    DeductiveClosure(RDFS_Semantics, improved_datatypes=False, rdfs_closure=True, datatype_axioms=False, axiomatic_triples=False).expand(union)
    print("After RDFS Closure:\n")
    #print(union.serialize(format='turtle'))
    closure_time = time.time() - start_time
    print(f"RDFS Closure materialization took {closure_time} seconds\n")
    start_time = time.time()
    results = union.query(query3)
    for row in results:
        print(row)
    query_time = time.time() - start_time
    print(f"Query after RDFS Closure took {query_time} seconds\n")
    print(f"Total time for materialization and querying: {closure_time + query_time} seconds\n")

def test_closure_materialization_action():
    rdf_wrapper = RDFWrapper()

    # parse KN graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')

    attr, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    predicate_dict = Predicate.gen_predicates(predicates)
    
    actions = actions_rewrite(predicate_dict)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)

    rdf_wrapper.load_scene(CurrentScene)
    graph = rdf_wrapper.generate_data_graph(attr)

    ds = rdf_wrapper.dataset
    tbox = rdf_wrapper.tbox
    abox = rdf_wrapper.abox
    union = abox + tbox
    
    #print((abox+tbox).serialize(format='turtle'))
    query3 = """SELECT ?lane WHERE {
        <http://example.org/data#lane1> <http://example.org/Scene#hasLateralNeighbour> ?lane .
        }
    """
    results = union.query(query3)
    for row in results:
        print(row)
    start_time = time.time()
    # materialize RDFS closure on abox
    DeductiveClosure(RDFS_Semantics, improved_datatypes=False, rdfs_closure=True, datatype_axioms=False, axiomatic_triples=False).expand(union)
    print("After RDFS Closure:\n")
    #print(union.serialize(format='turtle'))
    closure_time = time.time() - start_time
    print(f"RDFS Closure materialization took {closure_time} seconds\n")
    start_time = time.time()
    results = union.query(query3)
    for row in results:
        print(row)
    query_time = time.time() - start_time
    print(f"Query after RDFS Closure took {query_time} seconds\n")
    print(f"Total time for materialization and querying: {closure_time + query_time} seconds\n")

    # action proof
    for act in action_list:
        act.init_action_with_rdf(rdf_wrapper)
        print(act.name)
        act.precondition
        pre = union.query(act.precondition)
        for row in pre:
            print(row)

        # TEST check_precondition
        print(f'{act.name}.check_precondition_improve() => {act.check_precondition_on_rdf(union)}\n')

        # TEST execute_select_dict_list_improve
        print(f'{act.name}.execute_select_dict_list_improve() => {act.execute_action_on_rdf(union)}\n')

def test_dataset_closure_rewriting():
    rdf_wrapper = RDFWrapper()

    # parse KN graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')

    attr, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    predicate_dict = Predicate.gen_predicates(predicates)
    
    actions = actions_rewrite(predicate_dict)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)

    rdf_wrapper.load_scene(CurrentScene)
    graph = rdf_wrapper.generate_data_graph(attr)

    ds = rdf_wrapper.dataset
    tbox = rdf_wrapper.tbox
    abox = rdf_wrapper.abox
    merge = abox + tbox
    
    print("Before RDFS Closure:")
    #print((abox+tbox).serialize(format='turtle'))

    query3 = """SELECT ?lane WHERE {
        <http://example.org/data#lane1> <http://example.org/Scene#hasLateralNeighbour> ?lane .
        }
    """
    results = merge.query(query3)
    for row in results:
        print(row)
    start_time = time.time()
    # rewrite queries according to RDFS rules
    rewriter = RDFSRewriter(tbox)
    rewritten_queries = rewriter.rewrite(query3)
    print("Rewritten query:\n", rewritten_queries, "\n")
    rewritten_time = time.time() - start_time
    print(f"RDFS Closure rewriting took {rewritten_time} seconds\n")

    start_time = time.time()
    print("Query Answer:\n")
    results = merge.query(rewritten_queries)
    for row in results:
        print(row)
    re_query_time = time.time() - start_time
    print(f"Query after RDFS rewriting took {re_query_time} seconds\n")
    print(f"Total time for rewriting and querying: {rewritten_time + re_query_time} seconds\n")


def test_closure_rewriting_action():
    rdf_wrapper = RDFWrapper()

    # parse KN graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')

    attr, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    predicate_dict = Predicate.gen_predicates(predicates)
    
    actions = actions_rewrite(predicate_dict)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)

    rdf_wrapper.load_scene(CurrentScene)
    graph = rdf_wrapper.generate_data_graph(attr)

    ds = rdf_wrapper.dataset
    tbox = rdf_wrapper.tbox
    abox = rdf_wrapper.abox
    merge = abox + tbox
    
    print("Before RDFS Closure:")
    #print((abox+tbox).serialize(format='turtle'))

    query3 = """SELECT ?lane WHERE {
        <http://example.org/data#lane1> <http://example.org/Scene#hasLateralNeighbour> ?lane .
        }
    """
    results = merge.query(query3)
    for row in results:
        print(row)
    start_time = time.time()
    # rewrite queries according to RDFS rules
    rewriter = RDFSRewriter(tbox)
    rewritten_queries = rewriter.rewrite(query3)
    print("Rewritten query:\n", rewritten_queries, "\n")
    rewritten_time = time.time() - start_time
    print(f"RDFS Closure rewriting took {rewritten_time} seconds\n")

    start_time = time.time()
    print("Query Answer:\n")
    results = merge.query(rewritten_queries)
    for row in results:
        print(row)
    re_query_time = time.time() - start_time
    print(f"Query after RDFS rewriting took {re_query_time} seconds\n")
    print(f"Total time for rewriting and querying: {rewritten_time + re_query_time} seconds\n")

        # action proof
    for act in action_list:
        act.init_action_with_rdf(rdf_wrapper, rewrite=True)
        print(act.name)
        act.precondition
        pre = merge.query(act.precondition)
        for row in pre:
            print(row)

        # TEST check_precondition
        print(f'{act.name}.check_precondition_improve() => {act.check_precondition_on_rdf(merge)}\n')

        # TEST execute_select_dict_list_improve
        print(f'{act.name}.execute_select_dict_list_improve() => {act.execute_action_on_rdf(merge)}\n')
    
if __name__ == "__main__":
    test_dataset_closure_materialization()
    test_dataset_closure_rewriting()
    test_closure_materialization_action()
    test_closure_rewriting_action()

