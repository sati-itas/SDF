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
from sdf_core import SDLObject, Scene, Action, OType
from sdf_def_predicates_actions import actions_simple, predicates_simple

from sdf_solver import Solver, check_subset_scenes, check_identical_scenes
from tests.road_test_scenarios import *


def test_goal_checker():
    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)

    scn_1 = {Agent: [1, 2]}

    object_list = [Agent, lane1]

    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    predicate_list = list(predicates.values())
    (
        is_on,
        is_on_lane,
        has_right_neighbour,
        has_left_neighbour,
        has_successor,
        has_predecessor,
        has_top_right_neighbour,
        has_top_left_neighbour,
        has_bottom_right_neighbour,
        has_bottom_left_neighbour,
    ) = predicate_list

    # Erzeugung Relationen Init-Szene
    rel_is_on_lane = {is_on_lane: [Agent, lane1]}
    rel_has_predecessor = {has_predecessor: [[lane1, lane2], [lane1, lane3]]}

    goal_rel_is_on = {is_on_lane: [Agent, lane1]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {**rel_is_on_lane, **rel_has_predecessor}
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    scene_list = [scn_1, scn_1]
    if scn_1 in scene_list:
        print(scn_1)
    else:
        print('not')
    # print(scn_1.items() == scn_2.items())
    print(check_subset_scenes(GoalScene, InitScene))
    print(all(item in InitScene.scene_relations.items() for item in GoalScene.scene_relations.items()))

    ##############################################

    CurrentScene, Goal_scene, action_list = scenario_10(predicates, actions)
    CurrentScene1, GoalScene1, action_list1 = scenario_10(predicates, actions)
    print(CurrentScene.scene_relations)
    print('----------------')
    print(CurrentScene1.scene_relations)

    print(check_subset_scenes(CurrentScene, CurrentScene1))
    print(CurrentScene.scene_relations.items() <= CurrentScene1.scene_relations.items())
    print(CurrentScene.scene_relations.items() == CurrentScene1.scene_relations.items())
    print(all(item in CurrentScene.scene_relations.items() for item in CurrentScene1.scene_relations.items()))
    print(check_identical_scenes(CurrentScene, CurrentScene1))

    ###############################################

    visited = {CurrentScene: True}
    visited[CurrentScene1] = True
    visited[InitScene] = True
    visited[GoalScene] = False
    print(visited)
    print(CurrentScene in visited)


def test_DFS():
    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = Ramp_On(predicates, actions)
    print(CurrentScene)
    loop_count = 0
    planning_processing_time = []
    while loop_count < 50:
        start_planning_time = timeit.default_timer()
        plan = Solver.simple_DFS(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    for item in plan[0]:
        if isinstance(item, Action):
            print(item.name)


def test_BFS():
    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = Ramp_On(predicates, actions)
    print(CurrentScene)
    loop_count = 0
    planning_processing_time = []
    while loop_count < 50:
        start_planning_time = timeit.default_timer()
        plan = Solver.simple_BFS(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    for item in plan[0]:
        if isinstance(item, Action):
            print(item.name)


def test_BFS_DP():
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)
    print(CurrentScene)
    loop_count = 0
    planning_processing_time = []
    while loop_count < 1:
        start_planning_time = timeit.default_timer()
        plan = Solver.BFS_DP(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time - start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    if len(plan[0]) > 1:
        plan = plan[0][1:]
        for item in plan:
            print(item.name)
    else:
        for item in plan:
            print(item.name)


if __name__ == "__main__":

    # test_goal_checker()
    # test_BFS() #Solution: LK,LL,LK
    test_BFS_DP()
    # test_DFS()
