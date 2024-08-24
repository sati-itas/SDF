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


def test_DFS(loops: int):
    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)
    # print(CurrentScene)

    loop_count = 0
    planning_processing_time = []
    while loop_count < loops:
        start_planning_time = timeit.default_timer()
        plan = Solver.simple_dfs(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print('\n---------solver dfs-----------')
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    if isinstance(plan, bool):
        pass
    else:
        print(f'\ndfs solution:')
        for item in plan[0]:
            if isinstance(item, Action):
                print(f'{item.name}')


def test_BFS(loops: int):
    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)
    # print(CurrentScene)

    loop_count = 0
    planning_processing_time = []
    while loop_count < loops:
        start_planning_time = timeit.default_timer()
        plan = Solver.simple_bfs(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print('\n---------solver bfs-----------')
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    if isinstance(plan, bool):
        pass
    else:
        print(f'\nbfs solution:')
        for item in plan[0]:
            if isinstance(item, Action):
                print(f'{item.name}')


def test_BFS_DP(loops: int):
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)
    # print(CurrentScene)

    loop_count = 0
    planning_processing_time = []
    while loop_count < loops:
        start_planning_time = timeit.default_timer()
        plan = Solver.bfs_dp(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print('\n---------solver bfs_dp-----------')
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    if not plan[1]:
        print(f'bfs_dp: no solution found')
        pass
    else:
        print(f'\nbfs_dp solution:')
        print(plan)
        for item in plan[0]:
            if isinstance(item, Action):
                print(f'{item.name}')


def test_BFS_DP_list(loops: int):
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)
    # print(CurrentScene)

    loop_count = 0
    planning_processing_time = []
    while loop_count < loops:
        start_planning_time = timeit.default_timer()
        plan = Solver.bfs_dp_list(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print('\n---------solver bfs_dp_list-----------')
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    if not plan[1]:
        print(f'bfs_dp_list: no solution found')
        pass
    else:
        print(f'\nbfs_dp_list solution:')
        for item in plan[0]:
            if isinstance(item, Action):
                print(f'{item.name}')
            else:
                print(f'{item}')


def test_DFS_list(loops: int):
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)
    # print(CurrentScene)

    loop_count = 0
    planning_processing_time = []
    while loop_count < loops:
        start_planning_time = timeit.default_timer()
        plan = Solver.dfs_list(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print('\n---------solver dfs_list-----------')
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    if not plan[1]:
        print(f'no solution found')
        pass
    else:
        print(f'\ndfs_list solution:')
        for item in plan[0]:
            if isinstance(item, Action):
                print(f'{item.name}')
            else:
                print(f'{item}')


if __name__ == "__main__":
    loops = 1
    test_DFS(loops)
    # test_BFS(loops)
    test_BFS_DP(loops)
    test_BFS_DP_list(loops)
    test_DFS_list(loops)
