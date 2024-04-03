import os
import sys
import timeit
import numpy as np
import matplotlib.pyplot as plt
from typing import List,Dict
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir,'..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from sdf_def_predicates_actions import actions_simple, predicates_simple
from sdf_solver import Solver, check_subset_scenes, check_identical_scenes
from sdf_core import SDL_Object, Predicate, Scene, Action, OType, RDF_Wrapper
from analyse.data_storage import DataStorage
from tests.road_test_scenarios import *


def helper_timeit_decorator(solver):
    # define the inner
    def time_solver(current_scene, goal_scene, action_list, data_logger):
        start_planning_time = timeit.default_timer()
        plan = solver(current_scene, goal_scene, action_list, data_logger)
        if plan:
            end_planning_time = timeit.default_timer()
            planning_step_processing_time = end_planning_time - start_planning_time
            return [plan, planning_step_processing_time]
        else:
            return [None,None]
    return time_solver
    

def test_scenes_vis_execute_statistic(testloop):

    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    current_scene_6, goal_scene_6, action_list_6= scenario_5(predicates, actions)
    current_scene_10, goal_scene_10, action_list_10= scenario_10(predicates, actions)
    current_scene_16, goal_scene_16, action_list_16= scenario_15(predicates, actions)
    current_scene_20, goal_scene_20, action_list_20= scenario_20(predicates, actions)

    data_bfs_6 = DataStorage(test_loop = testloop, solver='BFS_DP')
    data_bfs_6.domain = 'scenario_5'
    data_bfs_10 = DataStorage(test_loop = testloop, solver='BFS_DP')
    data_bfs_10.domain = 'scenario_10'
    data_bfs_16 = DataStorage(test_loop = testloop, solver='BFS_DP')
    data_bfs_16.domain = 'scenario_15'
    data_bfs_20 = DataStorage(test_loop = testloop, solver='BFS_DP')
    data_bfs_20.domain = 'scenario_20'

    loop_count = 0
    while loop_count < testloop:

        simple_BFS = helper_timeit_decorator(Solver.simple_BFS)

        plan_bfs_6, bfs_planning_step_processing_time_6 = simple_BFS(current_scene_6, goal_scene_6, action_list_6, data_logger = data_bfs_6)
        plan_bfs_10, bfs_planning_step_processing_time_10 = simple_BFS(current_scene_10, goal_scene_10, action_list_10, data_logger = data_bfs_10)
        plan_bfs_16, bfs_planning_step_processing_time_16 = simple_BFS(current_scene_16, goal_scene_16, action_list_16, data_logger = data_bfs_16)
        plan_bfs_20, bfs_planning_step_processing_time_20 = simple_BFS(current_scene_20, goal_scene_20, action_list_20, data_logger = data_bfs_20)

        #data_simple_dfs.planning_processing_time.append(dfs_planning_step_processing_time)
        data_bfs_6.planning_processing_time.append(bfs_planning_step_processing_time_6)
        data_bfs_10.planning_processing_time.append(bfs_planning_step_processing_time_10)
        data_bfs_16.planning_processing_time.append(bfs_planning_step_processing_time_16)
        data_bfs_20.planning_processing_time.append(bfs_planning_step_processing_time_20)

        loop_count += 1

        #data_simple_dfs.test_loop = loop_count
        data_bfs_6.test_loop = loop_count
        data_bfs_10.test_loop = loop_count
        data_bfs_16.test_loop = loop_count
        data_bfs_20.test_loop = loop_count

    # consol output
    #print(f'[mean_dfs_planning_processing_time :]: {np.mean(np.array(data_simple_dfs.planning_processing_time))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_6]: {np.mean(np.array(data_bfs_6.planning_processing_time))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_10]: {np.mean(np.array(data_bfs_10.planning_processing_time))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_16]: {np.mean(np.array(data_bfs_16.planning_processing_time))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_20]: {np.mean(np.array(data_bfs_20.planning_processing_time))*1000} [msec]')
    
    plot_execute_statistic([data_bfs_6, data_bfs_10, data_bfs_16, data_bfs_20])

