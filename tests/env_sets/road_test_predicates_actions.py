from typing import Dict

from sdf.core.sdf_core import Action
from sdf.core.sdf_core import Predicate
from sdf.core.rdf_wrapper import RDFUtils

from sdf.data.otype import OType


def predicates_simple() -> Dict[str, Predicate]:

    # Definition Predicates
    is_on = Predicate("is_on")  # ego vehicle is on lane
    is_on_lane = Predicate("is_on_lane")  # vehicle is on lane
    has_right_neighbour = Predicate("has_right_neighbour")  # lane has right neighbour
    has_left_neighbour = Predicate("has_left_neighbour")  # lane hast left neighbour
    has_successor = Predicate("has_successor")  # lane has successor lane
    has_predecessor = Predicate("has_predecessor")  # lane has predecessor lane
    has_top_right_neighbour = Predicate("has_top_right_neighbour")  # lane has top right diagonal lane
    has_top_left_neighbour = Predicate("has_top_left_neighbour")  # lane has top left diagonal lane
    has_bottom_right_neighbour = Predicate("has_bottom_right_neighbour")  # lane has bottom right diagonal lane
    has_bottom_left_neighbour = Predicate("has_bootom_left_neighbour")  # lane has bottom left diagonal lane

    predicate_dict = {
        'is_on': is_on,
        'is_on_lane': is_on_lane,
        'has_right_neighbour': has_right_neighbour,
        'has_left_neighbour': has_left_neighbour,
        'has_successor': has_successor,
        'has_predecessor': has_predecessor,
        'has_top_right_neighbour': has_top_right_neighbour,
        'has_top_left_neighbour': has_top_left_neighbour,
        'has_bottom_right_neighbour': has_bottom_right_neighbour,
        'has_bottom_left_neighbour': has_bottom_left_neighbour,
    }
    return predicate_dict

def actions_simple(predicate_dict, base_uri: str = 'http://example.org/knowledge#'):

    is_on_lane = predicate_dict['is_on_lane']

    # SPARQL Query according: https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#QueryForms
    # prepared for rdflib in python: https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html
    lc_right_precondition = f"""
                PREFIX scene: <{base_uri}>
                SELECT ?x ?y ?v ?e
                WHERE {{
                        ?e scene:is_on_lane ?x .
                        ?x scene:has_right_neighbour ?y .
                        FILTER NOT EXISTS {{ ?v scene:is_on ?y}}
                }}
            """

    lc_left_precondition = f"""
                PREFIX scene:   <{base_uri}>
                SELECT ?y ?x ?v ?e
                WHERE {{
                        ?e scene:is_on_lane ?x .
                        ?x scene:has_left_neighbour ?y .
                        FILTER NOT EXISTS {{ ?v scene:is_on ?y}}
                }}
            """

    l_keep_precondition = f"""
                PREFIX scene: <{base_uri}>
                SELECT ?y ?x ?v ?e
                WHERE {{
                        ?e scene:is_on_lane ?x .
                        ?x scene:has_successor ?y .
                        FILTER NOT EXISTS {{ ?v scene:is_on ?y}}
                }}
            """

    # Definition of Actions
    lc_right = Action(
        'LANE_CHANGE_RIGHT',
        lc_right_precondition,
        [{is_on_lane: ["e", "y"]}],
        [{is_on_lane: ["e", "x"]}],
        ["e", "y", "x", "v"],
    )
    lc_left = Action(
        'LANE_CHANGE_LEFT',
        lc_left_precondition,
        [{is_on_lane: ["e", "y"]}],
        [{is_on_lane: ["e", "x"]}],
        ["e", "y", "x", "v"],
    )
    lc_keep = Action(
        'LANE_KEEPING',
        l_keep_precondition,
        [{is_on_lane: ["e", "y"]}],
        [{is_on_lane: ["e", "x"]}],
        ["e", "y", "x", "v"],
    )

    action_list = [lc_right, lc_left, lc_keep]

    return action_list

def manhattan_distance(a: float, b: float) -> float:
    """
    Calculate the Manhattan distance between two points
    """
    return sum(abs(x - y) for x, y in zip(a, b))

def euclidean_distance(a: float, b: float) -> float:
    """
    Calculate the Euclidean distance between two points
    """
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

def make_road_heuristic_sd(predicate_dict):
    def road_heuristic_sd(goal_scene, state):
        is_on_lane = predicate_dict['is_on_lane']
        # calculate the Manhattan distance between the ego vehicle's position in the current state and the goal scene
        lane_state_ego = state.scene_relations[is_on_lane][0][1]
        ego_x = lane_state_ego.x
        ego_y = lane_state_ego.y
        lane_goal_ego = goal_scene.scene_relations[is_on_lane][0][1]
        goal_x = lane_goal_ego.x
        goal_y = lane_goal_ego.y
        return euclidean_distance((ego_x, ego_y), (goal_x, goal_y))
    return road_heuristic_sd

def make_road_heuristic_rdf():
    state_query = """
    PREFIX scene: <http://example.org/knowledge#>
    SELECT ?ego_x ?ego_y
    WHERE {
        ?ego scene:is_on_lane ?ego_lane .
        ?ego_lane scene:x ?ego_x .
        ?ego_lane scene:y ?ego_y .
    }
    """
    goal_query = """
    PREFIX scene: <http://example.org/knowledge#>
    SELECT ?goal_x ?goal_y
    WHERE {
        ?goal scene:is_on_lane ?goal_lane .
        ?goal_lane scene:x ?goal_x .
        ?goal_lane scene:y ?goal_y .
    }
    """
    prep_goal_query = RDFUtils.prepare_sparql_query(goal_query, "http://example.org/knowledge#")
    prep_state_query = RDFUtils.prepare_sparql_query(state_query, "http://example.org/knowledge#")

    def road_heuristic_rdf(goal_scene, state):
        """
        Heuristic function for road scenarios using RDF.
        This function calculates the Manhattan distance between the ego vehicle's position in the current state and the goal scene.
        """
        state_results = RDFUtils.query_rdf_graph(state, prep_state_query)
        goal_results = RDFUtils.query_rdf_graph(goal_scene, prep_goal_query)
        #results = state.rdf_wrapper.query(query)
        # if not goal_results or not state_results:
        #     print("No results found for the heuristic query.")
        #     return 0  # If no results, return infinity as heuristic value
        for row in state_results:
            #print(f"State results: {row}")
            ego_x = float(row['ego_x'][0]) #cast to float ego
            ego_y = float(row['ego_y'][0])
        for row in goal_results:
            #print(f"Goal results: {row}")
            goal_x = float(row['goal_x'][0])
            goal_y = float(row['goal_y'][0])
        return manhattan_distance((ego_x, ego_y), (goal_x, goal_y))
    return road_heuristic_rdf



