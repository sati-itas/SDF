# run env_sets/gen_pred_action_from_dar.enum_gen()
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from core.sdf_core import SDObject, Scene, Action

from data._gen.domain_otypes import DomainTypes
from data._gen.domain_scenery import Scenery
from data._gen.domain_dyn_object import DynamicObject
from data._gen.domain_location import Location
from data._gen.domain_self import SelfRepresentation


def actions_light(predicate_dict, base):

    has_lane_assignment = 'has_lane_assignment'
    print(base)
    base_uri = 'http://example.org/predicate#'


    # SPARQL Query according: https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#QueryForms
    # prepared for rdflib in python: https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html
    lc_right_precondition = f"""
                PREFIX ex: <{base_uri}>
                PREFIX ego: <http://example.org/SelfRepresentation.EGO#>
                SELECT ?x ?y ?v ?e
                WHERE {{
                        ?e ex:has_lane_assignment ?x .
                        ?x ex:has_right_neighbour ?y .
                        FILTER NOT EXISTS {{?v ex:has_lane_assignment ?y .}} 
                        FILTER (?e = ego:ego)
                }}
            """

    lc_left_precondition = f"""
                PREFIX ex: <{base_uri}>
                PREFIX ego: <http://example.org/SelfRepresentation.EGO#>
                SELECT ?y ?x ?v ?e
                WHERE {{
                        ?e ex:has_lane_assignment ?x .
                        ?x ex:has_left_neighbour ?y .
                        FILTER NOT EXISTS {{ ?v ex:has_lane_assignment ?y.}}
                        FILTER (?e = ego:ego)
                }}
            """

    l_keep_precondition = f"""
                PREFIX ex: <{base_uri}>
                PREFIX ego: <http://example.org/SelfRepresentation.EGO#>
                SELECT ?y ?x ?v ?e
                WHERE {{
                        ?e ex:has_lane_assignment ?x .
                        ?x ex:has_successor ?y .
                        FILTER NOT EXISTS {{ ?v ex:has_lane_assignment ?y}}
                        FILTER (?e = ego:ego)
                }}
            """
    
    has_lane_assignment = predicate_dict['has_lane_assignment']
    # Definition of Actions
    lc_right = Action(
        'LANE_CHANGE_RIGHT',
        lc_right_precondition,
        [{has_lane_assignment: ["e", "y"]}],
        [{has_lane_assignment: ["e", "x"]}],
        ["e", "y", "x", "v"],
    )
    lc_left = Action(
        'LANE_CHANGE_LEFT',
        lc_left_precondition,
        [{has_lane_assignment: ["e", "y"]}],
        [{has_lane_assignment: ["e", "x"]}],
        ["e", "y", "x", "v"],
    )
    lc_keep = Action(
        'LANE_KEEPING',
        l_keep_precondition,
        [{has_lane_assignment: ["e", "y"]}],
        [{has_lane_assignment: ["e", "x"]}],
        ["e", "y", "x", "v"],
    )

    action_list = [lc_right, lc_left, lc_keep]

    return action_list


