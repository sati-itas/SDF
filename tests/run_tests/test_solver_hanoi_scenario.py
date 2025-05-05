import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from tests.env_sets.hanoi_predicates_actions import actions_simple, hanoi_predicates

from sdf.core.sdf_solver import Solver
from tests.env_sets.hanoi_sceanario import hanoi_classic
from tests.run_tests.test_base import TestBase




def test_hanoi():
    testbase = TestBase()

    loops = 1

    predicates = hanoi_predicates()
    actions = actions_simple(predicates)

    scene_tuple = hanoi_classic(predicates, actions)


    bfs_sdscene = Solver.bfs_sdscene
    bfs_rdf = Solver.bfs_rdf

    solver_list = [bfs_sdscene, bfs_rdf]
    

    for solver in solver_list:
        testbase.test_solver(scene_tuple, solver, loops)



if __name__ == "__main__":

    test_hanoi()
