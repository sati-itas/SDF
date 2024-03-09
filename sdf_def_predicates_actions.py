from sdf_core import Predicate ,Action, OType
from typing import Dict

def predicates_simple()-> Dict[str,Predicate]:

    #Definition Predicates
    is_on=Predicate("is_on", o1type=1, o2type=2, predicate_ident=1)                                          # ego vehicle is on lane 
    is_on_lane=Predicate("is_on_lane", o1type=3, o2type=2, predicate_ident=2)                                # vehicle is on lane 
    has_right_neighbour=Predicate("has_right_neighbour", o1type=2, o2type=2, predicate_ident=3)              # lane has right neighbour  
    has_left_neighbour=Predicate("has_left_neighbour", o1type=2, o2type=2, predicate_ident=4)                # lane hast left neighbour
    has_successor=Predicate("has_successor", o1type=2, o2type=2, predicate_ident=5)                          # lane has successor lane
    has_predecessor=Predicate("has_predecessor", o1type=2, o2type=2, predicate_ident=6)                      # lane has predecessor lane
    has_top_right_neighbour=Predicate("has_top_right_neighbour",o1type=2, o2type=2, predicate_ident=7)       # lane has top right diagonal lane
    has_top_left_neighbour=Predicate("has_top_left_neighbour",o1type=2, o2type=2, predicate_ident=8)         # lane has top left diagonal lane
    has_bottom_right_neighbour=Predicate("has_bottom_right_neighbour",o1type=2, o2type=2, predicate_ident=9) # lane has bottom right diagonal lane
    has_bottom_left_neighbour=Predicate("has_bootom_left_neighbour",o1type=2, o2type=2, predicate_ident=10)   # lane has bottom left diagonal lane 

    predicate_dict={'is_on':is_on, 'is_on_lane':is_on_lane, 'has_right_neighbour':has_right_neighbour, 'has_left_neighbour':has_left_neighbour,\
                    'has_successor':has_successor, 'has_predecessor':has_predecessor, 'has_top_right_neighbour':has_top_right_neighbour,\
                    'has_top_left_neighbour':has_top_left_neighbour, 'has_bottom_right_neighbour':has_bottom_right_neighbour, 'has_bottom_left_neighbour':has_bottom_left_neighbour}
    return predicate_dict

def actions_simple(predicate_dict):
    
    is_on_lane = predicate_dict['is_on_lane']

    # SPARQL Query according: https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#QueryForms
    # prepared for rdflib in python: https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html
    lc_right_precondition = """
            PREFIX pre: <predicate:>
            SELECT ?x ?y ?v ?e
            WHERE {
                    ?e pre:is_on_lane ?x .
                    ?x pre:has_right_neighbour ?y .
                    FILTER NOT EXISTS { ?v pre:is_on ?y}
            }
            """

    lc_left_precondition = """
                PREFIX pre: <predicate:>
                SELECT ?y ?x ?v ?e
                WHERE {
                        ?e pre:is_on_lane ?x .
                        ?x pre:has_left_neighbour ?y .
                        FILTER NOT EXISTS { ?v pre:is_on ?y}
                }
            """

    l_keep_precondition = """
                PREFIX pre: <predicate:>
                SELECT ?y ?x ?v ?e
                WHERE {
                        ?e pre:is_on_lane ?x .
                        ?x pre:has_successor ?y .
                        FILTER NOT EXISTS { ?v pre:is_on ?y}
                }
            """
    
    # Definition of Actions
    lc_right=Action('LANE_CHANGE_RIGHT', lc_right_precondition, [{is_on_lane:["e","y"]}],[{is_on_lane:["e","x"]}],["e","y","x","v"])
    lc_left=Action('LANE_CHANGE_LEFT', lc_left_precondition, [{is_on_lane:["e","y"]}],[{is_on_lane:["e","x"]}],["e","y","x","v"])
    lc_keep=Action('LANE_KEEPING', l_keep_precondition, [{is_on_lane:["e","y"]}],[{is_on_lane:["e","x"]}],["e","y","x","v"])

    action_list = [lc_right, lc_left, lc_keep]

    return action_list

# def goal_scene_simple(predicate_dict):
#         is_on = predicate_dict['is_on']
#         goal_rel_is_on={is_on:[Agent, lane5]}
#         goal_scene={**goal_rel_is_on}