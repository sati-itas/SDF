import os
import sys
import timeit

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from sdf.core.rdf_wrapper import RDFWrapper
from sdf.data.otype import OType 

from tests.env_sets.gen_road_scenario import actions_light, scenario_5gen
from tests.env_sets.road_test_predicates_actions import predicates_simple, actions_simple
from tests.env_sets.road_test_scenarios import scenario_20
from tests.env_sets.hanoi_predicates_actions import hanoi_predicates
from tests.env_sets.hanoi_sceanario import hanoi_classic
from sdf.core.gen_data import DataGenerator
from sdf.core.rdf_wrapper import RDFUtils


def test_sdf_actions_sdscene():

    generator = DataGenerator('test_scene.ttl')
    predicate_dict = generator.gen_predicates('gen_pred_list2.txt')

    generator.rdf_wrapper.get_base_uri(generator._graph_datagen)
    base_uri = generator.rdf_wrapper.base_uri

    actions = actions_light(predicate_dict, base_uri)
    CurrentScene, GoalScene, action_list = scenario_5gen(predicate_dict, actions)


    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.generate_graph()

    # SPARQL proof
    for act in action_list:
        act.init_action()
        print(act.name)
        act.precondition
        pre = graph.query(act.precondition)
        for row in pre:
            print(row)
        # TEST check_precondition
        scene_rdf_wrapper = CurrentScene.init_rdf_wrapper()
        act.check_precondition_on_rdf(scene_rdf_wrapper.data_graph, debug=False)
        # precondition
        # TEST check_precondition
        new_scene_action_dict = act.execute_action_on_sdscene(CurrentScene, debug=False)
        print(f'\n CurrentScene: {CurrentScene}')
        if new_scene_action_dict:
            print(f'\n new_scene_action_dict: {[key for key in new_scene_action_dict.keys()][0]}')
        else: 
            print(f'\n new_scene_action_dict: {new_scene_action_dict}')

def test_sdf_actions_rdf():


    # predicates = hanoi_predicates()
    # actions = actions_simple(predicates)
    # CurrentScene, GoalScene, action_list = hanoi_classic(predicates, actions)


    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)

    # Test the RDFWrapper Scene Initialization
    #initialize the RDFWrapper with the current scene
    rdf_wrapper = RDFWrapper(CurrentScene)
    start_time = timeit.default_timer()
    print(f'Generating RDF graph for CurrentScene: {CurrentScene.name}')
    graph = rdf_wrapper.generate_graph()
    generation_time = timeit.default_timer() - start_time
    print(f'RDF graph generation time: {generation_time:.6f} seconds')

    rdf_wrapper= CurrentScene.init_rdf_wrapper()
    print(f'graphs are equal: {RDFUtils.is_equal(graph, rdf_wrapper.data_graph)}')
    CurrentScene_graph = rdf_wrapper.data_graph

    # SPARQL proof
    for act in action_list:
        act.init_action_with_rdf(rdf_wrapper)

        # Test action query
        # Measure timing for raw query
        start_time = timeit.default_timer()
        pre = graph.query(act.precondition)
        raw_query_time = timeit.default_timer() - start_time
        print(f"Raw query time: {raw_query_time:.6f} seconds")
        for row in pre:
            print(row)
        # Measure timing for prepared query
        start_time = timeit.default_timer()
        pre = graph.query(act.prep_query)
        prepared_query_time = timeit.default_timer() - start_time
        print(f"Prepared query time: {prepared_query_time:.6f} seconds")
        for row in pre:
            print(row)

        # TEST check_precondition
        print(f'{act.name}.check_precondition_improve() => {act.check_precondition_on_rdf(CurrentScene_graph, debug=False)}\n')

        # TEST execute_select_dict_list_improve
        print(f'{act.name}.execute_select_dict_list_improve() => {act.execute_action_on_rdf(CurrentScene_graph, debug=False)}\n')
if __name__ == "__main__":
    test_sdf_actions_sdscene()
    test_sdf_actions_rdf()
