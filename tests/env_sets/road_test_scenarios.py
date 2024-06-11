import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from core.sdf_core import SDLObject, Scene, OType


def scenario_5(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    lane6 = SDLObject("lane6", OType.LANE)

    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5, lane6]

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
    rel_is_on = {is_on: [Car1, lane3]}

    rel_has_right_neighbour = {has_right_neighbour: [[lane2, lane1], [lane4, lane3], [lane6, lane5]]}

    rel_has_left_neighbour = {has_left_neighbour: [[lane1, lane2], [lane3, lane4], [lane5, lane6]]}

    rel_has_successor = {has_successor: [[lane1, lane3], [lane3, lane5], [lane2, lane4], [lane4, lane6]]}

    rel_has_predecessor = {has_predecessor: [[lane3, lane1], [lane5, lane3], [lane4, lane2], [lane6, lane4]]}

    goal_rel_is_on = {is_on_lane: [Agent, lane5]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_10(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    lane6 = SDLObject("lane6", OType.LANE)
    lane7 = SDLObject("lane7", OType.LANE)
    lane8 = SDLObject("lane8", OType.LANE)
    lane9 = SDLObject("lane9", OType.LANE)
    lane10 = SDLObject("lane10", OType.LANE)

    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5, lane6, lane7, lane8, lane9, lane10]

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
    rel_is_on = {is_on: [Car1, lane5]}

    rel_has_right_neighbour = {
        has_right_neighbour: [[lane2, lane1], [lane4, lane3], [lane6, lane5], [lane8, lane7], [lane10, lane9]]
    }

    rel_has_left_neighbour = {
        has_left_neighbour: [[lane1, lane2], [lane3, lane4], [lane5, lane6], [lane7, lane8], [lane9, lane10]]
    }

    rel_has_successor = {
        has_successor: [
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
        has_predecessor: [
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

    goal_rel_is_on = {is_on_lane: [Agent, lane9]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_15(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    lane6 = SDLObject("lane6", OType.LANE)
    lane7 = SDLObject("lane7", OType.LANE)
    lane8 = SDLObject("lane8", OType.LANE)
    lane9 = SDLObject("lane9", OType.LANE)
    lane10 = SDLObject("lane10", OType.LANE)
    lane11 = SDLObject("lane11", OType.LANE)
    lane12 = SDLObject("lane12", OType.LANE)
    lane13 = SDLObject("lane13", OType.LANE)
    lane14 = SDLObject("lane14", OType.LANE)
    lane15 = SDLObject("lane15", OType.LANE)
    lane16 = SDLObject("lane16", OType.LANE)

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
    rel_is_on = {is_on: [Car1, lane5]}

    rel_has_right_neighbour = {
        has_right_neighbour: [
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
        has_left_neighbour: [
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
        has_successor: [
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
        has_predecessor: [
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

    goal_rel_is_on = {is_on_lane: [Agent, lane15]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_20(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    lane6 = SDLObject("lane6", OType.LANE)
    lane7 = SDLObject("lane7", OType.LANE)
    lane8 = SDLObject("lane8", OType.LANE)
    lane9 = SDLObject("lane9", OType.LANE)
    lane10 = SDLObject("lane10", OType.LANE)
    lane11 = SDLObject("lane11", OType.LANE)
    lane12 = SDLObject("lane12", OType.LANE)
    lane13 = SDLObject("lane13", OType.LANE)
    lane14 = SDLObject("lane14", OType.LANE)
    lane15 = SDLObject("lane15", OType.LANE)
    lane16 = SDLObject("lane16", OType.LANE)
    lane17 = SDLObject("lane17", OType.LANE)
    lane18 = SDLObject("lane18", OType.LANE)
    lane19 = SDLObject("lane19", OType.LANE)
    lane20 = SDLObject("lane20", OType.LANE)

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
    rel_is_on = {is_on: [Car1, lane6]}

    rel_has_right_neighbour = {
        has_right_neighbour: [
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
        has_left_neighbour: [
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
        has_successor: [
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
        has_predecessor: [
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

    goal_rel_is_on = {is_on_lane: [Agent, lane18]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_30(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    lane6 = SDLObject("lane6", OType.LANE)
    lane7 = SDLObject("lane7", OType.LANE)
    lane8 = SDLObject("lane8", OType.LANE)
    lane9 = SDLObject("lane9", OType.LANE)
    lane10 = SDLObject("lane10", OType.LANE)
    lane11 = SDLObject("lane11", OType.LANE)
    lane12 = SDLObject("lane12", OType.LANE)
    lane13 = SDLObject("lane13", OType.LANE)
    lane14 = SDLObject("lane14", OType.LANE)
    lane15 = SDLObject("lane15", OType.LANE)
    lane16 = SDLObject("lane16", OType.LANE)
    lane17 = SDLObject("lane17", OType.LANE)
    lane18 = SDLObject("lane18", OType.LANE)
    lane19 = SDLObject("lane19", OType.LANE)
    lane20 = SDLObject("lane20", OType.LANE)
    lane21 = SDLObject("lane21", OType.LANE)
    lane22 = SDLObject("lane22", OType.LANE)
    lane23 = SDLObject("lane23", OType.LANE)
    lane24 = SDLObject("lane24", OType.LANE)
    lane25 = SDLObject("lane25", OType.LANE)
    lane26 = SDLObject("lane26", OType.LANE)
    lane27 = SDLObject("lane27", OType.LANE)
    lane28 = SDLObject("lane28", OType.LANE)
    lane29 = SDLObject("lane29", OType.LANE)
    lane30 = SDLObject("lane30", OType.LANE)

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
    rel_is_on = {is_on: [Car1, lane5]}

    rel_has_right_neighbour = {
        has_right_neighbour: [
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
        has_left_neighbour: [
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
        has_successor: [
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
        has_predecessor: [
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

    goal_rel_is_on = {is_on_lane: [Agent, lane29]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def scenario_3_lane(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    lane6 = SDLObject("lane6", OType.LANE)
    lane7 = SDLObject("lane7", OType.LANE)
    lane8 = SDLObject("lane8", OType.LANE)
    lane9 = SDLObject("lane9", OType.LANE)
    lane10 = SDLObject("lane10", OType.LANE)
    lane11 = SDLObject("lane11", OType.LANE)
    lane12 = SDLObject("lane12", OType.LANE)
    lane13 = SDLObject("lane13", OType.LANE)
    lane14 = SDLObject("lane14", OType.LANE)
    lane15 = SDLObject("lane15", OType.LANE)
    lane16 = SDLObject("lane16", OType.LANE)
    lane17 = SDLObject("lane17", OType.LANE)
    lane18 = SDLObject("lane18", OType.LANE)
    lane19 = SDLObject("lane19", OType.LANE)
    lane20 = SDLObject("lane20", OType.LANE)
    lane21 = SDLObject("lane21", OType.LANE)
    lane22 = SDLObject("lane22", OType.LANE)
    lane23 = SDLObject("lane23", OType.LANE)
    lane24 = SDLObject("lane24", OType.LANE)
    lane25 = SDLObject("lane25", OType.LANE)
    lane26 = SDLObject("lane26", OType.LANE)
    lane27 = SDLObject("lane27", OType.LANE)
    lane28 = SDLObject("lane28", OType.LANE)

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
    rel_is_on = {is_on: [Car1, lane6]}

    rel_has_right_neighbour = {
        has_right_neighbour: [
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
        has_left_neighbour: [
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
        has_successor: [
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
        has_predecessor: [
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

    goal_rel_is_on = {is_on_lane: [Agent, lane18]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions


def Ramp_On(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5]

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
    rel_is_on = {is_on: [Car1, lane3]}
    rel_has_right_neighbour = {has_right_neighbour: [[lane4, lane2], [lane5, lane3]]}
    rel_has_left_neighbour = {has_left_neighbour: [[lane2, lane4], [lane3, lane5]]}
    rel_has_successor = {has_successor: [[lane1, lane2], [lane2, lane3], [lane4, lane5]]}
    rel_has_predecessor = {has_predecessor: [[lane2, lane1], [lane3, lane2], [lane5, lane4]]}

    goal_rel_is_on = {is_on_lane: [Agent, lane5]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    InitScene

    return InitScene, GoalScene, actions


def Ramp_Off(predicates, actions):

    # Instanziierung Objekte
    Agent = SDLObject("ego", OType.EGO)
    Car1 = SDLObject("car1", OType.VEHICLE)
    lane1 = SDLObject("lane1", OType.LANE)
    lane2 = SDLObject("lane2", OType.LANE)
    lane3 = SDLObject("lane3", OType.LANE)
    lane4 = SDLObject("lane4", OType.LANE)
    lane5 = SDLObject("lane5", OType.LANE)
    object_list = [Agent, Car1, lane1, lane2, lane3, lane4, lane5]

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
    rel_is_on = {is_on: [Car1, lane2]}
    rel_has_right_neighbour = {has_right_neighbour: [[lane1, lane2], [lane3, lane4], [lane4, lane5]]}
    rel_has_left_neighbour = {has_left_neighbour: [[lane2, lane1], [lane4, lane3], [lane5, lane4]]}
    rel_has_successor = {has_successor: [[lane1, lane3], [lane2, lane4]]}
    rel_has_predecessor = {has_predecessor: [[lane3, lane1], [lane4, lane2]]}

    goal_rel_is_on = {is_on_lane: [Agent, lane5]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {
        **rel_is_on,
        **rel_is_on_lane,
        **rel_has_right_neighbour,
        **rel_has_left_neighbour,
        **rel_has_successor,
        **rel_has_predecessor,
    }
    InitScene = Scene(object_list, init_scene, predicate_list)
    GoalScene = Scene(object_list, goal_scene, predicate_list)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions
