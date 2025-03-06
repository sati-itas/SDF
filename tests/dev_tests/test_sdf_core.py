import os
import sys
import timeit

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from core.rdf_wrapper import RDFWrapper
from data.otype import OType 

from tests.env_sets.gen_road_scenario import actions_light, scenario_5gen
from core.gen_data import DataGenerator


def test_sdf_actions():

    generator = DataGenerator('scene_otypes.ttl')
    predicate_dict = generator.gen_predicates('gen_pred_list2.txt')

    generator.rdf_wrapper.get_base_uri(generator._graph_datagen)
    base_uri = generator.rdf_wrapper.base_uri

    actions = actions_light(predicate_dict, base_uri)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)


    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.gen_rdf_graph(debug=False)

    # SPARQL proof
    for act in action_list:
        print(act.name)
        act.precondition
        pre = graph.query(act.precondition)
        for row in pre:
            print(row)

        # TEST check_precondition
        act.check_precondition(CurrentScene, debug=False)
        # precondition
        # TEST check_precondition
        new_scene_action_dict = act.execute_select_dict_list(CurrentScene, debug=False)
        print(f'\n CurrentScene: {CurrentScene}')
        if new_scene_action_dict:
            print(f'\n new_scene_action_dict: {[key for key in new_scene_action_dict.keys()][0]}')
        else: 
            print(f'\n new_scene_action_dict: {new_scene_action_dict}')

if __name__ == "__main__":
    test_sdf_actions()
