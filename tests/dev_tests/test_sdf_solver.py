import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from core.sdf_core import SDObject, Scene, OType
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple
from tests.env_sets.hanoi_predicates_actions import hanoi_predicates
from tests.env_sets.hanoi_predicates_actions import actions_simple as hanoi_move

from core.sdf_solver import check_subset_scenes, check_identical_scenes
from tests.env_sets.road_test_scenarios import *
from tests.env_sets.hanoi_sceanario import scenario_test


def test_goal_checker_road():
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

    goal_checker(InitScene, GoalScene)

    ##############################################

    CurrentScene, Goal_scene, action_list = scenario_10(predicates, actions)
    CurrentScene1, GoalScene1, action_list1 = scenario_10(predicates, actions)
    goal_checker(CurrentScene, CurrentScene1)

    ###############################################

    visited = {CurrentScene: True}
    visited[CurrentScene1] = True
    visited[InitScene] = True
    visited[GoalScene] = False
    print(visited)
    print(CurrentScene in visited)


def test_goal_checker_hanoi():

    # Instanziierung Prädikate
    predicates = hanoi_predicates()
    actions = hanoi_move(predicates)

    CurrentScene, Goal_scene, action_list = scenario_test(predicates, actions)
    CurrentScene1, GoalScene1, action_list1 = scenario_test(predicates, actions)

    goal_checker(CurrentScene, GoalScene1)


def goal_checker(scene, goal):

    print(f'----- SCENE SCENE----- \t\n {scene}')
    print(f'----- GOAL SCENE-----  \t\n {goal}')

    print(f'-----RESULT goal_checker()-----  \n')
    print(f'check_subset_scenes(): \t\n {check_subset_scenes(goal,scene)}')
    print(f'check_identical_scenes(): \t\n {check_identical_scenes(scene, goal)}')
    print(
        f'goal.scene_relations.items() <= scene.scene_relations.items(): \t\n {goal.scene_relations.items() <= scene.scene_relations.items()}'
    )
    print(
        f'scene.scene_relations.items() == goal.scene_relations.items(): \t\n  {scene.scene_relations.items() == goal.scene_relations.items()}'
    )
    print(
        f'all(item in scene.scene_relations.items() for item in goal.scene_relations.items()): \t\n {all(item in scene.scene_relations.items() for item in goal.scene_relations.items())}'
    )
    print(f'check_identical_scenes(): \t\n {check_identical_scenes(scene, goal)}')


if __name__ == "__main__":

    # test_goal_checker_road()
    test_goal_checker_hanoi()
