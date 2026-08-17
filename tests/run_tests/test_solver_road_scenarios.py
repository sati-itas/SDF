import os
import sys

from sdf.core.rdf_wrapper import RDFUtils, RDFWrapper
from sdf.core.sdf_core import Action, Predicate, SDObject, Scene

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple, make_road_heuristic_rdf,actions_rewrite

from sdf.core.sdf_solver import Solver
from tests.env_sets.road_test_scenarios import scenario_20, scenario_5gen
#from tests.env_sets.gen_road_scenario import actions_light, actions_rewrite, scenario_5gen

from tests.run_tests.test_base import TestBase

# set logger level to error to avoid too much output during tests
import logging
logging.getLogger('sdf.core.sdf_solver').setLevel(logging.ERROR)
logging.getLogger('sdf.core.rdf_wrapper').setLevel(logging.ERROR)
logging.getLogger('sdf.core.sdf_core').setLevel(logging.ERROR)

SDOBJECT_TEMPLATE = [
    "id",
    "object_type",
    "name",
    "x",
    "y",
    #"width",
    #"speed",
    #"acceleration",
    #"lane_assignment",
    # ...
]

def test_scenario20():
    testbase = TestBase()

    loops = 1
    predicates = predicates_simple()
    actions = actions_simple(predicates)

    heuristic_rdf = make_road_heuristic_rdf()

    scene_tuple = scenario_20(predicates, actions)

    solver = Solver([SDOBJECT_TEMPLATE], predicates=predicates)
    dfs_rdf = solver.dfs_rdf
    bfs_rdf = solver.bfs_rdf
    astar_rdf = solver.astar_rdf

    solver_list = [bfs_rdf, dfs_rdf, astar_rdf]


    for solver in solver_list:
        if solver == astar_rdf:
            print(f'\n testing solver: {solver.__name__} with heuristic rdf')
            testbase.test_solver(scene_tuple, solver, loops, heuristic_rdf)
        testbase.test_solver(scene_tuple, solver, loops)

def test_scenario_KN():
    testbase = TestBase()

    loops = 1

    query1 = """
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o .
    }
    """
    #TODO heuristics

    ## wrapper for current scene from KN graph
    wrapper = RDFWrapper()
    graph = wrapper.load_knowledge_graph('sdf/data/situation_tbox_rdfs_v1.1.ttl')
    attr, predicates = wrapper.get_attrs_and_pred_kg()
    print(wrapper.base_uri)
    predicate_dict = Predicate.gen_predicates(predicates)
    

    actions = actions_rewrite(predicate_dict)
    scene_tuple = scenario_5gen(predicate_dict, actions)
    wrapper.load_scene(scene_tuple[0])
    current_rdf_graph = wrapper.generate_data_graph(object_attributes=attr)
    # pre = current_rdf_graph.query(query1)
    # for row in pre:
    #     print(row)

    goal_wrapper = RDFWrapper()
    goal_wrapper.get_attrs_and_pred_kg() #TODO set base uri properly
    goal_wrapper.load_scene(scene_tuple[1])
    goal_rdf_graph = goal_wrapper.generate_data_graph(object_attributes=attr)
    print(RDFUtils.is_equal(current_rdf_graph, goal_rdf_graph))
    # pre = goal_rdf_graph.query(query1)
    # for row in pre:
    #     print(row)


    situation_tuple = (current_rdf_graph, goal_rdf_graph, actions)

    solver = Solver(current_scene_rdf_wrapper=wrapper, fo_rewrite=True)

    dfs_rdf = solver.dfs_rdf
    bfs_rdf = solver.bfs_rdf
    astar_rdf = solver.astar_rdf

    solver_list = [bfs_rdf, dfs_rdf, astar_rdf] 


    for solver in solver_list:
        # if solver == astar_rdf:
        #     print(f'\n testing solver: {solver.__name__} with heuristic rdf')
        #     testbase.test_solver(scene_tuple, solver, loops, heuristic_rdf)
        testbase.test_solver(situation_tuple, solver, loops)


