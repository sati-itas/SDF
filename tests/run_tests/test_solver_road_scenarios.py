import os
import sys

from sdf.core.rdf_wrapper import RDFUtils, RDFWrapper
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

# set logger level to error to avoid too much output during tests
import logging
logging.getLogger('sdf.core.sdf_solver').setLevel(logging.ERROR)
logging.getLogger('sdf.core.rdf_wrapper').setLevel(logging.ERROR)
logging.getLogger('sdf.core.sdf_core').setLevel(logging.ERROR)

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

def test_scenario20():
    testbase = TestBase()

    loops = 1
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    heuristic_sd = make_road_heuristic_sd(predicates)
    heuristic_rdf = make_road_heuristic_rdf()

    scene_tuple = scenario_20(predicates, actions)

    solver = Solver([SDOBJECT_TEMPLATE], predicates=predicates)
    bfs_sd = solver.bfs_sdscene
    dfs_sd = solver.dfs_sdscene
    dfs_rdf = solver.dfs_rdf
    bfs_rdf = solver.bfs_rdf
    astar_sd = solver.astar_sdscene
    astar_rdf = solver.astar_rdf

    solver_list = [bfs_rdf, dfs_rdf, astar_rdf]
    #solver_list = [bfs_rdf, dfs_rdf]# 
    #
    solver_list = [bfs_sd, bfs_rdf, dfs_rdf, dfs_sd, astar_sd, astar_rdf]# bfs_sd, bfs_rdf, dfs_rdf, dfs_sd, 

    for solver in solver_list:
        if solver == astar_rdf:
            print(f'\n testing solver: {solver.__name__} with heuristic rdf')
            testbase.test_solver(scene_tuple, solver, loops, heuristic_rdf)
        elif solver == astar_sd:
            print(f'\n testing solver: {solver.__name__} with heuristic sd')
            testbase.test_solver(scene_tuple, solver, loops, heuristic_sd)
        testbase.test_solver(scene_tuple, solver, loops)

def test_scenario_KN():
    testbase = TestBase()

    loops = 1

    query1 = """
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o .
    }
    """
    #TODO heuristics



    ## wrapper for current scene from KN graph
    wrapper = RDFWrapper()
    graph = wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')
    attr, predicates = wrapper.get_attrs_and_pred_kg()
    print(wrapper.base_uri)
    predicate_dict = Predicate.gen_predicates(predicates)
    

    actions = actions_rewrite(predicate_dict)
    scene_tuple = scenario_5gen(predicate_dict, actions)
    wrapper.load_scene(scene_tuple[0])
    current_rdf_graph = wrapper.generate_data_graph(object_attributes=attr)
    # pre = current_rdf_graph.query(query1)
    # for row in pre:
    #     print(row)

    goal_wrapper = RDFWrapper()
    goal_wrapper.get_attrs_and_pred_kg() #TODO set base uri properly
    goal_wrapper.load_scene(scene_tuple[1])
    goal_rdf_graph = goal_wrapper.generate_data_graph(object_attributes=attr)
    print(RDFUtils.is_equal(current_rdf_graph, goal_rdf_graph))
    # pre = goal_rdf_graph.query(query1)
    # for row in pre:
    #     print(row)



    scene_tuple = (current_rdf_graph, goal_rdf_graph, actions)

    solver = Solver(current_scene_rdf_wrapper=wrapper, fo_rewrite=True)



    bfs_sd = solver.bfs_sdscene
    dfs_sd = solver.dfs_sdscene
    dfs_rdf = solver.dfs_rdf
    bfs_rdf = solver.bfs_rdf
    astar_sd = solver.astar_sdscene
    astar_rdf = solver.astar_rdf

    solver_list = [bfs_rdf, dfs_rdf, astar_rdf] 
    #solver_list = [dfs_rdf] 
    #solver_list = [bfs_sd, bfs_rdf, dfs_rdf, dfs_sd, astar_sd, astar_rdf]# bfs_sd, bfs_rdf, dfs_rdf, dfs_sd, 

    for solver in solver_list:
        # if solver == astar_rdf:
        #     print(f'\n testing solver: {solver.__name__} with heuristic rdf')
        #     testbase.test_solver(scene_tuple, solver, loops, heuristic_rdf)
        # elif solver == astar_sd:
        #     print(f'\n testing solver: {solver.__name__} with heuristic sd')
        #     testbase.test_solver(scene_tuple, solver, loops, heuristic_sd)
        testbase.test_solver(scene_tuple, solver, loops)

def test_scenario5gen():
    testbase = TestBase()
    generator = DataGenerator('test_scene1.ttl')
    predicate_dict = generator.gen_predicates()
    generator.rdf_wrapper.get_base_uri(generator._graph_datagen)
    base_uri = generator.rdf_wrapper.base_uri

    
    loops = 10

    actions = actions_light(predicate_dict)

    scene_tuple = scenario_5gen(predicate_dict, actions)

    bfs_sd = Solver.bfs_sdscene
    dfs_sd = Solver.dfs_sdscene

    solver_list = [dfs_sd, bfs_sd]

    for solver in solver_list:
        testbase.test_solver(scene_tuple, solver, loops)


if __name__ == "__main__":

    #test_scenario20()
    test_scenario_KN()
    #test_scenario5gen()
