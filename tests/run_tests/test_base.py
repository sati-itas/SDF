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
from core.sdf_solver import Solver


class TestBase:

    def __init__(self):
        pass

    def test_solver(scene: tuple, solver: Solver, loops: int):
        CurrentScene, GoalScene, action_list = scene
        loop_count = 0
        planning_processing_time = []

        print(f'\n ------ SOLVER: {solver.__name__} ------')

        while loop_count < loops:

            start_planning_time = timeit.default_timer()
            plan = solver(CurrentScene, GoalScene, action_list)
            end_planning_time = timeit.default_timer()

            print(f'\n planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')

            loop_count += 1
            planning_processing_time.append(end_planning_time - start_planning_time)

        print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

        if not plan[1]:
            print(f'solver: no solution found')
            pass
        else:
            print(f'\n --solution--')
            # print(plan)
            for item in plan[0]:
                if isinstance(item, Action):
                    print(f'{item.name}')
                else:
                    print(f'{item}')
