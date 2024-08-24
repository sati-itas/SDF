from typing import Dict

from core.sdf_core import Action
from core.sdf_core import Predicate


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
    move_precondition0 = """
                PREFIX pre: <predicate:>
                PREFIX attr: <NONE:>
                SELECT ?disc ?from ?to
                WHERE {
                        ?to pre:smaller ?disc .
                        ?disc pre:is_on ?from .
                        ?disc pre:clear attr:o_clear .
                        ?to pre:clear attr:o_clear .
                }
            """
    move_precondition1 = """
                PREFIX pre: <predicate:>
                SELECT ?disc ?from ?to ?clear
                WHERE {
                        ?to pre:smaller ?disc .
                        ?disc pre:is_on ?from .
                        ?disc pre:clear ?clear .
                        ?to pre:clear ?clear .
                }
            """

    move0 = Action(
        'move',
        move_precondition0,
        [{is_on: ["disc", "to"]}, {clear: ["from", "o_clear"]}],
        [{is_on: ["disc", "from"]}, {clear: ["to", "o_clear"]}],
        ["disc", "from", "to"],
    )

    move1 = Action(
        'move',
        move_precondition1,
        [{is_on: ["disc", "to"]}, {clear: ["from", "clear"]}],
        [{is_on: ["disc", "from"]}, {clear: ["to", "clear"]}],
        ["disc", "from", "to", "clear"],
    )

    action_list = [move1]

    return action_list