def test_scenes_vis_solver_statistic(testloop):

    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    current_scene_6, goal_scene_6, action_list_6= scenario_5(predicates, actions)
    current_scene_10, goal_scene_10, action_list_10= scenario_10(predicates, actions)
    current_scene_16, goal_scene_16, action_list_16= scenario_15(predicates, actions)
    current_scene_20, goal_scene_20, action_list_20= scenario_20(predicates, actions)

    bfs = [[],[],[],[]]
    dfs = [[],[],[],[]]
    bfs_dp = [[],[],[],[]]

    loop_count = 0
    while loop_count < testloop:

        simple_dfs = helper_timeit_decorator(Solver.simple_DFS)
        simple_BFS = helper_timeit_decorator(Solver.simple_BFS)
        BFS_dp = helper_timeit_decorator(Solver.BFS_DP)

        plan_bfs_6, bfs_planning_step_processing_time_6 = simple_BFS(current_scene_6, goal_scene_6, action_list_6, data_logger=DataStorage('simple_bfs'))
        plan_bfs_10, bfs_planning_step_processing_time_10 = simple_BFS(current_scene_10, goal_scene_10, action_list_10, data_logger=DataStorage('simple_bfs'))
        plan_bfs_16, bfs_planning_step_processing_time_16 = simple_BFS(current_scene_16, goal_scene_16, action_list_16, data_logger=DataStorage('simple_bfs'))
        plan_bfs_20, bfs_planning_step_processing_time_20 = simple_BFS(current_scene_20, goal_scene_20, action_list_20, data_logger=DataStorage('simple_bfs'))
        bfs[0].append(bfs_planning_step_processing_time_6)
        bfs[1].append(bfs_planning_step_processing_time_10)
        bfs[2].append(bfs_planning_step_processing_time_16)
        bfs[3].append(bfs_planning_step_processing_time_20)

        plan_dfs_6, dfs_planning_step_processing_time_6 = simple_dfs(current_scene_6, goal_scene_6, action_list_6, data_logger=DataStorage('simple_dfs'))
        plan_dfs_10, dfs_planning_step_processing_time_10 = simple_dfs(current_scene_10, goal_scene_10, action_list_10, data_logger=DataStorage('simple_dfs'))
        plan_dfs_16, dfs_planning_step_processing_time_16 = simple_dfs(current_scene_16, goal_scene_16, action_list_16, data_logger=DataStorage('simple_dfs'))
        plan_dfs_20, dfs_planning_step_processing_time_20 = simple_dfs(current_scene_20, goal_scene_20, action_list_20, data_logger=DataStorage('simple_dfs'))
        dfs[0].append(dfs_planning_step_processing_time_6)
        dfs[1].append(dfs_planning_step_processing_time_10)
        dfs[2].append(dfs_planning_step_processing_time_16)
        dfs[3].append(dfs_planning_step_processing_time_20)

        plan_bfs_dp_6, bfs_dp_planning_step_processing_time_6 = BFS_dp(current_scene_6, goal_scene_6, action_list_6, data_logger=DataStorage('bfs_dp'))
        plan_bfs_dp_10, bfs_dp_planning_step_processing_time_10 = BFS_dp(current_scene_10, goal_scene_10, action_list_10, data_logger=DataStorage('bfs_dp'))
        plan_bfs_dp_16, bfs_dp_planning_step_processing_time_16 = BFS_dp(current_scene_16, goal_scene_16, action_list_16, data_logger=DataStorage('bfs_dp'))
        plan_bfs_dp_20, bfs_dp_planning_step_processing_time_20 = BFS_dp(current_scene_20, goal_scene_20, action_list_20, data_logger=DataStorage('bfs_dp'))
        bfs_dp[0].append(bfs_dp_planning_step_processing_time_6)
        bfs_dp[1].append(bfs_dp_planning_step_processing_time_10)
        bfs_dp[2].append(bfs_dp_planning_step_processing_time_16)
        bfs_dp[3].append(bfs_dp_planning_step_processing_time_20)

        loop_count += 1

    # consol output
    #print(f'[mean_dfs_planning_processing_time :]: {np.mean(np.array(data_simple_dfs.planning_processing_time))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_6]: {np.mean(np.array(bfs[0]))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_10]: {np.mean(np.array(bfs[1]))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_16]: {np.mean(np.array(bfs[2]))*1000} [msec]')
    print(f'[mean_bfs_planning_step_processing_time_20]: {np.mean(np.array(bfs[3]))*1000} [msec]')

    print('plan_dfs:')
    for item in plan_dfs_20[0]:
        if isinstance(item,Action):
            print(item.name)
    
    result = {'bfs':bfs,'dfs':dfs,'bfs_dp':bfs_dp}
    plot_solver_statistic(result)

