import os
import sys

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
from tests.env_sets.gen_road_scenario import actions_light, scenario_5gen

from tests.run_tests.test_base import TestBase

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

    solver = Solver(object_template=[SDOBJECT_TEMPLATE])
    bfs_sd = solver.bfs_sdscene
    dfs_sd = solver.dfs_sdscene
    dfs_rdf = solver.dfs_rdf
    bfs_rdf = solver.bfs_rdf
    astar_sd = solver.astar_sdscene
    astar_rdf = solver.astar_rdf

    solver_list = [bfs_rdf, dfs_rdf, astar_rdf] 
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

def test_scenario5gen():
    testbase = TestBase()
    generator = DataGenerator('test_scene.ttl')
    predicate_dict = generator.gen_predicates()
    generator.rdf_wrapper.get_base_uri(generator._graph_datagen)
    base_uri = generator.rdf_wrapper.base_uri

    
    loops = 10

    actions = actions_light(predicate_dict, base_uri)

    scene_tuple = scenario_5gen(predicate_dict, actions)

    bfs_sd = Solver.bfs_sdscene
    dfs_sd = Solver.dfs_sdscene

    solver_list = [dfs_sd, bfs_sd]

    for solver in solver_list:
        testbase.test_solver(scene_tuple, solver, loops)


if __name__ == "__main__":

    test_scenario20()
    #TODO
    #test_scenario5gen()
