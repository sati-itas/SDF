from typing import Dict

from sdf.core.sdf_core import Action
from sdf.core.sdf_core import Predicate
from sdf.data.otype import OType


def hanoi_predicates() -> Dict[str, Predicate]:

    # Definition Predicates
    smaller = Predicate("smaller")
    is_on = Predicate("is_on")
    clear = Predicate("clear")

    predicate_dict = {'smaller': smaller, 'is_on': is_on, 'clear': clear}
    return predicate_dict


def actions_simple(predicate_dict):

    is_on = predicate_dict['is_on']
    clear = predicate_dict['clear']

    # SPARQL Query according: https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#QueryForms
    # prepared for rdflib in python: https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html

    move_precondition1 = """
                PREFIX pre: <http://example.org/predicate#>
                SELECT ?disc ?from ?to ?clear
                WHERE {
                        ?disk pre:smaller ?to .
                        ?disc pre:is_on ?from .
                        ?disc pre:clear ?clear .
                        ?to pre:clear ?clear .
                }
            """

    move1 = Action(
        'move',
        move_precondition1,
        [{is_on: ["disc", "to"]}, {clear: ["from", "clear"]}],
        [{is_on: ["disc", "from"]}, {clear: ["to", "clear"]}],
        ["disc", "from", "to", "clear"],
    )

    move2 = Action(
        'move',
        move_precondition1,
        [{is_on: ["to", "disc"]}, {clear: ["disc", "clear"]}],
        [{is_on: ["disc", "from"]}, {clear: ["to", "clear"]}],
        ["disc", "from", "to", "clear"],
    )

    action_list = [move1]

    return action_list


def hanoi_heuristic(state, goal_scene):
    # count the number of facts in the goal scene that are not in the current state
    return sum(1 for fact in goal_scene.scene_relations.items() if fact not in state.scene_relations.items())


def hanoi_heuristic_rdf(state, goal_scene):
    # count the number of facts in the goal scene that are not in the current state
    return sum(1 for fact in goal_scene.scene_relations.items() if fact not in state.scene_relations.items())