def test_forall_vars_advance_all_bound_vehicles():
    """forall_vars lets a single Action tick advance EVERY vehicle bound by
    the precondition query into ONE shared successor graph, instead of the
    default select_dict_list behaviour that branches into one successor
    graph PER matched row. Uses three independent cars, each on its own
    lane pair, so the row count (3) is unambiguous evidence of what would
    otherwise be 3 separate successor states.
    """
    predicates = predicates_simple()
    is_on = predicates['is_on']
    has_successor = predicates['has_successor']

    car1 = SDObject('car1', 'VEHICLE')
    car2 = SDObject('car2', 'VEHICLE')
    car3 = SDObject('car3', 'VEHICLE')
    lane_a1 = SDObject('lane_a1', 'LANE')
    lane_a2 = SDObject('lane_a2', 'LANE')
    lane_b1 = SDObject('lane_b1', 'LANE')
    lane_b2 = SDObject('lane_b2', 'LANE')
    lane_c1 = SDObject('lane_c1', 'LANE')
    lane_c2 = SDObject('lane_c2', 'LANE')

    object_map = {
        o.name: o
        for o in (car1, car2, car3, lane_a1, lane_a2, lane_b1, lane_b2, lane_c1, lane_c2)
    }
    scene_relations = {
        is_on: [[car1, lane_a1], [car2, lane_b1], [car3, lane_c1]],
        has_successor: [[lane_a1, lane_a2], [lane_b1, lane_b2], [lane_c1, lane_c2]],
    }
    CurrentScene = Scene(object_map, scene_relations)
    rdf_wrapper = CurrentScene.init_rdf_wrapper()
    current_graph = rdf_wrapper.data_graph

    precondition = """
                PREFIX situ: <http://example.org/Situ#>
                SELECT ?c ?from ?to
                WHERE {
                        ?c situ:is_on ?from .
                        ?from situ:has_successor ?to .
                }
            """

    def make_action(forall):
        return Action(
            'ADVANCE_ALL_VEHICLES',
            precondition,
            [{is_on: ['c', 'to']}],
            [{is_on: ['c', 'from']}],
            ['c', 'from', 'to'],
            forall_vars=['c', 'from', 'to'] if forall else None,
        )

    # baseline: default behaviour branches into one successor graph per row
    branching_action = make_action(forall=False)
    branching_action.init_action_with_rdf(rdf_wrapper)
    assert branching_action.check_precondition_on_rdf(current_graph) is True
    assert len(branching_action.select_dict_list) == 3
    branching_result = branching_action.execute_action_on_rdf(current_graph)
    assert len(branching_result) == 3

    # forall_vars: all three matched rows collapse into ONE successor graph
    forall_action = make_action(forall=True)
    forall_action.init_action_with_rdf(rdf_wrapper)
    assert forall_action.check_precondition_on_rdf(current_graph) is True
    assert len(forall_action.select_dict_list) == 3
    forall_result = forall_action.execute_action_on_rdf(current_graph)
    assert len(forall_result) == 1

    new_graph = next(iter(forall_result))
    for car, old_lane, new_lane in (
        (car1, lane_a1, lane_a2),
        (car2, lane_b1, lane_b2),
        (car3, lane_c1, lane_c2),
    ):
        car_uri = rdf_wrapper.sd_rdf_dict[car]
        is_on_uri = rdf_wrapper.sd_rdf_dict[is_on]
        old_uri = rdf_wrapper.sd_rdf_dict[old_lane]
        new_uri = rdf_wrapper.sd_rdf_dict[new_lane]
        assert (car_uri, is_on_uri, new_uri) in new_graph
        assert (car_uri, is_on_uri, old_uri) not in new_graph
        # original scene graph stays untouched
        assert (car_uri, is_on_uri, old_uri) in current_graph


if __name__ == "__main__":

    test_scenario20()
    test_scenario_KN()
    test_forall_vars_advance_all_bound_vehicles()
