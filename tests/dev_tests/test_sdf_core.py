import os
import sys
import timeit
import pytest
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from sdf.core.rdf_wrapper import RDFWrapper
from sdf.core.sdf_core import Action, Scene
from sdf.data.otype import OType 

from tests.env_sets.road_test_predicates_actions import predicates_simple, actions_simple
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple
from tests.env_sets.road_test_scenarios import scenario_20, scenario_30
from sdf.core.rdf_wrapper import RDFUtils
import pytest
from sdf.core.sdf_core import SDObject, Predicate, Scene, SDUtils


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

### Test generating RDF graph from SD Scene
@pytest.fixture
def sample_scene():
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_30(predicates, actions)
    return CurrentScene, GoalScene, action_list, predicates

def test_sdf_init_rdf_wrapper(sample_scene: tuple[Scene, Scene, list[Action], dict]):
    # SHOULD TEST THE INITIALIZATION ONLY

    CurrentScene, GoalScene, action_list, predicates = sample_scene

    # Test default initialization
    rdf_wrapper = RDFWrapper()
    assert rdf_wrapper is not None
    assert rdf_wrapper.data_graph is not None
    assert len(rdf_wrapper.data_graph) == 0

def test_sdf_init_rdf_wrapper_C1(sample_scene: tuple[Scene, Scene, list[Action], dict]):

    CurrentScene, GoalScene, action_list, predicates = sample_scene

    test_data_dir = Path(__file__).resolve().parents[1] / "tests_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    # Case 1 no template, no predicates, no knowledge graph
    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.generate_graph()
    assert graph is not None
    assert len(graph) > 0
    assert hasattr(rdf_wrapper, "gen_rdf_graph_processing_time")
    assert rdf_wrapper.gen_rdf_graph_processing_time >= 0
    # serialize directly to a tmp_path file (avoid wrapper path assumptions)
    out_file = test_data_dir / "output_test_sdf_init_rdf_wrapper_case1.ttl"
    rdf_wrapper.data_graph.serialize(destination=str(out_file), format="turtle")
    assert out_file.exists()

def test_sdf_init_rdf_wrapper_C2(sample_scene: tuple[Scene, Scene, list[Action], dict]):

    CurrentScene, GoalScene, action_list, predicates = sample_scene

    test_data_dir = Path(__file__).resolve().parents[1] / "tests_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    # Case 2 with knowledge graph
    knowledge_graph_file_1 = 'sdf/data/situation_tbox_rdfs_v1.1.ttl'
    rdf_wrapper = RDFWrapper(CurrentScene)
    loaded_graph_1 = rdf_wrapper.load_knowledge_graph(knowledge_graph_file_1)
    attributes, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    rdf_wrapper.generate_data_graph(object_attributes=attributes)
    assert rdf_wrapper.data_graph is not None
    assert len(rdf_wrapper.data_graph) > 0
    # serialize directly to a tmp_path file (avoid wrapper path assumptions)
    out_file = test_data_dir / "output_test_sdf_init_rdf_wrapper_case2.ttl"
    rdf_wrapper.data_graph.serialize(destination=str(out_file), format="turtle")
    assert out_file.exists()


def test_sdf_init_rdf_wrapper_C3(sample_scene: tuple[Scene, Scene, list[Action], dict]):

    CurrentScene, GoalScene, action_list, predicates = sample_scene

    test_data_dir = Path(__file__).resolve().parents[1] / "tests_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)


    # Case 3 with template and predicates
    rdf_wrapper = RDFWrapper(CurrentScene)
    rdf_wrapper.generate_graph(object_template=SDOBJECT_TEMPLATE, predicates=predicates)
    assert rdf_wrapper.data_graph is not None
    assert len(rdf_wrapper.data_graph) > 0
    # serialize directly to a tmp_path file (avoid wrapper path assumptions)
    out_file = test_data_dir / "output_test_sdf_init_rdf_wrapper_case3.ttl"
    rdf_wrapper.data_graph.serialize(destination=str(out_file), format="turtle")
    assert out_file.exists()


def test_sdobject_eq_and_hash():
    a1 = SDObject("objA", "Type1")
    a2 = SDObject("objA", "Type2")
    b = SDObject("objB", "Type1")
    assert a1 == a2
    assert hash(a1) == hash(a2)
    assert a1 != b


def test_predicate_gen_predicates():
    names = {"on", "next_to"}
    preds = Predicate.gen_predicates(names)
    assert set(preds.keys()) == names
    for k, v in preds.items():
        assert isinstance(v, Predicate)
        assert v.name == k


def test_scene_init_validation_non_dict_relations_raises():
    obj_map = {}
    with pytest.raises(TypeError):
        Scene(obj_map, ["not", "a", "dict"])


def test_scene_init_validation_value_not_list_raises():
    a = SDObject("a", "T")
    obj_map = {"a": a}
    p = Predicate("rel")
    # value is a tuple, not a list -> TypeError
    bad_rel = {p: (a, a)}
    with pytest.raises(TypeError):
        Scene(obj_map, bad_rel)


def test_scene_init_validation_invalid_item_raises():
    a = SDObject("a", "T")
    obj_map = {"a": a}
    p = Predicate("rel")
    # list contains an invalid tuple (length != 2) -> ValueError
    bad_rel = {p: [(a,)]}
    with pytest.raises(ValueError):
        Scene(obj_map, bad_rel)


def test_get_relations_for_object_and_search_object_and_search_all_individuals_of_class():
    a = SDObject("A", "Car")
    b = SDObject("B", "Car")
    c = SDObject("C", "Tree")
    obj_map = {o.name: o for o in (a, b, c)}
    p1 = Predicate("near")
    p2 = Predicate("on")
    scene_relations = {
        p1: [[a, b], [b, c]],
        p2: [[c, a]],
    }
    scene = Scene(obj_map, scene_relations)

    rels_a = scene.get_relations_for_object("A")
    assert p1 in rels_a and [a, b] in rels_a[p1]
    assert p2 in rels_a and [c, a] in rels_a[p2]

    assert scene.search_object("B") is b
    assert scene.search_object("Z") is None

    cars = scene.search_all_individuals_of_class("Car")
    assert set(cars) == {a, b}


def test_sdutils_checks_and_canonical_signature():
    a = SDObject("A", "X")
    b = SDObject("B", "X")
    c = SDObject("C", "Y")
    p1 = Predicate("r1")
    p2 = Predicate("r2")

    rels1 = {p1: [[a, b], [b, c]], p2: [[c, a]]}
    rels2 = {p1: [[a, b], [b, c]], p2: [[c, a]]}
    rels3 = {p1: [[a, b]]}

    s1 = Scene({o.name: o for o in (a, b, c)}, rels1)
    s2 = Scene({o.name: o for o in (a, b, c)}, rels2)
    s3 = Scene({o.name: o for o in (a, b, c)}, rels3)

    assert SDUtils.check_identical_scenes(s1, s2) is True
    assert SDUtils.check_subset_pair(s3, s1) is True
    assert SDUtils.check_common_keys(s1, s3) == {p1}
    assert SDUtils.check_subset_pair(s3, s1) is True
    # canonical signature contains tuples (pred.name, subj.name, obj.name) sorted
    sig = SDUtils.canonical_scene_signature(s1)
    expected_facts = {
        (p1.name, "A", "B"),
        (p1.name, "B", "C"),
        (p2.name, "C", "A"),
    }
    assert set(sig) == expected_facts

def test_sdf_actions_rdfscene_assertions():
    # fails if self.KN is not set properly in RDFWrapper (without loading KN graph)
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_20(predicates, actions)

    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.generate_graph()

    rdf_wrapper = CurrentScene.init_rdf_wrapper()
    assert RDFUtils.is_equal(graph, rdf_wrapper.data_graph)
    CurrentScene_graph = rdf_wrapper.data_graph

    results = {}
    for act in action_list:
        act.init_action_with_rdf(rdf_wrapper)
        results[act.name] = act.check_precondition_on_rdf(CurrentScene_graph)

    expected = {
        "LANE_CHANGE_RIGHT": False,
        "LANE_CHANGE_LEFT": True,
        "LANE_KEEPING": True,
    }

    for name, exp in expected.items():
        assert name in results
        assert results[name] is exp
