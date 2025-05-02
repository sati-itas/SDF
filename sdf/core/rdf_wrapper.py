from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Dict
from typing import List

from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef
from rdflib.compare import to_isomorphic
from rdflib.plugins.sparql import prepareQuery

from sdf.core.utility.dict_helper import merge_dicts
from sdf.core.utility.timing_utils import time_tracker
from sdf.core.utility.timing_utils import time_tracker_static


if TYPE_CHECKING:
    from sdf.core.sdf_core import Scene


class RDFWrapper:
    """Wrapper for mapping SD structure to rdf (and vice versa)

    Args:
        object_types (OType class): class holding all enums for object types
        scene (Scene):  scene, whos representation in SD shell by transferred to rdf
    """

    def __init__(self, scene: Scene | None = None, base_uri: str = ''):
        if scene is not None:
            self.object_types = None
            self.scene = scene
            self.scene_objects = scene.object_map
            self.scene_relation_dict = scene.scene_relations
        # else:
        #     print('WARNING: no scene passed to the constructor')

        self.graph = Graph()
        self.list_of_triplets = []
        self.rdf_triplet_list = []
        self.namespace_list = []

        self.object_mapping_dict = {}
        self.subject_mapping_dict = {}
        self.predicate_mapping_dict = {}
        self.sd_rdf_dict = {}

        self.base_uri = base_uri
        self.ex_base_uri = 'http://example.org/'
        if not self.base_uri:
            self.base_uri = self.ex_base_uri

    def set_base_uri(self, uri: str):
        self.base_uri = uri
        return self.base_uri

    def to_uri(self, value: str) -> URIRef:
        """Converts a string to an URIRef using RDFUtils."""
        return RDFUtils.to_uri(value)

    def load_rdf_graph(self, data_graph: str, format_: str):
        """loads RDF graph from file"""
        # https://rdflib.readthedocs.io/en/stable/plugin_parsers.html
        # https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph.parse
        loaded_graph = self.graph.parse(f'sdf/data/{data_graph}', format=format_)
        return loaded_graph

    def get_base_uri(self, loaded_graph: Graph):
        """get base uri from loaded graph"""
        if any(loaded_graph.subjects(RDF.type, OWL.Ontology)):
            for s in loaded_graph.subjects(RDF.type, OWL.Ontology):
                self.base_uri = str(s)
                break
        else:
            print(f'\n no base uri found; wrapper base uri set to {self.base_uri}\n')
            # self.base_uri = next(iter(loaded_graph.namespaces()))[1]

    def get_subclasses(self, loaded_graph: Graph, class_uri: str):
        """get all subclasses of a given class_uri using RDFUtils"""
        return RDFUtils.get_subclasses(loaded_graph, class_uri)

    def get_predicates(self, loaded_graph: Graph):
        """get all predicates/properties from graph if they are marked with OWL.ObjectProperty"""
        return RDFUtils.get_predicates(self, loaded_graph)

    def gen_namespace(self, debug=False) -> List:
        """generates unique Namespace instances from object and predicate lists

        Args:
            object_types (OType class): ENUM of objects
            objects (list): list of unique objects

        Returns:
            list of rdflib.namespace.Namespace objects: list of unique Namespace objects for rdf
        """
        for item in self.scene_objects.values():
            ns_uri = f'{self.base_uri}{item.object_type}#'  # "http://example.org/{object_type}/"
            ns = Namespace(ns_uri)
            self.graph.bind(f'{item.object_type}', ns)
            if ns not in self.namespace_list:
                self.namespace_list.append(ns)

        # generate predicate namespace
        ns_pred_uri = f'{self.base_uri}predicate#'  # "http://example.org/predicate/"
        self.PRED = Namespace(ns_pred_uri)
        self.graph.bind('pred', self.PRED)
        self.namespace_list.append(self.PRED)

        if debug:
            print(
                f'\nRDFWrapper.gen_namespace() - generate all rdf namespaces: {self.namespace_list}\n'
            )
            for item in self.namespace_list:
                print(f'\tType Namespace {item}: {type(item)}\n')
        return self.namespace_list

    def gen_rdf_database(self, debug=False) -> Dict:
        """generates a dict which maps any SD object to a generated rdf object; within all relations of a sdf scene.

        Args:
            debug (bool, optional)): debugmode. Dafault is False
        Returns (Dict):
            self.sd_rdf_dict {key=any SD object: value=any rdf object}
        """

        # iterate over all relations in current scene
        for key, sd_value in self.scene_relation_dict.items():
            # "scene_relation_dict" data structure: {key=sd_predicate: value=[nested List of sd_object instances]}
            sd_predicate = key

            # map sd_predicates to rdf predicate namespace
            for namespace in self.namespace_list:
                if namespace == self.PRED:
                    self.predicate_mapping_dict = {
                        sd_predicate: namespace[sd_predicate.name]
                    }
                    # append all mappings of rdf instances with Namespace self.PRED
                    # to SD Predicate instances to "sd_rdf_dict" mapping dict
                    self.sd_rdf_dict = {
                        **self.sd_rdf_dict,
                        **self.predicate_mapping_dict,
                    }

            # iterate over all values (sd_objects) in "scene_relation_dict"
            for objects in sd_value:
                if debug:
                    print(f'wrapper.gen_rdf_database() - \t {objects}')
                if not isinstance(objects, list):
                    # if value is no nested list
                    sd_subject = sd_value[0]
                    sd_object = sd_value[1]

                    for namespace_item in self.namespace_list:
                        # iterate over namespaces
                        # if namespace name and object type is identical generate rdf item
                        if (
                            str(namespace_item)
                            == f'{self.base_uri}{sd_subject.object_type}#'
                        ):
                            self.subject_mapping_dict = {
                                sd_subject: namespace_item[sd_subject.name]
                            }  # generate rdf item
                            self.sd_rdf_dict = {
                                **self.sd_rdf_dict,
                                **self.subject_mapping_dict,
                            }

                        if (
                            str(namespace_item)
                            == f'{self.base_uri}{sd_object.object_type}#'
                        ):
                            self.object_mapping_dict = {
                                sd_object: namespace_item[sd_object.name]
                            }
                            self.sd_rdf_dict = {
                                **self.sd_rdf_dict,
                                **self.object_mapping_dict,
                            }

                        if str(namespace_item) == self.PRED:
                            self.predicate_mapping_dict = {
                                sd_predicate: namespace_item[sd_predicate.name]
                            }
                            self.sd_rdf_dict = {
                                **self.sd_rdf_dict,
                                **self.predicate_mapping_dict,
                            }

                else:  # else: value is nested list; iterate over all nested lists
                    # if value is nested list
                    for _item in objects:
                        # same as above but one hierarchy level further down
                        # (instead of sd_value[0] and sd_value[1]: sd_value[...][0] and sd_value[...][1])
                        if not isinstance(_item, list):
                            sd_subject = objects[0]
                            sd_object = objects[1]

                            for namespace_item in self.namespace_list:
                                if (
                                    str(namespace_item)
                                    == f'{self.base_uri}{sd_subject.object_type}#'
                                ):
                                    self.subject_mapping_dict = {
                                        sd_subject: namespace_item[sd_subject.name]
                                    }
                                    self.sd_rdf_dict = {
                                        **self.sd_rdf_dict,
                                        **self.subject_mapping_dict,
                                    }

                                if (
                                    str(namespace_item)
                                    == f'{self.base_uri}{sd_object.object_type}#'
                                ):
                                    self.object_mapping_dict = {
                                        sd_object: namespace_item[sd_object.name]
                                    }
                                    self.sd_rdf_dict = {
                                        **self.sd_rdf_dict,
                                        **self.object_mapping_dict,
                                    }

                                if str(namespace_item) == self.PRED:
                                    self.predicate_mapping_dict = {
                                        sd_predicate: namespace_item[sd_predicate.name]
                                    }
                                    self.sd_rdf_dict = {
                                        **self.sd_rdf_dict,
                                        **self.predicate_mapping_dict,
                                    }

        if debug:
            print(
                'wrapper.gen_rdf_database() -> self.sd_rdf_dict {key=any SD object: value=any rdf object }\n'
            )
            for key, value in self.sd_rdf_dict.items():
                print(f'\tkey (sd object): {key} \n \tvalue (rdf object): {value}\n \n')

        return self.sd_rdf_dict

    def rdf_triplets(self, debug=False) -> List:
        """Generating rdf triplets from scene (self.scene_relation_dict),
        namespaces (self.namespace_list) and database (self.sd_rdf_dict)

        Args:
            debug (bool, optional): debugmode. Dafault is False

        Returns:
            List:  List of Tuples: List of rdf triplets
        """

        # iterate over all SD relations in current scene
        for sd_key, sd_value in self.scene_relation_dict.items():
            sd_predicate = sd_key

            for objects in sd_value:
                if debug:
                    print(f'wrapper.rdf_triplets() - \t {objects}')

                if not isinstance(objects, list):
                    # if objects is no nested list
                    sd_subject = sd_value[0]
                    sd_object = sd_value[1]

                    # take value entries and find equivilants in "sd_rdf_dict"
                    for rdf_key in self.sd_rdf_dict.keys():
                        if rdf_key == sd_predicate:
                            rdf_predicate = self.sd_rdf_dict[sd_predicate]
                        if rdf_key == sd_subject:
                            rdf_subject = self.sd_rdf_dict[sd_subject]
                        if rdf_key == sd_subject:
                            rdf_object = self.sd_rdf_dict[sd_object]

                    triple = (rdf_subject, rdf_predicate, rdf_object)

                    # if triple is not already in "list_of_triplets": append it
                    if triple not in self.list_of_triplets:
                        self.list_of_triplets.append(triple)
                    break

                else:
                    # if value is nested list
                    for _item in objects:
                        # same as above but one hierarchy level further down
                        # (instead of sd_value[0] and sd_value[1]: sd_value[...][0] and sd_value[...][1])
                        if not isinstance(_item, list):
                            sd_subject = objects[0]
                            sd_object = objects[1]
                            # take value entries and find equivilants in "sd_rdf_dict"
                            for rdf_key in self.sd_rdf_dict.keys():
                                if rdf_key == sd_predicate:
                                    rdf_predicate = self.sd_rdf_dict[sd_predicate]
                                if rdf_key == sd_subject:
                                    rdf_subject = self.sd_rdf_dict[sd_subject]
                                if rdf_key == sd_subject:
                                    rdf_object = self.sd_rdf_dict[sd_object]
                            triple = (rdf_subject, rdf_predicate, rdf_object)
                            if triple not in self.list_of_triplets:
                                self.list_of_triplets.append(triple)
                            break
        if debug:
            print('\nRDFWrapper.RDFTriplets - generate RDF-triplets from SD_Scene:')
            for item in self.list_of_triplets:
                print(f'\t{item}\n')
            print('\t\tTypes of triplet entries (given example: first triplet):')
            for triplet_item in self.list_of_triplets[0]:
                print(f'\t\t\t{triplet_item}: {type(triplet_item)}\n')
        return self.list_of_triplets

    @time_tracker('gen_rdf_graph_processing_time')
    def gen_rdf_graph(self, warmup=False, debug=False):
        """builds up RDF graph from RDF triplets

        Args:
            triplets (list of tuples): RDF triplets (subject, predicate, object)

        Returns:
            rdflib.graph.Graph : RDF graph
        """
        self.gen_namespace(debug=debug)
        self.gen_rdf_database(debug=debug)
        self.rdf_triplets(debug=debug)
        # iterate over all triplets and add them to the graph
        for item in self.list_of_triplets:
            self.graph.add(item)

        # warmup graph (load graph in memory)
        if warmup:
            self.graph.query(("ASK { ?s ?p ?o }"))
        return self.graph

    def triplet_from_relation(self, relation):
        """generates RDF triplet from single SD relation

        Args:
            relation (Dict): Relation based on SD Objects and Predicates

        Returns:
            Tuple: RDF triplet (RDF subject, RDF predicate, RDF object)
        """
        for sd_rel_key, sd_rel_value in relation.items():
            for mapping_key, mapping_value in self.sd_rdf_dict.items():
                if sd_rel_key == mapping_key:
                    pre = mapping_value
                if sd_rel_value[0] == mapping_key:
                    sub = mapping_value
                if sd_rel_value[1] == mapping_key:
                    obj = mapping_value

            triplet = (sub, pre, obj)
            return triplet

    def gen_sd_scene_from_rdf_database(self, new_graph) -> Scene:
        """generates new SD scene from manipulated RDF Database.
        The action manipulates the RDF Database but not SD scene itself in the first place.
        The new SD scene after the execution of the action has to be generated based on the manipulated RDF Database.
        Args:
            new_graph (rdflib.graph.Graph): new RDF Database after the execution of the action

        Returns:
            Scene: new SD Scene
        """

        new_sd_relations = {}
        for triplet in new_graph:
            # print(f"triplet: {triplet}")
            for key, value in self.sd_rdf_dict.items():
                if triplet[0] == value:
                    new_sub = key
                if triplet[1] == value:
                    new_pred = key
                if triplet[2] == value:
                    new_obj = key
            try:
                new_sd_relations = merge_dicts(
                    new_sd_relations, {new_pred: [[new_sub, new_obj]]}
                )
            except Exception as e:
                print(f'{e}:Error while creating new SD scene relations')

        from sdf.core.sdf_core import Scene

        new_scene = Scene(
            object_map=self.scene.object_map, scene_relations=new_sd_relations
        )
        return new_scene

    def serialize_rdf_graph(self, graph_name: str):
        """serialize to turtle per default"""
        with open(f'sdf/data/{graph_name}.ttl', 'wb') as f:
            self.graph.serialize(f, format='turtle')

    def prepare_sparql_query(self, query: str):
        """Prepares the SPARQL query for the RDF graph using RDFUtils."""
        return RDFUtils.prepare_sparql_query(query, self.base_uri)

    @time_tracker('query_rdf_graph_processing_time')
    def query_rdf_graph(self, graph: Graph, query: str = None, prepared_query=None):
        """
        Queries the RDF graph using a SPARQL query or a prepared query.

        Args:
            graph (Graph): The RDF graph to query.
            query (str, optional): SPARQL query string. Defaults to None.
            prepared_query (PreparedQuery, optional): Precompiled SPARQL query. Defaults to None.

        Returns:
            Result: Query result or None if an error occurs.
        """
        return RDFUtils.query_rdf_graph(graph, query=query, prepared_query=prepared_query)

    def copy_rdf_graph(self, g: Graph) -> Graph:
        """Creates a copy of the given RDF graph from the given graph.
        Args:
            graph (Graph): The RDF graph to copy.
        Returns:
            Graph: A new RDF graph that is a copy of the original.
        """
        return RDFUtils.copy_graph(g)

    def map_rdf_object_to_sd_object(self, rdf_obj):
        """maps given RDF object from database to SD object from given scene

        Args:
            rdf_obj (RDF URI): RDF entity from Namespace

        Returns:
            Object: object instance equivilant of given RDF object
        """
        for key, value in self.scene_relation_dict.items():
            if value == rdf_obj:
                return key

    def remove_triplets_from_rdf_database(self, d_list):
        """removes triplets from the current RDF graph wrapper instance
        Args:
            d_list (list): list of triplets to be removed
        Returns:
            rdflib.graph.Graph: updated RDF self.graph
        """
        self.graph = RDFUtils.remove_triplets(self.graph, d_list)
        return self.graph

    def add_triplets_to_rdf_database(self, a_list):
        """adds triplets to the current RDF graph wrapper instance
        Args:
            a_list (list): list of triplets to be added
        Returns:
            rdflib.graph.Graph: updated RDF self.graph
        """
        self.graph = RDFUtils.add_triplets(self.graph, a_list)
        return self.graph

    def remove_triplets(self, _graph: Graph, d_list):
        """removes triplets from RDF graph using RDFUtils"""
        return RDFUtils.remove_triplets(_graph, d_list)

    def add_triplets(self, _graph: Graph, a_list):
        """adds triplets to the RDF graph using RDFUtils"""
        return RDFUtils.add_triplets(_graph, a_list)


