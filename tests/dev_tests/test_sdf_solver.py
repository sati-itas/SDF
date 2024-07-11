import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from core.sdf_core import SDObject, Scene, OType
from core.sdf_def_predicates_actions import actions_simple, predicates_simple

from core.sdf_solver import check_subset_scenes, check_identical_scenes
from tests.env_sets.road_test_scenarios import *


def test_goal_checker():
    # Instanziierung Objekte
    Agent = SDObject("ego", OType.EGO)
    lane1 = SDObject("lane1", OType.LANE)
    lane2 = SDObject("lane2", OType.LANE)
    lane3 = SDObject("lane3", OType.LANE)

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


if __name__ == "__main__":

    test_goal_checker()
