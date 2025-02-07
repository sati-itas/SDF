import os
import sys
import timeit
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from core.sdf_core import Action
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple

from core.sdf_solver import Solver
from tests.env_sets.road_test_scenarios import *

from tests.run_tests.test_base import TestBase

def test_scenario20():
    testbase = TestBase

    loops = 1
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    scene_tuple = scenario_20(predicates, actions)

    bfs_list = Solver.bfs_list
    dfs_list = Solver.dfs_list

    solver_list = [dfs_list,bfs_list]

    for solver in solver_list:
        testbase.test_solver(scene_tuple, solver, loops)

def test_scenario30():
    testbase = TestBase

    loops = 10
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    scene_tuple = scenario_30(predicates, actions)

    simple_bfs = Solver.simple_bfs
    simple_dfs = Solver.simple_dfs
    bfs_list = Solver.bfs_list
    dfs_list = Solver.dfs_list

    solver_list = [simple_bfs,simple_dfs,bfs_list, dfs_list]

    for solver in solver_list:
        testbase.test_solver(scene_tuple, solver, loops)


if __name__ == "__main__":

    test_scenario20()
    # test_scenario30()
