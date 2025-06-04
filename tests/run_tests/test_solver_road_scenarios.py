import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from sdf.core.gen_data import DataGenerator
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple

from sdf.core.sdf_solver import Solver
from tests.env_sets.road_test_scenarios import *
from tests.env_sets.gen_road_scenario import actions_light, scenario_5gen

from tests.run_tests.test_base import TestBase

def test_scenario20():
    testbase = TestBase()

    loops = 10
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    scene_tuple = scenario_20(predicates, actions)

    bfs_list = Solver.bfs_sdscene
    dfs_list = Solver.dfs_sdscene
    dfs_list_rdf = Solver.dfs_rdf
    bfs_list_rdf = Solver.bfs_rdf
    astar_sdscene = Solver.astar_sdscene
    astar_rdf = Solver.astar_rdf

    #solver_list = [bfs_list_rdf, dfs_list_rdf, astar_rdf]
    solver_list = [bfs_list, bfs_list_rdf, dfs_list_rdf, dfs_list, astar_sdscene, astar_rdf]

    for solver in solver_list:
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

    bfs_list = Solver.bfs_sdscene
    dfs_list = Solver.dfs_sdscene

    solver_list = [dfs_list, bfs_list]

    for solver in solver_list:
        testbase.test_solver(scene_tuple, solver, loops)


if __name__ == "__main__":

    test_scenario20()
    #TODO
    #test_scenario5gen()
