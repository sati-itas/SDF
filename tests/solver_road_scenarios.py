import os
import sys
import timeit
import numpy as np
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir,'..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from sdf_def_predicates_actions import actions_simple, predicates_simple
from sdf_solver import Solver, check_subset_scenes, check_identical_scenes
from sdf_core import SDL_Object, Predicate, Scene, Action, OType, RDF_Wrapper


def Ramp_Off():

    # Instanziierung Objekte
    Agent=SDL_Object("ego", 1, 1)
    Car1=SDL_Object("car1", 2, 3)
    lane1=SDL_Object("lane1", 3, 2)
    lane2=SDL_Object("lane2", 4, 2)
    lane3=SDL_Object("lane3", 5, 2)
    lane4=SDL_Object("lane4", 6, 2)
    lane5=SDL_Object("lane5", 7, 2)
    object_list=[Agent, Car1, lane1, lane2, lane3, lane4, lane5]




    predicates = predicates_simple()
    actions = actions_simple(predicates)

    predicate_list = list(predicates.values())
    is_on, is_on_lane, has_right_neighbour, has_left_neighbour, has_successor, has_predecessor,\
    has_top_right_neighbour, has_top_left_neighbour,has_bottom_right_neighbour,\
    has_bottom_left_neighbour=predicate_list

    # Erzeugung Relationen Init-Szene
    rel_is_on_lane={is_on_lane:[Agent, lane1]}
    rel_is_on={is_on:[Car1, lane2]}
    rel_has_right_neighbour={has_right_neighbour:[[lane1, lane2], [lane3, lane4], [lane4, lane5]]}
    rel_has_left_neighbour={has_left_neighbour:[[lane2, lane1],[lane4, lane3], [lane5, lane4]]}
    rel_has_successor={has_successor:[[lane1, lane3],[lane2, lane4]]}
    rel_has_predecessor={has_predecessor:[[lane3, lane1],[lane4, lane2]]}


    goal_rel_is_on={is_on_lane:[Agent, lane5]}
    goal_scene={**goal_rel_is_on}

    init_scene={**rel_is_on, **rel_is_on_lane, **rel_has_right_neighbour, **rel_has_left_neighbour, **rel_has_successor, **rel_has_predecessor}
    InitScene=Scene(object_list, init_scene, predicate_list, 3)
    GoalScene=Scene(object_list, goal_scene, predicate_list, 4)


    CurrentScene=InitScene
    return CurrentScene, GoalScene, actions



def Ramp_On():     

    # Instanziierung Objekte
    Agent=SDL_Object("ego", 1, 1)
    Car1=SDL_Object("car1", 2, 3)
    lane1=SDL_Object("lane1", 3, 2)
    lane2=SDL_Object("lane2", 4, 2)
    lane3=SDL_Object("lane3", 5, 2)
    lane4=SDL_Object("lane4", 6, 2)
    lane5=SDL_Object("lane5", 7, 2)
    object_list=[Agent, Car1, lane1, lane2, lane3, lane4, lane5]

    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    predicate_list = list(predicates.values())
    is_on, is_on_lane, has_right_neighbour, has_left_neighbour, has_successor, has_predecessor,\
    has_top_right_neighbour, has_top_left_neighbour,has_bottom_right_neighbour,\
    has_bottom_left_neighbour=predicate_list

    # Erzeugung Relationen Init-Szene
    rel_is_on_lane={is_on_lane:[Agent, lane1]}
    rel_is_on={is_on:[Car1, lane3]}
    rel_has_right_neighbour={has_right_neighbour:[[lane4, lane2], [lane5, lane3]]}
    rel_has_left_neighbour={has_left_neighbour:[[lane2, lane4],[lane3, lane5]]}
    rel_has_successor={has_successor:[[lane1, lane2],[lane2, lane3],[lane4, lane5]]}
    rel_has_predecessor={has_predecessor:[[lane2, lane1],[lane3, lane2],[lane5, lane4]]}


    goal_rel_is_on={is_on_lane:[Agent, lane5]}
    goal_scene={**goal_rel_is_on}

    init_scene={**rel_is_on, **rel_is_on_lane, **rel_has_right_neighbour, **rel_has_left_neighbour, **rel_has_successor, **rel_has_predecessor}
    InitScene=Scene(object_list, init_scene, predicate_list, 3)
    GoalScene=Scene(object_list, goal_scene, predicate_list, 4)

    CurrentScene=InitScene
    return CurrentScene, GoalScene, actions