class RDFUtils:
    """Utility class for RDF operations"""

    @staticmethod
    def get_predicates(self, loaded_graph: Graph):
        """get all predicates/properties from graph if they marked with OWL.ObjectProperty"""
        predicates = set()
        for pred in loaded_graph.subjects(RDF.type, OWL.ObjectProperty):
            predicates.add(pred.split('#')[-1])
            # print("object-property:", pred.split("#")[-1])
        if predicates:
            return predicates
        else:
            return None

    @staticmethod
    def get_subclasses(loaded_graph: Graph, class_uri: str) -> Dict:
        """
        Get all subclasses of a given class URI.

        Args:
            loaded_graph (Graph): The RDF graph to query.
            class_uri (str): The URI of the class to find subclasses for.

        Returns:
            Dict: A dictionary of subclasses and their deeper subclasses.
        """
        subclasses = {}
        gen_graph_subjects = loaded_graph.subjects(RDFS.subClassOf, URIRef(class_uri))
        for subclass in gen_graph_subjects:
            subclass_name = subclass.split('#')[-1]
            deeper_subclasses = RDFUtils.get_subclasses(loaded_graph, URIRef(subclass))
            if deeper_subclasses:
                subclasses[subclass_name] = deeper_subclasses
            else:
                subclasses[subclass_name] = None
        return subclasses

    @staticmethod
    def to_uri(value: str) -> URIRef:
        """
        Converts a string to an URIRef.

        Args:
            value (str): The string to be converted.

        Returns:
            URIRef: The converted URIRef object.
        """
        if not value.startswith("http://") and not value.startswith("https://"):
            raise ValueError(f"Invalid URI: {value}. Must start with 'http://' or 'https://'.")
        return URIRef(value)

    @staticmethod
    def remove_triplets(_graph: Graph, d_list):
        """removes triplets from _graph

        Args:
            d_list (_type_): _description_

        Returns:
            rdflib.graph.Graph: _graph
        """
        for triplet in d_list:
            _graph.remove(triplet)
        return _graph

    @staticmethod
    def add_triplets(_graph: Graph, a_list):
        """adds triplets to the RDF graph

        Args:
            a_list (_type_): _description_


        Returns:
            rdflib.graph.Graph: new RDF graph
        """

        for _tuple in a_list:
            _graph.add(_tuple)
        return _graph

    @staticmethod
    def is_isomorphic_equal(g: Graph, other_graph: Graph):
        """Compares two RDF graphs for isomorphism. Essentially checks if they are structurally identical.
        This is a more general comparison than checking for equality, as it does not require the graphs to be identical in terms of URIs or literals.
        Note that this method is relvent in case of BNodes, where the same node can be represented by different URIs in different graphs.
        It uses the rdflib.compare.to_isomorphic function to perform the comparison.
        Args:
            other_graph (Graph): The other RDF graph to compare with.
        Returns:
            bool: True if the graphs are isomorphic, False otherwise.
        """
        return to_isomorphic(g) == to_isomorphic(other_graph)

    @staticmethod
    def is_isomorphic_subset(g: Graph, other_graph: Graph):
        """Compares two RDF graphs for isomorphism. Essentially checks if they are structurally identical.
        This is a more general comparison than checking for equality, as it does not require the graphs to be identical in terms of URIs or literals.
        Note that this method is relvent in case of BNodes, where the same node can be represented by different URIs in different graphs.
        It uses the rdflib.compare.to_isomorphic function to perform the comparison.
        Args:
            other_graph (Graph): The other RDF graph to compare with.
        Returns:
            bool: True if the graphs are isomorphic, False otherwise.
        """
        iso1 = to_isomorphic(g)
        iso2 = to_isomorphic(other_graph)

        triples1 = set(iso1.triples((None, None, None)))
        triples2 = set(iso2.triples((None, None, None)))

        return triples1.issubset(triples2)

    @staticmethod
    def is_equal(g: Graph, other_graph: Graph):
        """Compares two RDF graphs for equality. This means that they must be identical in terms of URIs and literals.
        This is a stricter comparison than is_isomorphic, as it requires the graphs to be identical in terms of URIs and literals.
        Note that this method dosn't consider BNodes, where the same node can be represented by different URIs in different graphs.
        Args:
            other_graph (Graph): The other RDF graph to compare with.
        Returns:
            bool: True if the graphs are isomorphic, False otherwise.
        """
        return set(g) == set(other_graph)

    @staticmethod
    def is_subset(g: Graph, other_graph: Graph):
        """Compares two RDF graphs to check if one is a subset of the other.
        This means that all triples in the first graph must also be present in the second graph.
        Args:
            other_graph (Graph): The other RDF graph to compare with.
        Returns:
            bool: True if the first graph is a subset of the second, False otherwise.
        """
        return set(g).issubset(set(other_graph))

    @staticmethod
    def delete_subject(graph: Graph, subject: str):
        """Deletes a subject from the RDF graph. with SPARQL DELETE query.
        Args:
            graph (Graph): The RDF graph to delete the subject from.
            subject (str): The subject to be deleted.
        Returns:
            Graph: The updated RDF graph.
        """
        delete_template = SPARQLTemplate(
            """
            DELETE WHERE {
                <{subject}> ?p ?o .
                }
            """)

        delete_template.execute(graph=graph, subject=subject)
        return graph

    @staticmethod
    def insert_subject(graph: Graph, subject: str):
        """Inserts a new subject into the RDF graph. with SPARQL INSERT query.
        Args:
            graph (Graph): The RDF graph to insert the subject into.
            subject (str): The subject to be inserted.
        Returns:
            Graph: The updated RDF graph.
        """
        insert_template = SPARQLTemplate(
            """
                INSERT DATA {
                    <{subject}> <{predicate}> "{value}" .
                }
            """)

        insert_template.execute(graph=graph, subject=subject)
        return graph

    @staticmethod
    def copy_graph(g: Graph) -> Graph:
        """Creates a copy of the given RDF graph.

        Args:
            g (Graph): The RDF graph to copy.

        Returns:
            Graph: A new RDF graph that is a copy of the original.
        """
        graph_copy = Graph()
        for item in g:
            graph_copy.add(item)
        return graph_copy

    #@time_tracker_static('query_rdf_graph_processing_time')
    @staticmethod
    def query_rdf_graph(graph: Graph, query: str = None, prepared_query=None):
        """
        Queries the RDF graph using a SPARQL query or a prepared query.

        Args:
            graph (Graph): The RDF graph to query.
            query (str, optional): SPARQL query string. Defaults to None.
            prepared_query (PreparedQuery, optional): Precompiled SPARQL query. Defaults to None.

        Returns:
            Result: Query result or None if an error occurs.
        """
        try:
            if prepared_query:
                return graph.query(prepared_query)
            elif query:
                return graph.query(query)
            else:
                raise ValueError("Either 'query' or 'prepared_query' must be provided.")
        except Exception as e:
            print(f"Error while querying RDF graph: {e}")
            return None

    @staticmethod
    def prepare_sparql_query(query: str, base_uri: str) -> str:
        """
        Prepares the SPARQL query for the RDF graph.
        Compiles the SPARQL query once and saves it as bytecode.

        Args:
            query (str): SPARQL query.
            base_uri (str): Base URI to initialize the namespace.

        Returns:
            str: Prepared query.
        """
        q = prepareQuery(
            query,
            initNs={
                'owl': OWL,
                'rdf': RDF,
                'rdfs': RDFS,
                'ex': Namespace(base_uri),
            },
        )
        return q


class SPARQLTemplate:
    def __init__(self, template_str):
        self.template = template_str

    def render(self, **kwargs):
        return self.template.format(**kwargs)

    def execute(self, graph, **kwargs):
        query = self.render(**kwargs)
        return graph.update(query)
