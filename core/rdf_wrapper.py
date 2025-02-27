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

from core.utility.dict_helper import merge_dicts
from core.utility.timing_utils import time_tracker


if TYPE_CHECKING:
    from core.sdf_core import Scene


class RDFWrapper:
    '''Wrapper for mapping SD structure to rdf (and vice versa)

    Args:
        object_types (OType class): class holding all enums for object types
        scene (Scene):  scene, whos representation in SD shell by transferred to rdf
    '''

    def __init__(self, scene: Scene | None = None, base_uri: str = ""):

        if scene is not None:
            self.object_types = None
            self.scene = scene
            self.scene_objects = scene.object_list
            self.scene_relation_dict = scene.scene_relations
        else:
            print('WARNING: no scene passed to the constructor')

        self.graph = Graph()
        self.list_of_triplets = []
        self.rdf_triplet_list = []
        self.namespace_list = []

        self.object_mapping_dict = {}
        self.subject_mapping_dict = {}
        self.predicate_mapping_dict = {}
        self.sd_rdf_dict = {}

        self.base_uri = base_uri
        self.ex_base_uri = "http://example.org/"
        if not self.base_uri:
            self.base_uri = self.ex_base_uri

    def set_base_uri(self, uri: str):
        self.base_uri = uri
        return self.base_uri

    def load_rdf_graph(self, data_graph: str, format_: str):
        # https://rdflib.readthedocs.io/en/stable/plugin_parsers.html
        # https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph.parse
        loaded_graph = self.graph.parse(f"data/{data_graph}", format=format_)
        return loaded_graph

    def get_base_uri(self, loaded_graph: Graph):
        if any(loaded_graph.subjects(RDF.type, OWL.Ontology)):
            for s in loaded_graph.subjects(RDF.type, OWL.Ontology):
                self.base_uri = str(s)
                break
        else:
            print(f'\n no base uri found; wrapper base uri set to {self.base_uri}\n')
            # self.base_uri = next(iter(loaded_graph.namespaces()))[1]

    def get_subclasses(self, loaded_graph: Graph, class_uri: str):
        """ get all subclasses of a given class_uri
        """
        # TODO if '#' or '/' or '*' distinguish split of class_uri
        subclasses = {}
        gen_graph_subjects = loaded_graph.subjects(RDFS.subClassOf, URIRef(class_uri))
        for subclass in gen_graph_subjects:
            subclass_name = subclass.split("#")[-1]
            deeper_subclasses = self.get_subclasses(loaded_graph, URIRef(subclass))
            if deeper_subclasses:
                subclasses[subclass_name] = deeper_subclasses
            else:
                subclasses[subclass_name] = None
        return subclasses

    def get_predicates(self, loaded_graph: Graph):
        """ get all predicates/properties from graph if they marked with OWL.ObjectProperty
        """
        predicates = set()
        for pred in loaded_graph.subjects(RDF.type, OWL.ObjectProperty):
            predicates.add(pred.split("#")[-1])
            # print("object-property:", pred.split("#")[-1])
        if predicates:
            return predicates
        else:
            return None

    def gen_namespace(self, debug=False) -> List:
        '''generates unique Namespace instances from object and predicate lists

        Args:
            object_types (OType class): ENUM of objects
            objects (list): list of unique objects

        Returns:
            list of rdflib.namespace.Namespace objects: list of unique Namespace objects for rdf
        '''
        for item in self.scene_objects:
            ns_uri = f"{self.base_uri}{item.object_type}#"  # "http://example.org/{object_type}/"
            ns = Namespace(ns_uri)
            self.graph.bind(f'{item.object_type}', ns)
            if ns not in self.namespace_list:
                self.namespace_list.append(ns)

        # generate predicate namespace
        ns_pred_uri = f'{self.base_uri}predicate#'  # "http://example.org/predicate/"
        self.PRED = Namespace(ns_pred_uri)
        self.graph.bind("pred", self.PRED)
        self.namespace_list.append(self.PRED)

        if debug:
            print(f"\nRDFWrapper.gen_namespace() - generate all rdf namespaces: {self.namespace_list}\n")
            for item in self.namespace_list:
                print(f"\tType Namespace {item}: {type(item)}\n")
        return self.namespace_list

    def gen_rdf_database(self, debug=False) -> Dict:
        '''generates a dict which maps any SD object to a generated rdf object; within all relations of a sdf scene.

        Args:
            debug (bool, optional)): debugmode. Dafault is False
        Returns (Dict):
            self.sd_rdf_dict {key=any SD object: value=any rdf object}
        '''

        # iterate over all relations in current scene
        for key, sd_value in self.scene_relation_dict.items():
            # "scene_relation_dict" data structure: {key=sd_predicate: value=[nested List of sd_object instances]}
            sd_predicate = key

            # map sd_predicates to rdf predicate namespace
            for namespace in self.namespace_list:
                if namespace == self.PRED:
                    self.predicate_mapping_dict = {sd_predicate: namespace[sd_predicate.name]}  # TODO ersetze mit namespace.[sd_predicate.name]
                    # append all mappings of rdf instances with Namespace self.PRED
                    # to SD Predicate instances to "sd_rdf_dict" mapping dict
                    self.sd_rdf_dict = {**self.sd_rdf_dict, **self.predicate_mapping_dict}

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
                        if str(namespace_item) == f'{self.base_uri}{sd_subject.object_type}#':
                            self.subject_mapping_dict = {
                                sd_subject: namespace_item[sd_subject.name]
                            }  # generate rdf item
                            self.sd_rdf_dict = {**self.sd_rdf_dict, **self.subject_mapping_dict}

                        if str(namespace_item) == f'{self.base_uri}{sd_object.object_type}#':
                            self.object_mapping_dict = {sd_object: namespace_item[sd_object.name]}
                            self.sd_rdf_dict = {**self.sd_rdf_dict, **self.object_mapping_dict}

                        if str(namespace_item) == self.PRED:
                            self.predicate_mapping_dict = {sd_predicate: namespace_item[sd_predicate.name]}
                            self.sd_rdf_dict = {**self.sd_rdf_dict, **self.predicate_mapping_dict}

                else:  # else: value is nested list; iterate over all nested lists
                    # if value is nested list
                    for _item in objects:
                        # same as above but one hierarchy level further down
                        # (instead of sd_value[0] and sd_value[1]: sd_value[...][0] and sd_value[...][1])
                        if not isinstance(_item, list):

                            sd_subject = objects[0]
                            sd_object = objects[1]

                            for namespace_item in self.namespace_list:
                                if str(namespace_item) == f'{self.base_uri}{sd_subject.object_type}#':
                                    self.subject_mapping_dict = {sd_subject: namespace_item[sd_subject.name]}
                                    self.sd_rdf_dict = {**self.sd_rdf_dict, **self.subject_mapping_dict}

                                if str(namespace_item) == f'{self.base_uri}{sd_object.object_type}#':
                                    self.object_mapping_dict = {sd_object: namespace_item[sd_object.name]}
                                    self.sd_rdf_dict = {**self.sd_rdf_dict, **self.object_mapping_dict}

                                if str(namespace_item) == self.PRED:
                                    self.predicate_mapping_dict = {sd_predicate: namespace_item[sd_predicate.name]}
                                    self.sd_rdf_dict = {**self.sd_rdf_dict, **self.predicate_mapping_dict}

        if debug:
            print("wrapper.gen_rdf_database() -> self.sd_rdf_dict {key=any SD object: value=any rdf object }\n")
            for key, value in self.sd_rdf_dict.items():
                print(f"\tkey (sd object): {key} \n \tvalue (rdf object): {value}\n \n")

        return self.sd_rdf_dict

    def rdf_triplets(self, debug=False) -> List:
        '''Generating rdf triplets from scene (self.scene_relation_dict),
        namespaces (self.namespace_list) and database (self.sd_rdf_dict)

        Args:
            debug (bool, optional): debugmode. Dafault is False

        Returns:
            List:  List of Tuples: List of rdf triplets
        '''

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
            print("\nRDFWrapper.RDFTriplets - generate RDF-triplets from SD_Scene:")
            for item in self.list_of_triplets:
                print(f"\t{item}\n")
            print("\t\tTypes of triplet entries (given example: first triplet):")
            for triplet_item in self.list_of_triplets[0]:
                print(f"\t\t\t{triplet_item}: {type(triplet_item)}\n")
        return self.list_of_triplets

    @time_tracker("gen_rdf_graph_processing_time")
    def gen_rdf_graph(self, debug=False):
        '''builds up RDF graph from RDF triplets

        Args:
            triplets (list of tuples): RDF triplets (subject, predicate, object)

        Returns:
            rdflib.graph.Graph : RDF ontology
        '''
        self.gen_namespace(debug=debug)
        self.gen_rdf_database(debug=debug)
        self.rdf_triplets(debug=debug)

        for item in self.list_of_triplets:
            self.graph.add(item)
        return self.graph

    def serialize_rdf_graph(self, graph_name: str):
        """serialize to turtle per default"""
        with open(f"data/{graph_name}.ttl", "wb") as f:
            self.graph.serialize(f, format="turtle")

    @time_tracker("query_rdf_graph_processing_time")
    def query_rdf_graph(self, graph: Graph, preconditions: str):
        result = graph.query(preconditions)
        return result

    def copy_rdf_graph(self) -> Graph:
        graph_copy = Graph()
        for item in self.list_of_triplets:
            graph_copy.add(item)
        return graph_copy

    def map_rdf_object_to_sd_object(self, rdf_obj):
        '''maps given RDF object from database to SD object from given scene

        Args:
            rdf_obj (RDF URI): RDF entity from Namespace

        Returns:
            Object: object instance equivilant of given RDF object
        '''
        for key, value in self.scene_relation_dict.items():
            if value == rdf_obj:
                return key

    def remove_triplets_from_rdf_database(self, d_list):
        '''removes triplets from RDF graph

        Args:
            d_list (_type_): _description_

        Returns:
            rdflib.graph.Graph: new RDF graph
        '''
        for triplet in d_list:
            self.graph.remove(triplet)
        return self.graph

    def remove_triplets(self, _graph: Graph, d_list):
        '''removes triplets from _graph

        Args:
            d_list (_type_): _description_

        Returns:
            rdflib.graph.Graph: _graph
        '''
        for triplet in d_list:
            _graph.remove(triplet)
        return _graph

    def add_triplets_to_rdf_database(self, a_list):
        '''adds triplets to the RDF graph

        Args:
            a_list (_type_): _description_


        Returns:
            rdflib.graph.Graph: new RDF graph
        '''

        for _tuple in a_list:
            self.graph.add(_tuple)
        return self.graph

    def add_triplets(self, _graph: Graph, a_list):
        '''adds triplets to the RDF graph

        Args:
            a_list (_type_): _description_


        Returns:
            rdflib.graph.Graph: new RDF graph
        '''

        for _tuple in a_list:
            _graph.add(_tuple)
        return _graph

    def triplet_from_relation(self, relation):
        '''generates RDF triplet from single SD relation

        Args:
            relation (Dict): Relation based on SD Objects and Predicates

        Returns:
            Tuple: RDF triplet (RDF subject, RDF predicate, RDF object)
        '''
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
        '''generates new SD scene from manipulated RDF Database.
        The action manipulates the RDF Database but not SD scene itself in the first place.
        The new SD scene after the execution of the action has to be generated based on the manipulated RDF Database.
        Args:
            new_graph (rdflib.graph.Graph): new RDF Database after the execution of the action

        Returns:
            Scene: new SD Scene
        '''

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
                new_sd_relations = merge_dicts(new_sd_relations, {new_pred: [new_sub, new_obj]})
            except Exception as e:
                print(f'{e}:Error while creating new SD scene relations')

        from core.sdf_core import Scene
        new_scene = Scene(
            object_list=self.scene.object_list, scene_relations=new_sd_relations)
        return new_scene