def test_goal_checker():
    CurrentScene, Goal_scene, action_list = Ramp_On()
    CurrentScene1, GoalScene1, action_list1 = Ramp_On()

    scn_1 = {'sdl_pre':[1,2]}
    scn_2 = {'sdl_pre':[1,2]}

    # Instanziierung Objekte
    Agent=SDL_Object("ego", 1, 1)
    lane1=SDL_Object("lane1", 3, 2)
    lane2=SDL_Object("lane2", 3, 2)
    lane3=SDL_Object("lane3", 3, 2)

    object_list=[Agent, lane1]

    # Instanziierung Prädikate
    predicates = predicates_simple()


    predicate_list = list(predicates.values())
    is_on, is_on_lane, has_right_neighbour, has_left_neighbour, has_successor, has_predecessor,\
    has_top_right_neighbour, has_top_left_neighbour,has_bottom_right_neighbour,\
    has_bottom_left_neighbour=predicate_list

    # Erzeugung Relationen Init-Szene
    rel_is_on_lane={is_on_lane:[Agent, lane1]}
    rel_has_predecessor={has_predecessor:[[lane1, lane2], [lane1, lane3]]}


    goal_rel_is_on={is_on_lane:[Agent, lane1]}
    goal_scene={**goal_rel_is_on}

    init_scene={**rel_is_on_lane, **rel_has_predecessor}
    InitScene=Scene(object_list, init_scene, predicate_list, 3)
    GoalScene=Scene(object_list, goal_scene, predicate_list, 4)

    scene_list = [scn_1,scn_1]
    if scn_1 in scene_list:
        print(scn_1)
    else:
        print('not')
    # print(scn_1.items() == scn_2.items())
    # print(check_subset_scenes(GoalScene,InitScene))
    print(all(item in InitScene.scene_relations.items() for item in GoalScene.scene_relations.items()))
    
    print(check_subset_scenes(CurrentScene,CurrentScene1))
    print(CurrentScene.scene_relations.items() <= CurrentScene1.scene_relations.items())
    print(CurrentScene.scene_relations.items() == CurrentScene1.scene_relations.items())
    print(all(item in CurrentScene.scene_relations.items() for item in CurrentScene1.scene_relations.items()))
    print(check_identical_scenes(CurrentScene,CurrentScene1))

def test_ramp_on_BFS():
    CurrentScene, GoalScene, action_list = Ramp_On()
    print(CurrentScene)
    loop_count = 0
    planning_processing_time = []
    while loop_count < 50:
        start_planning_time = timeit.default_timer()
        plan = Solver.simple_BFS(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time-start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    for item in plan[0]:
        if isinstance(item,Action):
            print(item.name)

def test_ramp_on_BFS_DP():
    CurrentScene, GoalScene, action_list = Ramp_On()
    print(CurrentScene)
    loop_count = 0
    planning_processing_time = []
    while loop_count < 50:
        start_planning_time = timeit.default_timer()
        plan = Solver.BFS_DP(CurrentScene, GoalScene, action_list)
        end_planning_time = timeit.default_timer()
        print(f'planning step processing_time : {(end_planning_time-start_planning_time)*1000} [msec]')
        loop_count += 1
        planning_processing_time.append(end_planning_time-start_planning_time)
    print(f'[mean_planning_processing_time :]: {np.mean(np.array(planning_processing_time))*1000} [msec]')

    for item in plan[0]:
        if isinstance(item,Action):
            print(item.name)


def test_ramp_off_BFS():

    CurrentScene, GoalScene, action_list = Ramp_Off()
    print(CurrentScene)

    plan = Solver.simple_BFS(CurrentScene, GoalScene, action_list)

    for item in plan[0]:
        if isinstance(item,Action):
            print(item.name)

if __name__ == "__main__":
    test_goal_checker()
    test_ramp_on_BFS() #Solution: LK,LL,LK
    #test_ramp_on_BFS_DP()
    #test_ramp_off_BFS() #Solution: LK,LR,LR