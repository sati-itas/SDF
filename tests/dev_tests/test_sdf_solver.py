import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from core.gen_data import DataGenerator
from core.sdf_core import SDObject, Scene
from data.otype import OType

from core.sdf_solver import check_subset_scenes, check_identical_scenes, check_common_keys, check_subset_pair

from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple
from tests.env_sets.road_test_scenarios import scenario_10

from tests.env_sets.gen_road_scenario import actions_light, scenario_5gen
from data._gen.domain_otypes import DomainTypes
from data._gen.domain_scenery import Scenery
from data._gen.domain_dyn_object import DynamicObject
from data._gen.domain_location import Location
from data._gen.domain_self import SelfRepresentation

from tests.env_sets.hanoi_predicates_actions import hanoi_predicates
from tests.env_sets.hanoi_predicates_actions import actions_simple as hanoi_move
from tests.env_sets.hanoi_sceanario import hanoi_classic


def test_goal_checker_road():
    Agent = SDObject("ego", OType.EGO)
    car1 = SDObject("car1", OType.VEHICLE)
    lane1 = SDObject("lane1", OType.LANE)
    lane2 = SDObject("lane2", OType.LANE)
    lane3 = SDObject("lane3", OType.LANE)

    scn_1 = {Agent: [1, 2]}

    object_list = [Agent, lane1]


    predicates = predicates_simple()
    actions = actions_simple(predicates)

    # rel_is_on_lane = {predicates['is_on_lane']: [[Agent, lane1], [car1, lane2]]}
    rel_is_on_lane = {predicates['is_on_lane']: [[Agent, lane1]]}
    rel_has_predecessor = {predicates['has_predecessor']: [[lane1, lane2], [lane1, lane3]]}

    goal_rel_is_on = {predicates['is_on_lane']: [[Agent, lane1]]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {**rel_is_on_lane, **rel_has_predecessor}
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    goal_checker(InitScene, GoalScene)

    ##############################################

    CurrentScene, Goal_scene, action_list = scenario_10(predicates, actions)
    CurrentScene1, GoalScene1, action_list1 = scenario_10(predicates, actions)
    goal_checker(CurrentScene, GoalScene1)

    ###############################################

    # visited = {CurrentScene: True}
    # visited[CurrentScene1] = True
    # visited[InitScene] = True
    # visited[GoalScene] = False
    # print(visited)
    # print(CurrentScene in visited)


def test_goal_checker_hanoi():

    predicates = hanoi_predicates()
    actions = hanoi_move(predicates)

    CurrentScene, Goal_scene, action_list = hanoi_classic(predicates, actions)
    CurrentScene1, GoalScene1, action_list1 = hanoi_classic(predicates, actions)

    goal_checker(CurrentScene, GoalScene1)

def test_goal_gen_road():
    generator = DataGenerator('test_scene.ttl')
    predicate_dict = generator.gen_predicates()
    generator.rdf_wrapper.get_base_uri(generator._graph_datagen)
    base_uri = generator.rdf_wrapper.base_uri

    #############
    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    lane6 = SDObject("lane6", Scenery.LANESEGMENT)

    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5, lane6]

    goal_rel_is_on = {predicate_dict['has_lane_assignment']: [[Agent, lane1]]}
    goal_rel_has_successor = {predicate_dict['has_successor']: [[lane1, lane3]]}
    goal_scene = {**goal_rel_is_on,**goal_rel_has_successor}


    GoalScene = Scene(object_list, goal_scene)

    ############

    actions = actions_light(predicate_dict, base_uri)


    CurrentScene, Goal_scene, action_list = scenario_5gen(predicate_dict, actions)
    CurrentScene1, GoalScene1, action_list1 = scenario_5gen(predicate_dict, actions)

    #goal_checker(CurrentScene, CurrentScene1)
    goal_checker(CurrentScene, GoalScene)


def goal_checker(scene, goal):

    print(f'----- SCENE SCENE----- \t\n {repr(scene)}')
    print(f'----- GOAL SCENE-----  \t\n {repr(goal)}')

    print(f'-----RESULT goal_checker()-----  \n')
    print(f'check_subset_scenes(): \t\n {check_subset_scenes(goal,scene)}')
    print(f'proof check_subset_scenes \t\n {goal.scene_relations.items() <= scene.scene_relations.items()}')
    print(f'\ntest_subset: {check_subset_pair(goal,scene)}')
    print(f'check_identical_scenes(): \t\n {check_identical_scenes(scene, goal)}')
    print(f'proof check_identical_scenes: \t\n  {scene.scene_relations.items() == goal.scene_relations.items()}')
    print(f'\n')
    print(f'check_common_keys: {check_common_keys(scene,goal)}')
    print(f'test_intersect: {test_intersect(goal,scene)}\n')


def test_intersect(scene1,scene2):
    common_keys = scene1.scene_relations.keys() & scene2.scene_relations.keys()
    test_intersect = []
    if common_keys:
        # check for overlaps
        for key in common_keys:
            # generate list of tuples
            set1 = {tuple(sublist) for sublist in scene1.scene_relations[key]}
            #print(set1)
            set2 = {tuple(sublist) for sublist in scene2.scene_relations[key]}
            #print(set2)
            # set intersect
            overlap = set1 & set2
            print(overlap)
            if overlap:
                #print(f"overlap: key '{key}' contains the elements {overlap} in both scene_relations.")
                test_intersect.append(True)
            else:
                #print(f"no overlap under key '{key}' found.")
                test_intersect.append(False)
        return all(test_intersect)
    else:
        return False


if __name__ == "__main__":

    # test_goal_checker_road()
    # test_goal_checker_hanoi()
    test_goal_gen_road()