def scenario_5gen(predicates, actions):

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

    # generate init-scene
    rel_has_lane_assignment = {predicates['has_lane_assignment']: [[Agent, lane1],[Car1, lane3]]}
    #rel_is_on = {has_lane_assignment: [Car1, lane3]}

    rel_has_right_neighbour = {predicates['has_right_neighbour']: [[lane2, lane1], [lane4, lane3], [lane6, lane5]]}

    rel_has_left_neighbour = {predicates['has_left_neighbour']: [[lane1, lane2], [lane3, lane4], [lane5, lane6]]}

    rel_has_successor = {predicates['has_successor']: [[lane1, lane3], [lane3, lane5], [lane2, lane4], [lane4, lane6]]}

    rel_has_predecessor = {predicates['has_predecessor']: [[lane3, lane1], [lane5, lane3], [lane4, lane2], [lane6, lane4]]}

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane5]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_has_lane_assignment,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_10(predicates, actions):

    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    lane6 = SDObject("lane6", Scenery.LANESEGMENT)
    lane7 = SDObject("lane7", Scenery.LANESEGMENT)
    lane8 = SDObject("lane8", Scenery.LANESEGMENT)
    lane9 = SDObject("lane9", Scenery.LANESEGMENT)
    lane10 = SDObject("lane10", Scenery.LANESEGMENT)

    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5, lane6, lane7, lane8, lane9, lane10]


    # generate init-scene
    rel_is_on_lane = {predicates['has_lane_assignment']: [Agent, lane1]}
    rel_is_on = {predicates['has_lane_assignment']: [Car1, lane5]}

    rel_has_right_neighbour = {
        predicates['has_right_neighbour']: [[lane2, lane1], [lane4, lane3], [lane6, lane5], [lane8, lane7], [lane10, lane9]]
    }

    rel_has_left_neighbour = {
        predicates['has_left_neighbour']: [[lane1, lane2], [lane3, lane4], [lane5, lane6], [lane7, lane8], [lane9, lane10]]
    }

    rel_has_successor = {
        predicates['has_successor']: [
            [lane1, lane3],
            [lane3, lane5],
            [lane5, lane7],
            [lane7, lane9],
            [lane2, lane4],
            [lane4, lane6],
            [lane6, lane8],
            [lane8, lane10],
        ]
    }

    rel_has_predecessor = {
        predicates['has_predecessor']: [
            [lane3, lane1],
            [lane5, lane3],
            [lane7, lane5],
            [lane9, lane7],
            [lane4, lane2],
            [lane6, lane4],
            [lane8, lane6],
            [lane10, lane8],
        ]
    }

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane9]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_15(predicates, actions):

    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    lane6 = SDObject("lane6", Scenery.LANESEGMENT)
    lane7 = SDObject("lane7", Scenery.LANESEGMENT)
    lane8 = SDObject("lane8", Scenery.LANESEGMENT)
    lane9 = SDObject("lane9", Scenery.LANESEGMENT)
    lane10 = SDObject("lane10", Scenery.LANESEGMENT)
    lane11 = SDObject("lane11", Scenery.LANESEGMENT)
    lane12 = SDObject("lane12", Scenery.LANESEGMENT)
    lane13 = SDObject("lane13", Scenery.LANESEGMENT)
    lane14 = SDObject("lane14", Scenery.LANESEGMENT)
    lane15 = SDObject("lane15", Scenery.LANESEGMENT)
    lane16 = SDObject("lane16", Scenery.LANESEGMENT)

    object_list = [
        Agent,
        Car1,
        lane1,
        lane2,
        lane3,
        lane4,
        lane5,
        lane6,
        lane7,
        lane8,
        lane9,
        lane10,
        lane11,
        lane12,
        lane13,
        lane14,
        lane15,
        lane16,
    ]

    # generate init-scene
    rel_is_on_lane = {predicates['has_lane_assignment']: [Agent, lane1]}
    rel_is_on = {predicates['has_lane_assignment']: [Car1, lane5]}

    rel_has_right_neighbour = {
        predicates['has_right_neighbour']: [
            [lane2, lane1],
            [lane4, lane3],
            [lane6, lane5],
            [lane8, lane7],
            [lane10, lane9],
            [lane12, lane11],
            [lane14, lane13],
            [lane16, lane15],
        ]
    }

    rel_has_left_neighbour = {
        predicates['has_left_neighbour']: [
            [lane1, lane2],
            [lane3, lane4],
            [lane5, lane6],
            [lane7, lane8],
            [lane9, lane10],
            [lane11, lane12],
            [lane13, lane14],
            [lane15, lane16],
        ]
    }

    rel_has_successor = {
        predicates['has_successor']: [
            [lane1, lane3],
            [lane3, lane5],
            [lane5, lane7],
            [lane7, lane9],
            [lane9, lane11],
            [lane11, lane13],
            [lane13, lane15],
            [lane2, lane4],
            [lane4, lane6],
            [lane6, lane8],
            [lane8, lane10],
            [lane10, lane12],
            [lane12, lane14],
            [lane14, lane16],
        ]
    }

    rel_has_predecessor = {
        predicates['has_predecessor']: [
            [lane3, lane1],
            [lane5, lane3],
            [lane7, lane5],
            [lane9, lane7],
            [lane11, lane9],
            [lane13, lane11],
            [lane15, lane13],
            [lane4, lane2],
            [lane6, lane4],
            [lane8, lane6],
            [lane10, lane8],
            [lane12, lane10],
            [lane14, lane12],
            [lane16, lane14],
        ]
    }

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane15]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_20(predicates, actions):

    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    lane6 = SDObject("lane6", Scenery.LANESEGMENT)
    lane7 = SDObject("lane7", Scenery.LANESEGMENT)
    lane8 = SDObject("lane8", Scenery.LANESEGMENT)
    lane9 = SDObject("lane9", Scenery.LANESEGMENT)
    lane10 = SDObject("lane10", Scenery.LANESEGMENT)
    lane11 = SDObject("lane11", Scenery.LANESEGMENT)
    lane12 = SDObject("lane12", Scenery.LANESEGMENT)
    lane13 = SDObject("lane13", Scenery.LANESEGMENT)
    lane14 = SDObject("lane14", Scenery.LANESEGMENT)
    lane15 = SDObject("lane15", Scenery.LANESEGMENT)
    lane16 = SDObject("lane16", Scenery.LANESEGMENT)
    lane17 = SDObject("lane17", Scenery.LANESEGMENT)
    lane18 = SDObject("lane18", Scenery.LANESEGMENT)
    lane19 = SDObject("lane19", Scenery.LANESEGMENT)
    lane20 = SDObject("lane20", Scenery.LANESEGMENT)

    object_list = [
        Agent,
        Car1,
        lane1,
        lane2,
        lane3,
        lane4,
        lane5,
        lane6,
        lane7,
        lane8,
        lane9,
        lane10,
        lane11,
        lane12,
        lane13,
        lane14,
        lane15,
        lane16,
        lane17,
        lane18,
        lane19,
        lane20,
    ]

    # generate init-scene
    rel_is_on_lane = {predicates['has_lane_assignment']: [Agent, lane1]}
    rel_is_on = {predicates['has_lane_assignment']: [Car1, lane6]}

    rel_has_right_neighbour = {
        predicates['has_right_neighbour']: [
            [lane20, lane1],
            [lane3, lane2],
            [lane5, lane4],
            [lane7, lane6],
            [lane9, lane8],
            [lane11, lane10],
            [lane13, lane12],
            [lane15, lane14],
            [lane17, lane16],
            [lane19, lane18],
        ]
    }

    rel_has_left_neighbour = {
        predicates['has_left_neighbour']: [
            [lane1, lane20],
            [lane2, lane3],
            [lane4, lane5],
            [lane6, lane7],
            [lane8, lane9],
            [lane10, lane11],
            [lane12, lane13],
            [lane14, lane15],
            [lane16, lane17],
            [lane18, lane19],
        ]
    }

    rel_has_successor = {
        predicates['has_successor']: [
            [lane20, lane3],
            [lane1, lane2],
            [lane2, lane4],
            [lane4, lane6],
            [lane6, lane8],
            [lane8, lane10],
            [lane10, lane12],
            [lane12, lane14],
            [lane14, lane16],
            [lane16, lane18],
            [lane3, lane5],
            [lane5, lane7],
            [lane7, lane9],
            [lane9, lane11],
            [lane11, lane13],
            [lane13, lane15],
            [lane15, lane17],
            [lane17, lane19],
        ]
    }

    rel_has_predecessor = {
        predicates['has_predecessor']: [
            [lane3, lane20],
            [lane2, lane1],
            [lane4, lane2],
            [lane6, lane4],
            [lane8, lane6],
            [lane10, lane8],
            [lane12, lane10],
            [lane14, lane12],
            [lane16, lane14],
            [lane18, lane16],
            [lane5, lane3],
            [lane7, lane5],
            [lane9, lane7],
            [lane11, lane9],
            [lane13, lane11],
            [lane15, lane13],
            [lane17, lane15],
            [lane19, lane17],
        ]
    }

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane18]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_30(predicates, actions):

    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    lane6 = SDObject("lane6", Scenery.LANESEGMENT)
    lane7 = SDObject("lane7", Scenery.LANESEGMENT)
    lane8 = SDObject("lane8", Scenery.LANESEGMENT)
    lane9 = SDObject("lane9", Scenery.LANESEGMENT)
    lane10 = SDObject("lane10", Scenery.LANESEGMENT)
    lane11 = SDObject("lane11", Scenery.LANESEGMENT)
    lane12 = SDObject("lane12", Scenery.LANESEGMENT)
    lane13 = SDObject("lane13", Scenery.LANESEGMENT)
    lane14 = SDObject("lane14", Scenery.LANESEGMENT)
    lane15 = SDObject("lane15", Scenery.LANESEGMENT)
    lane16 = SDObject("lane16", Scenery.LANESEGMENT)
    lane17 = SDObject("lane17", Scenery.LANESEGMENT)
    lane18 = SDObject("lane18", Scenery.LANESEGMENT)
    lane19 = SDObject("lane19", Scenery.LANESEGMENT)
    lane20 = SDObject("lane20", Scenery.LANESEGMENT)
    lane21 = SDObject("lane21", Scenery.LANESEGMENT)
    lane22 = SDObject("lane22", Scenery.LANESEGMENT)
    lane23 = SDObject("lane23", Scenery.LANESEGMENT)
    lane24 = SDObject("lane24", Scenery.LANESEGMENT)
    lane25 = SDObject("lane25", Scenery.LANESEGMENT)
    lane26 = SDObject("lane26", Scenery.LANESEGMENT)
    lane27 = SDObject("lane27", Scenery.LANESEGMENT)
    lane28 = SDObject("lane28", Scenery.LANESEGMENT)
    lane29 = SDObject("lane29", Scenery.LANESEGMENT)
    lane30 = SDObject("lane30", Scenery.LANESEGMENT)

    object_list = [
        Agent,
        Car1,
        lane1,
        lane2,
        lane3,
        lane4,
        lane5,
        lane6,
        lane7,
        lane8,
        lane9,
        lane10,
        lane11,
        lane12,
        lane13,
        lane14,
        lane15,
        lane16,
        lane17,
        lane18,
        lane19,
        lane20,
        lane21,
        lane22,
        lane23,
        lane24,
        lane25,
        lane26,
        lane27,
        lane28,
        lane29,
        lane30,
    ]

    # generate init-scene
    rel_is_on_lane = {predicates['has_lane_assignment']: [Agent, lane1]}
    rel_is_on = {predicates['has_lane_assignment']: [Car1, lane5]}

    rel_has_right_neighbour = {
        predicates['has_right_neighbour']: [
            [lane2, lane1],
            [lane4, lane3],
            [lane6, lane5],
            [lane8, lane7],
            [lane9, lane10],
            [lane12, lane11],
            [lane14, lane13],
            [lane16, lane15],
            [lane18, lane17],
            [lane20, lane19],
            [lane22, lane21],
            [lane24, lane23],
            [lane26, lane25],
            [lane28, lane27],
            [lane30, lane29],
        ]
    }

    rel_has_left_neighbour = {
        predicates['has_left_neighbour']: [
            [lane1, lane2],
            [lane3, lane4],
            [lane5, lane6],
            [lane7, lane8],
            [lane9, lane10],
            [lane11, lane12],
            [lane13, lane14],
            [lane15, lane16],
            [lane17, lane18],
            [lane19, lane20],
            [lane21, lane22],
            [lane23, lane24],
            [lane25, lane26],
            [lane27, lane28],
            [lane29, lane30],
        ]
    }

    rel_has_successor = {
        predicates['has_successor']: [
            [lane1, lane3],
            [lane3, lane5],
            [lane5, lane7],
            [lane7, lane9],
            [lane2, lane4],
            [lane4, lane6],
            [lane6, lane8],
            [lane8, lane10],
            [lane11, lane13],
            [lane13, lane15],
            [lane15, lane17],
            [lane17, lane19],
            [lane12, lane14],
            [lane14, lane16],
            [lane16, lane18],
            [lane18, lane20],
            [lane21, lane23],
            [lane23, lane25],
            [lane25, lane27],
            [lane27, lane29],
            [lane22, lane24],
            [lane24, lane26],
            [lane26, lane28],
            [lane28, lane30],
        ]
    }

    rel_has_predecessor = {
        predicates['has_predecessor']: [
            [lane3, lane1],
            [lane5, lane3],
            [lane7, lane5],
            [lane9, lane7],
            [lane4, lane2],
            [lane6, lane4],
            [lane8, lane6],
            [lane10, lane8],
            [lane13, lane11],
            [lane15, lane13],
            [lane17, lane15],
            [lane19, lane17],
            [lane14, lane12],
            [lane16, lane14],
            [lane18, lane16],
            [lane20, lane18],
            [lane23, lane21],
            [lane25, lane23],
            [lane27, lane25],
            [lane29, lane27],
            [lane24, lane22],
            [lane26, lane24],
            [lane28, lane26],
            [lane30, lane28],
        ]
    }

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane29]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_3_lane(predicates, actions):

    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    lane6 = SDObject("lane6", Scenery.LANESEGMENT)
    lane7 = SDObject("lane7", Scenery.LANESEGMENT)
    lane8 = SDObject("lane8", Scenery.LANESEGMENT)
    lane9 = SDObject("lane9", Scenery.LANESEGMENT)
    lane10 = SDObject("lane10", Scenery.LANESEGMENT)
    lane11 = SDObject("lane11", Scenery.LANESEGMENT)
    lane12 = SDObject("lane12", Scenery.LANESEGMENT)
    lane13 = SDObject("lane13", Scenery.LANESEGMENT)
    lane14 = SDObject("lane14", Scenery.LANESEGMENT)
    lane15 = SDObject("lane15", Scenery.LANESEGMENT)
    lane16 = SDObject("lane16", Scenery.LANESEGMENT)
    lane17 = SDObject("lane17", Scenery.LANESEGMENT)
    lane18 = SDObject("lane18", Scenery.LANESEGMENT)
    lane19 = SDObject("lane19", Scenery.LANESEGMENT)
    lane20 = SDObject("lane20", Scenery.LANESEGMENT)
    lane21 = SDObject("lane21", Scenery.LANESEGMENT)
    lane22 = SDObject("lane22", Scenery.LANESEGMENT)
    lane23 = SDObject("lane23", Scenery.LANESEGMENT)
    lane24 = SDObject("lane24", Scenery.LANESEGMENT)
    lane25 = SDObject("lane25", Scenery.LANESEGMENT)
    lane26 = SDObject("lane26", Scenery.LANESEGMENT)
    lane27 = SDObject("lane27", Scenery.LANESEGMENT)
    lane28 = SDObject("lane28", Scenery.LANESEGMENT)

    object_list = [
        Agent,
        Car1,
        lane1,
        lane2,
        lane3,
        lane4,
        lane5,
        lane6,
        lane7,
        lane8,
        lane9,
        lane10,
        lane11,
        lane12,
        lane13,
        lane14,
        lane15,
        lane16,
        lane17,
        lane18,
        lane19,
        lane20,
        lane21,
        lane22,
        lane23,
        lane24,
        lane25,
        lane26,
        lane27,
        lane28,
    ]

    # generate init-scene
    rel_is_on_lane = {predicates['has_lane_assignment']: [Agent, lane1]}
    rel_is_on = {predicates['has_lane_assignment']: [Car1, lane6]}

    rel_has_right_neighbour = {
        predicates['has_right_neighbour']: [
            [lane3, lane2],
            [lane5, lane4],
            [lane7, lane6],
            [lane9, lane8],
            [lane11, lane10],
            [lane13, lane12],
            [lane15, lane14],
            [lane17, lane16],
            [lane19, lane18],
            [lane2, lane20],
            [lane4, lane21],
            [lane6, lane22],
            [lane8, lane23],
            [lane10, lane24],
            [lane12, lane25],
            [lane14, lane26],
            [lane16, lane27],
            [lane18, lane28],
        ]
    }

    rel_has_left_neighbour = {
        predicates['has_left_neighbour']: [
            [lane2, lane3],
            [lane4, lane5],
            [lane6, lane7],
            [lane8, lane9],
            [lane10, lane11],
            [lane12, lane13],
            [lane14, lane15],
            [lane16, lane17],
            [lane18, lane19],
            [lane20, lane2],
            [lane21, lane4],
            [lane22, lane6],
            [lane23, lane8],
            [lane24, lane10],
            [lane25, lane12],
            [lane26, lane14],
            [lane27, lane16],
            [lane28, lane18],
        ]
    }

    rel_has_successor = {
        predicates['has_successor']: [
            [lane1, lane2],
            [lane2, lane4],
            [lane4, lane6],
            [lane6, lane8],
            [lane8, lane10],
            [lane10, lane12],
            [lane12, lane14],
            [lane14, lane16],
            [lane16, lane18],
            [lane3, lane5],
            [lane5, lane7],
            [lane7, lane9],
            [lane9, lane11],
            [lane11, lane13],
            [lane13, lane15],
            [lane15, lane17],
            [lane17, lane19],
            [lane20, lane21],
            [lane21, lane22],
            [lane22, lane23],
            [lane23, lane24],
            [lane24, lane25],
            [lane25, lane26],
            [lane25, lane26],
            [lane26, lane27],
            [lane27, lane28],
        ]
    }

    rel_has_predecessor = {
        predicates['has_predecessor']: [
            [lane2, lane1],
            [lane4, lane2],
            [lane6, lane4],
            [lane8, lane6],
            [lane10, lane8],
            [lane12, lane10],
            [lane14, lane12],
            [lane16, lane14],
            [lane18, lane16],
            [lane5, lane3],
            [lane7, lane5],
            [lane9, lane7],
            [lane11, lane9],
            [lane13, lane11],
            [lane15, lane13],
            [lane17, lane15],
            [lane19, lane17],
            [lane21, lane20],
            [lane22, lane21],
            [lane23, lane22],
            [lane24, lane23],
            [lane25, lane24],
            [lane26, lane25],
            [lane27, lane26],
            [lane28, lane27],
        ]
    }

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane18]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def Ramp_On(predicates, actions):

    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5]

    # generate init-scene
    rel_is_on_lane = {predicates['has_lane_assignment']: [Agent, lane1]}
    rel_is_on = {predicates['has_lane_assignment']: [Car1, lane3]}
    rel_has_right_neighbour = {predicates['has_right_neighbour']: [[lane4, lane2], [lane5, lane3]]}
    rel_has_left_neighbour = {predicates['has_left_neighbour']: [[lane2, lane4], [lane3, lane5]]}
    rel_has_successor = {predicates['has_successor']: [[lane1, lane2], [lane2, lane3], [lane4, lane5]]}
    rel_has_predecessor = {predicates['has_predecessor']: [[lane2, lane1], [lane3, lane2], [lane5, lane4]]}

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane5]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    InitScene

    return InitScene, GoalScene, actions