def test_scenes(testloop):

    # Instanziierung Prädikate
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    current_scene, goal_scene, action_list= scenario_5(predicates, actions)
    #current_scene, goal_scene, action_list= scenario_10(predicates, actions)
    #current_scene, goal_scene, action_list= scenario_15(predicates, actions)
    #current_scene, goal_scene, action_list= scenario_20(predicates, actions)

    #data_simple_dfs = DataStorage(test_loop = testloop, solver='simple_dfs')
    data_simple_bfs = DataStorage(test_loop = testloop, solver='simple_BFS')
    data_bfs_dp = DataStorage(test_loop = testloop, solver='BFS_DP')

    loop_count = 0
    while loop_count < testloop:

        #simple_dfs = helper_timeit_decorator(Solver.simple_DFS)
        simple_BFS = helper_timeit_decorator(Solver.simple_BFS)
        bfs_dp = helper_timeit_decorator(Solver.BFS_DP)

        # data_simple_dfs = DataStorage(test_loop = testloop, solver='simple_dfs')
        # data_simple_bfs = DataStorage(test_loop = testloop, solver='simple_BFS')
        # data_bfs_dp = DataStorage(test_loop = testloop, solver='BFS_DP')

        #plan_dfs, dfs_planning_step_processing_time = simple_dfs(current_scene, goal_scene, action_list, data_logger = data_simple_dfs)
        plan_bfs, bfs_planning_step_processing_time = simple_BFS(current_scene, goal_scene, action_list, data_logger = data_simple_bfs)
        plan_bfs_dp, bfs_dp_planning_step_processing_time = bfs_dp(current_scene, goal_scene, action_list, data_logger = data_bfs_dp)

        #data_simple_dfs.planning_processing_time.append(dfs_planning_step_processing_time)
        data_simple_bfs.planning_processing_time.append(bfs_planning_step_processing_time)
        data_bfs_dp.planning_processing_time.append(bfs_dp_planning_step_processing_time)

        loop_count += 1

        #data_simple_dfs.test_loop = loop_count
        data_simple_bfs.test_loop = loop_count
        data_bfs_dp.test_loop = loop_count

    # consol output
    #print(f'[mean_dfs_planning_processing_time :]: {np.mean(np.array(data_simple_dfs.planning_processing_time))*1000} [msec]')
    print(f'[mean_bfs_planning_processing_time :]: {np.mean(np.array(data_simple_bfs.planning_processing_time))*1000} [msec]')
    print(f'[mean_bfs_dp_planning_processing_time :]: {np.mean(np.array(data_bfs_dp.planning_processing_time))*1000} [msec]')

    # print(f'plan_dfs:')
    # for item in plan_dfs[0]:
    #     if isinstance(item,Action):
    #         print(item.name)

    print(f'plan_bfs:')
    for item in plan_bfs[0]:
        if isinstance(item,Action):
            print(item.name)

    if len(plan_bfs_dp[0])>1:
        plan = plan_bfs_dp[0][1:]
        print('plan_bfs_dp:')
        for item in plan:
            print(item[0].name)
    else:
        print('plan_bfs_dp:\n')
        for item in plan_bfs_dp:
            print(item.name)
    
    #plot_execute_statistic(data_simple_bfs)
    plot_solver_statistic([data_simple_bfs,data_bfs_dp])

def plot_execute_statistic(datastorage:List[DataStorage]):

    plot_data = []
    plot_dict = {}
    for data in datastorage:
        plot_data.append(data.convert2dict_rdfprocessing())
    
    #merge dicts
    for k in plot_data[0]:
        plot_dict[k] = [d[k] for d in plot_data]

    #mean values and flatten
    for key, item in plot_dict.items():
        plot_dict[key] = np.mean(np.array(item),axis=1)*1000
        #plot_dict[key] = [x for xs in item for x in xs]

    print(f'plot_dict: {plot_dict}')

    scene = ("scenario_6\n Objekte=8",'scenario_10\n Objekte=12','scenario_16\n Objekte=18', 'scenario_20\n Objekte=22')
    x = np.arange(len(plot_dict['mean_graph_processing_time']))  # the label locations
    width = 0.25
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained',figsize=(10, 5), dpi=400)

    for attribute, measurement in plot_dict.items():
        print(measurement)
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3,fmt='{:.2f}')
        multiplier += 1

    ax.set_ylabel('Dauer (ms)')
    ax.set_title("Performanz Aktions-Vorlagen (execute-methode)")
    ax.set_xticks(x + width, scene)
    ax.legend(loc='upper right') #, ncols=3

    plt.savefig("Performanz_Aktionsvorlagen-.pdf") #https://tex.stackexchange.com/questions/508567/best-matplotlitb-to-tikz-conversion-tool
    plt.show()

def plot_solver_statistic(datastorage:Dict):

    print(datastorage)
    for solver, item in datastorage.items():
        datastorage[solver] = np.mean(np.array(item),axis=1)*1000

    scene = ("scenario_6",'scenario_10','scenario_16', 'scenario_20')

    x = np.arange(len(scene))  # the label locations
    width = 0.25
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained', figsize=(10, 5), dpi=400)
    for key, values in datastorage.items():
        offset = width*multiplier

        p=ax.bar(x + offset, values, width, label=key)
        ax.bar_label(p,fmt='{:.0f}', padding=3)
        multiplier += 1

    ax.set_ylabel('Dauer (ms)')
    ax.set_title("Performanz Suchverfahren")
    ax.set_xticks(x + width, scene)
    ax.legend(loc='upper left') #, ncols=3

    plt.savefig("Performanz_Solver-.pdf") #https://tex.stackexchange.com/questions/508567/best-matplotlitb-to-tikz-conversion-tool
    plt.show()


if __name__ == "__main__":
    #test_scenes(1) #Solution: LK,LL,LK
    #test_scenes_vis_solver_statistic(1)
    test_scenes_vis_execute_statistic(1)
