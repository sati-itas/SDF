import pytest
from pathlib import Path

from sdf.core.rdf_wrapper import RDFWrapper
from sdf.core.sdf_core import Action, Scene
from tests.env_sets.road_test_scenarios import scenario_30
from tests.env_sets.road_test_predicates_actions import actions_simple, predicates_simple, Predicate
from tests.env_sets.gen_road_scenario import scenario_5gen, actions_light
from rdflib import Graph, URIRef, Literal, Namespace, XSD, RDF
from sdf.core.rdf_wrapper import RDFUtils, SPARQLTemplate, RDFWrapper
from urllib.parse import quote

## test RDFWrapper functionality

### Test generating RDF graph from SD Scene
@pytest.fixture
def sample_scene():
    predicates = predicates_simple()
    actions = actions_simple(predicates)
    CurrentScene, GoalScene, action_list = scenario_30(predicates, actions)
    return CurrentScene, GoalScene, action_list


def test_gen_rdf_graph_from_sd_scene(sample_scene: tuple[Scene, Scene, list[Action]], tmp_path: Path):
    CurrentScene, GoalScene, action_list = sample_scene

    rdf_wrapper = RDFWrapper(CurrentScene)
    graph = rdf_wrapper.generate_graph()

    assert graph is not None
    assert len(graph) > 0

    # serialize directly to a tmp_path file (avoid wrapper path assumptions)
    out_file = tmp_path / "output_test_gen_rdf_graph.ttl"
    rdf_wrapper.data_graph.serialize(destination=str(out_file), format="turtle")
    assert out_file.exists()


    assert hasattr(rdf_wrapper, "gen_rdf_graph_processing_time")
    assert rdf_wrapper.gen_rdf_graph_processing_time >= 0

### Test RDFUtils functionality
@pytest.fixture(scope="module")
def test_number_to_literal_and_to_uri_behavior():
    # number_to_literal
    lit_int = RDFUtils.number_to_literal(7)
    assert isinstance(lit_int, Literal)
    assert str(lit_int.datatype).endswith("integer")

    lit_float = RDFUtils.number_to_literal(3.14)
    assert isinstance(lit_float, Literal)
    assert str(lit_float.datatype).endswith("float")

    with pytest.raises(TypeError):
        RDFUtils.number_to_literal("not-a-number")

    # to_uri valid and invalid
    valid = RDFUtils.to_uri("http://example.org/resource")
    assert isinstance(valid, URIRef)
    with pytest.raises(ValueError):
        RDFUtils.to_uri("ftp://invalid.example/resource")


def test_add_remove_copy_and_subset_isomorphism():
    g = Graph()
    ns = Namespace("http://example.org/test#")
    s = URIRef(ns["s"])
    p = URIRef(ns["p"])
    o = Literal("o")

    # add_triplets
    RDFUtils.add_triplets(g, [(s, p, o)])
    assert (s, p, o) in g

    # copy_graph and is_equal
    g_copy = RDFUtils.copy_graph(g)
    assert RDFUtils.is_equal(g, g_copy)
    assert g is not g_copy  # distinct objects

    # create superset graph
    g2 = Graph()
    RDFUtils.add_triplets(g2, [(s, p, o), (URIRef(ns["s2"]), p, Literal("o2"))])
    assert RDFUtils.is_subset(g, g2)
    assert RDFUtils.is_isomorphic_subset(g, g2)

    # remove_triplets
    RDFUtils.remove_triplets(g2, [(URIRef(ns["s2"]), p, Literal("o2"))])
    assert (URIRef(ns["s2"]), p, Literal("o2")) not in g2


def test_sparql_template_insert_and_delete_subject():
    g = Graph()

    subject = "http://example.org/ins#s"
    predicate = "http://example.org/ins#p"
    value = "val"
    # use RDFUtils.insert_subject to add a triple
    g = RDFUtils.insert_subject(g, subject, predicate, value)
    # ensure triple was added
    assert (URIRef(subject), URIRef(predicate), Literal(value)) in g

    # use RDFUtils.delete_subject to remove all triples for a subject
    g = RDFUtils.delete_subject(g, subject)
    # ensure no triples with that subject remain
    assert not any(True for _ in g.triples((URIRef(subject), None, None)))


def test_obj_uri_and_object_to_rdf_basics():
    class DummyType:
        def __init__(self, name):
            self.name = name

    class DummyObj:
        def __init__(self, name, id_, obj_type):
            self.name = name
            self.id = id_
            self.object_type = obj_type

    obj = DummyObj("car#1", 123, DummyType("Vehicle"))
    wrapper = RDFWrapper()  # no scene required for these helpers

    uri = wrapper.obj_uri(obj)
    assert str(uri).startswith(str(wrapper.DATA))

    triples = wrapper.object_to_rdf(obj, template=["id", "name", "object_type", "speed"])
    # Expect type triple, rdfs:label and id triple to be present in returned list
    type_triple = next((t for t in triples if t[1] == RDF.type), None)
    label_triple = next((t for t in triples if "label" in str(t[1]) or "label" in t[1].split()[-1]), None)
    id_triple = next((t for t in triples if t[1].split("#")[-1] == "id"), None)

    assert type_triple is not None
    assert label_triple is not None
    assert id_triple is not None


def test_prepare_sparql_query_returns_prepared():
    q = RDFUtils.prepare_sparql_query("SELECT ?s WHERE { ?s ?p ?o }", "http://example.org/base#")
    assert q is not None
    # PreparedQuery objects support algebra attribute; check presence to ensure correctness
    assert hasattr(q, "algebra")

#### Test loading RDF graph from file and helper methods
@pytest.fixture(scope="module")
def loaded_graph():
    base = 'http://example.org/Env'
    rdf_wrapper = RDFWrapper(base_uri=base)
    #graph = rdf_wrapper.load_rdf_graph('test_scene1.ttl', 'ttl')
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')
    return graph, rdf_wrapper

def test_load_rdf_graph_and_helpers():
    initial_base = 'http://example.org/Env'
    rdf_wrapper = RDFWrapper(base_uri=initial_base)

    # parse graph with rdflib
    graph = rdf_wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')

    # TODO test namespace bindings

    # exercise helper methods: they should run and return iterables or None
    class_type = 'DomainTypes'
    subclasses = rdf_wrapper.get_subclasses(graph, f'{rdf_wrapper.base_uri}#{class_type}')
    assert subclasses is None or hasattr(subclasses, '__iter__')

    properties = rdf_wrapper.get_properties(graph)
    assert properties is None or hasattr(properties, '__iter__')

    predicates = rdf_wrapper.get_predicates(graph)
    assert predicates is None or hasattr(predicates, '__iter__')

    attributes = rdf_wrapper.get_attributes(graph)
    assert attributes is None or hasattr(attributes, '__iter__')

def test_load_n_prepare_knowledge_graph(loaded_graph: tuple):
    graph, rdf_wrapper = loaded_graph

    assert graph is not None
    assert len(graph) > 0

    attributes, predicates = rdf_wrapper.get_attrs_and_pred_kg()
    assert rdf_wrapper.knowledge_graph is not None
    assert len(rdf_wrapper.knowledge_graph) > 0
    assert isinstance(attributes, set)
    assert isinstance(predicates, set)
    assert len(attributes) > 0
    assert len(predicates) > 0
    # Example expected attributes and predicates (may vary based on test data)
    expected_attributes = {"hasValueX", "hasValueY"}
    # expected_predicates = {"has_predecessor", "has_lane_assignment"}
    expected_predicates = {"has_left_neighbour", "has_right_neighbour"}
    assert expected_attributes.issubset(attributes)
    assert expected_predicates.issubset(predicates)

def test_sdgraph_generation_KN():
    rdf_wrapper = RDFWrapper()

    graph = rdf_wrapper.load_knowledge_graph('sdf/data/test_scene1.ttl')

    attr, preds = rdf_wrapper.get_attrs_and_pred_kg()
    preds = Predicate.gen_predicates(preds)  # convert to SD Predicates Dict
    acts = actions_light(preds)
    CurrentScene, GoalScene, action_list = scenario_5gen(preds, acts)

    rdf_wrapper.load_scene(CurrentScene)
    rdf_graph1 = rdf_wrapper.generate_data_graph(object_attributes=attr)

    sd_scene1 = rdf_wrapper.gen_sd_scene_from_rdf_database(rdf_graph1)
    assert sd_scene1 is not None
    assert GoalScene is not None
    assert isinstance(action_list, list)
    assert isinstance(sd_scene1, Scene)
    #assert len(preds) == len(sd_scene1.scene_relations)
    # Test sd_scene1 has same number of objects as CurrentScene
    assert len(sd_scene1.object_map) == len(CurrentScene.object_map)
    # Test that all predicates are prestent in the generated scene
    for pred in sd_scene1.scene_relations.keys():
        assert pred in preds.values()