def Ramp_Off(predicates, actions):

    # instantiate sdf objects
    Agent = SDObject("ego", SelfRepresentation.EGO)
    Car1 = SDObject("car1", DynamicObject.ROADUSER)
    lane1 = SDObject("lane1", Scenery.LANESEGMENT)
    lane2 = SDObject("lane2", Scenery.LANESEGMENT)
    lane3 = SDObject("lane3", Scenery.LANESEGMENT)
    lane4 = SDObject("lane4", Scenery.LANESEGMENT)
    lane5 = SDObject("lane5", Scenery.LANESEGMENT)
    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5]

    # generate init-scene
    rel_is_on_lane = {predicates['has_lane_assignment']: [Agent, lane1]}
    rel_is_on = {predicates['has_lane_assignment']: [Car1, lane2]}
    rel_has_right_neighbour = {predicates['has_right_neighbour']: [[lane1, lane2], [lane3, lane4], [lane4, lane5]]}
    rel_has_left_neighbour = {predicates['has_left_neighbour']: [[lane2, lane1], [lane4, lane3], [lane5, lane4]]}
    rel_has_successor = {predicates['has_successor']: [[lane1, lane3], [lane2, lane4]]}
    rel_has_predecessor = {predicates['has_predecessor']: [[lane3, lane1], [lane4, lane2]]}

    goal_rel_is_on = {predicates['has_lane_assignment']: [Agent, lane5]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene)
    GoalScene = Scene(object_list, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions
