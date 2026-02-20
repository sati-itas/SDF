from __future__ import annotations

import re
from itertools import product
from logging import getLogger
from typing import TYPE_CHECKING
from typing import Dict
from urllib.parse import quote

from rdflib import Dataset
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib.compare import to_isomorphic
from rdflib.namespace import OWL
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import XSD
from rdflib.plugins.sparql import algebra
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.algebra import BGP
from rdflib.plugins.sparql.algebra import Union
from rdflib.plugins.sparql.sparql import Query

from sdf.core.utility.timing_utils import time_tracker


logger = getLogger(__name__)

# logger.setLevel(WARNING)  # Set logger to DEBUG level for detailed output 


if TYPE_CHECKING:
    from sdf.core.sdf_core import Scene

class NameSpaceRegistry:
    """Registry for commonly used namespaces in RDF graphs."""
    def __init__(self, base="http://example.org/"):
        self.BASE = base
        self.KN = Namespace(base + "knowledge#")
        self.DATA = Namespace(base + "data#")
        self.SCENE = Namespace(base + "Scene#")
        self.EX = Namespace(base)

        self.RDF = RDF
        self.RDFS = RDFS
        self.OWL = OWL
        self.XSD = XSD

        self.all = {
            "kn": self.KN,
            "data": self.DATA,
            "scene": self.SCENE,
            "ex": self.EX,
            "rdf": self.RDF,
            "rdfs": self.RDFS,
            "owl": self.OWL,
            "xsd": self.XSD,
        }

    def bind_all(self, graph):
        for p, ns in self.all.items():
            graph.bind(p, ns)


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

        self.rules = []

        self.list_of_triplets = []
        self.rdf_triplet_list = []
        self.namespace_list = []

        self.object_mapping_dict = {}
        self.subject_mapping_dict = {}
        self.predicate_mapping_dict = {}
        self.sd_rdf_dict = {}

        ## load Namespaces from NameSpaceRegistry
        # initialize base uri and namespace registry (default to example.org)
        if not base_uri:
            base_uri = 'http://example.org/'
        self.base_uri = base_uri
        self.nsr = NameSpaceRegistry(base=self.base_uri)

        # Dataset for multiple graphs
        persistent_store = False
        # create persistent store (sqlite) for dataset
        if persistent_store:
            # TODO make the store 
            # https://rdflib.readthedocs.io/en/latest/apidocs/rdflib.plugins.stores.berkeleydb/#rdflib.plugins.stores.berkeleydb.has_bsddb
            self.dataset = Dataset("BerkeleyDB")
            self.dataset.open("rdf_store", create=True)

        else:
            self.dataset = Dataset()

        self.tbox = self.dataset.graph(URIRef(f'{self.base_uri}/graphs/tbox'))
        self.abox = self.dataset.graph(URIRef(f'{self.base_uri}/graphs/abox'))

        self.knowledge_graph = self.tbox
        ## TODO currently a little hacky, fix later  # noqa: E266
        #self.KN = self.nsr.KN # --> not loading graph
        ##testing without KN loading from file: test_rdf_wrapper_copy.py, test_rdf_wrapper.py will  # noqa: E265

        self.KN = self.nsr.SCENE #--> load graph
        ## testing with KN loading from file (here the namespace should adopt if you load a different KN graph with different Namespace)  # noqa: E266
        ## testing with test_rdf_wrapper_copy.py and test_rdf_wrapper.py will generate wrong namspaces  # noqa: E266

        self.nsr.bind_all(self.tbox)

        self.data_graph = self.abox
        self.DATA = self.nsr.DATA
        self.nsr.bind_all(self.abox)

    def load_scene(self, scene: Scene):
        """Loads a new scene into the RDFWrapper.

        Args:
            scene (Scene): The scene to load.
        """
        self.scene = scene
        self.scene_objects = scene.object_map
        self.scene_relation_dict = scene.scene_relations

    def set_base_uri(self, uri: str):
        self.base_uri = uri
        if not self.base_uri.endswith(('#', '/')):
            self.base_uri += '#'
        return self.base_uri

    def to_uri(self, value: str) -> URIRef:
        """Converts a string to an URIRef using RDFUtils."""
        return RDFUtils.to_uri(value)

    def to_literal(self, value: float | int) -> Literal:
        """Converts a number to a Literal with xsd:float or xsd:integer type."""
        return RDFUtils.number_to_literal(value)

    def get_base_uri(self, loaded_graph: Graph):
        """get base uri from loaded graph"""
        if any(loaded_graph.subjects(RDF.type, OWL.Ontology)):
            for s in loaded_graph.subjects(RDF.type, OWL.Ontology):
                self.base_uri = str(s)
                if not self.base_uri.endswith(('#', '/')):
                    self.base_uri += '#'
                break
        else:
            print(f'[RDFWrapper]: No base uri found; wrapper base uri set to {self.base_uri}\n')
            print(f'[RDFWrapper]: You can set base uri manually via rdf_wrapper.set_base_uri(uri:str) method.\n')
            # self.base_uri = next(iter(loaded_graph.namespaces()))[1]

    def get_subclasses(self, loaded_graph: Graph, class_uri: str):
        """get all subclasses of a given class_uri using RDFUtils"""
        return RDFUtils.get_subclasses(loaded_graph, class_uri)

    def get_properties(self, loaded_graph: Graph):
        """get all properties from graph if they marked with OWL.ObjectProperty"""
        return RDFUtils.get_properties(loaded_graph)

    def get_predicates(self, loaded_graph: Graph):
        """get all predicates/properties from graph if they marked with OWL.ObjectProperty or RDF.Property"""
        return RDFUtils.get_predicates(loaded_graph)

    def get_attributes(self, loaded_graph: Graph):
        """get all data properties from graph if they marked with OWL.DatatypeProperty or RDF.Property, where rdfs:range is an XSD datatype or rdfs:Literal"""
        return RDFUtils.get_attributes(loaded_graph)

    def load_rdf_graph(self, data_graph: str, format_: str):
        """loads RDF graph from file"""
        # https://rdflib.readthedocs.io/en/stable/plugin_parsers.html
        # https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph.parse
        loaded_graph = Graph().parse(f'sdf/data/{data_graph}', format=format_)
        return loaded_graph

    def load_knowledge_graph(self, path: str) -> Graph:
        # TODO add tbox to self.knowledge_graph ?
        g = Graph()
        g.parse(path, format="turtle")
        self.tbox += g
        return g

    def get_attrs_and_pred_kg(self):
        """ Everything comes from the loaded knowledge graph in self.tbox (self.knowledge_graph)

        Returns:
            attributes (set): set of attribute names (data properties)
            predicates (set): set of predicate names (object properties)
        """

        #TODO
        # self.data_graph = self.create_data_graph(self.knowledge_graph)

        # self.merged_graph = self.knowledge_graph + self.data_graph
        #self.tbox += self.knowledge_graph
        #self.abox += self.data_graph


        # print(f'[RDFWrapper] Knowledge graph prepared with namespaces:\n')
        # for prefix, ns in self.knowledge_graph.namespaces():
        #     print(f'\t{prefix}: {ns}')
        # print(self.knowledge_graph.serialize(format='turtle'))

        attributes = self.get_attributes(self.knowledge_graph)
        predicates = self.get_predicates(self.knowledge_graph)
        return attributes, predicates

    def _ensure_predicate_mapping(self, sd_predicate, KN= None):
        """Ensure mapping exists for sd_predicate and return its URIRef."""
        if KN is None:
            KN = self.KN
        pred_uri = KN[sd_predicate.name]
        if sd_predicate not in self.predicate_mapping_dict:
            self.predicate_mapping_dict[sd_predicate] = pred_uri
        return pred_uri

    @time_tracker('gen_rdf_datagraph_processing_time')
    def generate_data_graph(self, object_attributes) -> Graph:
        """Generates and maps data based on the given ontology"""
        data_triples = []

        # iterate over all relations in current scene and generate ObjectProperty
        for sd_predicate, pairs_list in self.scene_relation_dict.items():
            pred_uri = self._ensure_predicate_mapping(sd_predicate)

            # Tripel hinzufügen
            for sd_subj, sd_obj in pairs_list:
                subj_uri = self.obj_uri(sd_subj)
                obj_uri = self.obj_uri(sd_obj)
                # add subject and object mapping
                self.subject_mapping_dict[sd_subj] = subj_uri
                self.object_mapping_dict[sd_obj] = obj_uri

                # add subject and object to data graph
                # use object_to_rdf function
                # to speed up the process comment this out
                subj_data_triple = self.object_to_rdf(sd_subj, template=object_attributes)
                data_triples.extend(subj_data_triple)
                obj_data_triple = self.object_to_rdf(sd_obj, template=object_attributes)
                data_triples.extend(obj_data_triple)

                # Add the relation triple
                data_triples.append((subj_uri, pred_uri, obj_uri))
        # Batch add all triples
        for triple in data_triples:
            self.abox.add(triple)

        # merge all mappings into sd_rdf_dict
        self.sd_rdf_dict = {
            **self.predicate_mapping_dict,
            **self.subject_mapping_dict,
            **self.object_mapping_dict,
        }
        return self.abox

    @time_tracker('gen_rdf_graph_processing_time')
    def generate_graph(self, object_template=None, predicates=None) -> Graph:
        """Generates a knowledge and data graph from the current scene.
        """
        knowledge_triples = []
        data_triples = []

        for obj in self.scene_objects.values():
            # if object type is not in knowledge graph, add it
            class_uri = self.KN[obj.object_type]
            if (class_uri, RDF.type, None) not in self.knowledge_graph:
                # print(f"ObjectType '{obj.object_type}' not in ontology - adding it: {class_uri}")
                class_uri = self.KN[obj.object_type]
                knowledge_triples.append((class_uri, RDF.type, RDFS.Class))
                knowledge_triples.append(
                    (class_uri, RDFS.label, Literal(f'{obj.object_type}'))
                )
        # add predicates to knowledge graph
        if predicates is not None:
            for sd_predicate in predicates.values():
                self._ensure_predicate_mapping(sd_predicate)
        # iterate over all relations in current scene and generate ObjectProperty
        for sd_predicate, pairs_list in self.scene_relation_dict.items():
            pred_uri = self._ensure_predicate_mapping(sd_predicate)

            # if predicate is not in knowledge graph, add it
            if (pred_uri, RDF.type, None) not in self.knowledge_graph:
                # print(f"Predicate '{sd_predicate.name}' not in ontology - adding it: {pred_uri}")
                knowledge_triples.append(
                    (pred_uri, RDF.type, RDF.Property)
                )  # OWL.ObjectProperty
                knowledge_triples.append(
                    (pred_uri, RDFS.label, Literal(sd_predicate.name))
                )

            # Tripel hinzufügen
            for sd_subj, sd_obj in pairs_list:
                subj_uri = self.obj_uri(sd_subj)
                obj_uri = self.obj_uri(sd_obj)
                # add subject and object mapping
                self.subject_mapping_dict[sd_subj] = subj_uri
                self.object_mapping_dict[sd_obj] = obj_uri

                # add subject and object to data graph
                # use object_to_rdf function
                # to speed up the process comment this out
                subj_data_triple = self.object_to_rdf(sd_subj, template=object_template)
                data_triples.extend(subj_data_triple)
                obj_data_triple = self.object_to_rdf(sd_obj, template=object_template)
                data_triples.extend(obj_data_triple)

                # Add the relation triple
                data_triples.append((subj_uri, pred_uri, obj_uri))

        # Batch add all triples
        for triple in knowledge_triples:
            self.knowledge_graph.add(triple)
        for triple in data_triples:
            self.data_graph.add(triple)

        # merge all mappings into sd_rdf_dict
        self.sd_rdf_dict = {
            **self.predicate_mapping_dict,
            **self.subject_mapping_dict,
            **self.object_mapping_dict,
        }
        # to use the knowledge graph in the data graph by binding the namespace
        # self.data_graph.bind('scene', self.KN)

        # print(self.knowledge_graph.serialize(format="turtle"))
        # print(self.data_graph.serialize(format="turtle"))
        # for key, value in self.sd_rdf_dict.items():
        #     print(f'\tkey (sd object): {key} \n \tvalue (rdf object): {value}\n \n')

        # TODO warmup graph (load graph in memory)
        # if warmup:
        #   self.graph.query(("ASK { ?s ?p ?o }"))

        return self.data_graph

    def obj_uri(self, obj):
        # helper function to generate URIRef for objects
        return URIRef(
            self.DATA + quote(obj.name)
        )  # or URIRef(self.DATA + quote(obj.id))

    def object_to_rdf(self, obj, template=None, knowledge_ns=None, data_ns=None):
        # TODO currently: static Template for object to RDF conversion,
        #  instead of using knowledge graph to get properties of an object type.
        obj_data_triples = []

        if template is None:
            return obj_data_triples  # return empty list if no template is provided

        if knowledge_ns is None:
            knowledge_ns = self.KN
        if data_ns is None:
            data_ns = self.DATA

        object_uri = self.obj_uri(obj)

        # Typ-Tripel hinzufügen (z.B. ex:Vehicle)
        # obj_type = getattr(obj, 'object_type', None) #TODO
        # if obj_type:
        #     obj_data_triples.append((object_uri, RDF.type, knowledge_ns[obj_type]))

        # obj_name = getattr(obj, "name", None)
        # if obj_name:
        #     obj_data_triples.append((object_uri, RDFS.label, Literal(obj_name)))

        # obj_id = getattr(obj, "id", None)
        # if obj_id:
        #     obj_data_triples.append((object_uri, knowledge_ns["id"], Literal(obj_id)))

        # Attribute als Properties einfügen
        for attr in template:
            if attr in {'id', 'object_type', 'name'}:
                continue  # schon verarbeitet

            if hasattr(obj, attr):
                value = getattr(obj, attr)
                if value is not None:
                    # add the attribute as a triple
                    obj_data_triples.append(
                        (object_uri, knowledge_ns[attr], Literal(value))
                    )
                    from sdf.core.sdf_core import Predicate

                    # generate sd_predicates from template
                    sd_predicate = Predicate(attr)
                    if sd_predicate not in self.predicate_mapping_dict:
                        self.predicate_mapping_dict[sd_predicate] = knowledge_ns[attr]

        return obj_data_triples

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
            new_sub = new_pred = new_obj = None
            for key, value in self.sd_rdf_dict.items():
                if triplet[0] == value:
                    new_sub = key
                if triplet[1] == value:
                    new_pred = key
                if triplet[2] == value:
                    new_obj = key
            if new_pred is not None and new_sub is not None and new_obj is not None:
                new_sd_relations.setdefault(new_pred, []).append([new_sub, new_obj])

        from sdf.core.sdf_core import Scene

        new_scene = Scene(
            object_map=self.scene.object_map, scene_relations=new_sd_relations
        )
        return new_scene

    def serialize_rdf_graph(self, graph_name: str):
        """serialize to turtle per default"""
        with open(f'sdf/data/{graph_name}.ttl', 'wb') as f:
            self.data_graph.serialize(f, format='turtle')

    def prepare_sparql_query(self, query: str):
        """Prepares the SPARQL query for the RDF graph using RDFUtils.
        RDFUtils will translate the string query into a Query object provided by rdflib."""
        return RDFUtils.prepare_sparql_query(query, self.base_uri)

    def rewrite_sparql_query(self, query: str):
        """Rewrites the SPARQL query for the RDF graph using RDFSRewriter."""
        if not hasattr(self, 'tbox') and self.tbox is None:
            raise Exception('[RDFWrapper] TBox not found for query rewriting. Please load a knowledge graph first.')
        rdfs_rewriter = RDFSRewriter(tbox=self.tbox)
        return rdfs_rewriter.rewrite_sparql_query(query)

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
        return RDFUtils.query_rdf_graph(
            graph, query=query, prepared_query=prepared_query
        )

    def copy_rdf_graph(self, g: Graph) -> Graph:
        """Creates a copy of the given RDF graph from the given graph.
        Args:
            graph (Graph): The RDF graph to copy.
        Returns:
            Graph: A new RDF graph that is a copy of the original.
        """
        g = RDFUtils.copy_graph(g)
        self.nsr.bind_all(g)
        return g

    def remove_triplets(self, _graph: Graph, d_list):
        """removes triplets from RDF graph using RDFUtils"""
        return RDFUtils.remove_triplets(_graph, d_list)

    def add_triplets(self, _graph: Graph, a_list):
        """adds triplets to the RDF graph using RDFUtils"""
        return RDFUtils.add_triplets(_graph, a_list)

    def init_ruler(self, rules=None):
        """Initializes the RDF ruler with predefined rules."""
        self.rules = rules if rules is not None else []
        # Apply initial rules to the data graph
        self.abox = self.apply_rules(self.abox)
        logger.info(f'[RDFWrapper] Initialized with {len(self.rules)} rules.')

    def apply_rules(self, graph: Graph, rules=None) -> Graph:
        """
        Applies predefined rules to the RDF graph.

        Args:
            graph (Graph): The RDF graph to which rules will be applied.

        Returns:
            Graph: The updated RDF graph after applying rules.

        Raises:
            TypeError: If the input is not an rdflib.Graph.
            Exception: If a rule application fails.

        Information:
            - self.rules should be a list of dicts, each with keys:
                'type': 'python' or 'sparql'
                'function': Python function ('python')
                'query': SPARQL query string ('sparql')
            - The function logs info about each rule application and errors.
        """
        if rules is not None:
            self.rules = rules
        if not isinstance(graph, Graph):
            logger.error("[RDFWrapper] Input 'graph' must be an rdflib.Graph instance.")
            raise TypeError("[RDFWrapper] Input 'graph' must be an rdflib.Graph instance.")

        if not self.rules:
            logger.info('[RDFWrapper] No rules to apply.')
            return graph

        try:
            for idx, rule in enumerate(self.rules):
                if not isinstance(rule, dict) or 'type' not in rule:
                    logger.error(f"[RDFWrapper] Rule at index {idx} is not a valid dict with a 'type' key.")
                    raise ValueError(f"[RDFWrapper] Rule at index {idx} is not a valid dict with a 'type' key.")

                if rule['type'] == 'python':
                    if 'function' not in rule or not callable(rule['function']):
                        logger.error(f"[RDFWrapper] Python rule at index {idx} missing or invalid 'function'.")
                        raise ValueError(f"[RDFWrapper] Python rule at index {idx} missing or invalid 'function'.")
                    graph = rule['function'](graph)
                elif rule['type'] == 'sparql':
                    if 'query' not in rule or not isinstance(rule['query'], str):
                        logger.error(f"[RDFWrapper] SPARQL rule at index {idx} missing or invalid 'query'.")
                        raise ValueError(f"[RDFWrapper] SPARQL rule at index {idx} missing or invalid 'query'.")
                    prepared_query = self.prepare_sparql_query(rule['query'])
                    graph.update(prepared_query)
                else:
                    logger.error(f"[RDFWrapper] Unknown rule type '{rule['type']}' at index {idx}.")
                    raise ValueError(f"[RDFWrapper] Unknown rule type '{rule['type']}' at index {idx}.")
        except Exception as e:
            logger.info(f"[RDFWrapper] Error applying rule {idx + 1}: {e}")

        return graph


class RDFUtils:
    """Utility class for RDF operations"""

    @staticmethod
    def show_graph(loaded_graph: Graph):
        """Displays the RDF graph in Turtle format if you call it with print(RDFUtils.show_graph(loaded_graph))"""
        return loaded_graph.serialize(format='turtle')

    @staticmethod
    def get_properties(loaded_graph: Graph):
        """get all properties from graph if they marked with OWL.ObjectProperty"""
        properties = set()
        for pred in loaded_graph.subjects(RDF.type, [OWL.ObjectProperty, RDF.Property]):
            properties.add(pred.split('#')[-1])
            # print("object-property:", pred.split("#")[-1])
        if properties:
            return properties
        else:
            return None

    @staticmethod
    def get_predicates(loaded_graph: Graph):
        """get all object-relations (predicates) from graph if they marked with OWL.ObjectProperty or RDF.Property"""
        predicates = set()

        for attr in loaded_graph.subjects(RDF.type, OWL.ObjectProperty):
            predicates.add(attr.split('#')[-1])

        # if RDF.Property is used as object property divide object and datatype properties by inspecting rdfs:range.
        for pred in loaded_graph.subjects(RDF.type, RDF.Property):
            ranges = list(loaded_graph.objects(pred, RDFS.range))
            if not ranges:
                # no range declared -> treat as object property
                predicates.add(pred.split('#')[-1])
                continue
            # consider it an object property if any range is not an XSD datatype
            is_object_property = any(
                not (isinstance(r, URIRef) and str(r).startswith(str(XSD))) for r in ranges
            )
            if is_object_property:
                predicates.add(pred.split('#')[-1])
        if predicates:
            return predicates
        else:
            return None

    @staticmethod
    def get_attributes(loaded_graph: Graph):
        """get all data properties from graph if they marked with OWL.DatatypeProperty or RDF.Property, where rdfs:range is an XSD datatype or rdfs:Literal"""
        attributes = set()
        # first check for OWL.DatatypeProperty
        for attr in loaded_graph.subjects(RDF.type, OWL.DatatypeProperty):
            attributes.add(attr.split('#')[-1])
        # case where only RDF.Property is used as datatype property
        # Divide object and datatype properties by inspecting rdfs:range.
        # Treat as datatype property only if rdfs:range is an XSD datatype.
        for prop in loaded_graph.subjects(RDF.type, RDF.Property):
            ranges = list(loaded_graph.objects(prop, RDFS.range))
            if not ranges:
                # no range declared -> don't treat as datatype property
                continue
            # consider it as datatype property if any range is an XSD datatype
            is_datatype = any(
                isinstance(r, URIRef) and str(r).startswith(str(XSD))
                or r == RDFS.Literal
                or isinstance(r, Literal)
                for r in ranges
            )
            if is_datatype:
                attributes.add(prop.split('#')[-1])
                # print("datatype-property:", prop.split("#")[-1])
        if attributes:
            return attributes
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
        if not value.startswith('http://') and not value.startswith('https://'):
            raise ValueError(
                f"Invalid URI: {value}. Must start with 'http://' or 'https://'."
            )
        return URIRef(value)

    @staticmethod
    def number_to_literal(value: float | int) -> Literal:
        """Converts a number to a Literal with xsd:float type."""
        if isinstance(value, float):
            return Literal(value, datatype=XSD.float)
        elif isinstance(value, int):
            return Literal(value, datatype=XSD.integer)
        else:
            raise TypeError(f"Unsupported type for conversion to Literal: {type(value)}")

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
    def canonical_rdf_signature(graph: Graph) -> tuple:
        """Returns a hashable, canonical signature for an RDF graph."""
        facts = sorted((str(s), str(p), str(o)) for s, p, o in graph)
        return tuple(facts)

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
            """
        )

        delete_template.execute(graph=graph, subject=subject)
        return graph

    @staticmethod
    def insert_subject(graph: Graph, subject: str, predicate: str, value: str):
        """Inserts a new subject into the RDF graph. with SPARQL INSERT query.
        Args:
            graph (Graph): The RDF graph to insert the subject into.
            subject (str): The subject to be inserted.
            predicate (str): The predicate for the triple.
            value (str): The value for the triple.
        Returns:
            Graph: The updated RDF graph.
        """
        insert_template = SPARQLTemplate(
            """
                INSERT DATA {
                    <{subject}> <{predicate}> "{value}" .
                }
            """
        )

        insert_template.execute(graph=graph, subject=subject, predicate=predicate, value=value)
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
        # return g + Graph()

    # @time_tracker_static('query_rdf_graph_processing_time')
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
            print(f'Error while querying RDF graph: {e}')
            return None

    @staticmethod
    def prepare_sparql_query(query: str, base_uri: str) -> Query:
        """
        Prepares the SPARQL query for the RDF graph.
        Compiles the SPARQL query once and saves it as bytecode.

        Args:
            query (str): SPARQL query.
            base_uri (str): Base URI to initialize the namespace.

        Returns:
            Query: Prepared query.
        """
        q = prepareQuery(
            query,
            initNs={
                'owl': OWL,
                'rdf': RDF,
                'rdfs': RDFS,
                'ex': Namespace(base_uri),
                'xsd': XSD,
                # 'kn': self.KN,
                # 'data': self.DATA,
            },
        )
        return q


class SPARQLTemplate:
    def __init__(self, template_str):
        self.template = template_str

    def render(self, **kwargs):
        # return self.template.format(**kwargs)
        def _repl(match):
            key = match.group(1)
            return str(kwargs.get(key, match.group(0)))
        return re.sub(r'\{(\w+)\}', _repl, self.template)

    def execute(self, graph, **kwargs):
        query = self.render(**kwargs)
        return graph.update(query)


class RDFSRewriter:
    """RDFS Query Rewriter for SPARQL queries based on a TBox graph."""
    # https://titan.dcs.bbk.ac.uk/~michael/sw15/slides/SPARQL.pdf
    # https://doi.org/10.1007/s13218-020-00671-w

    def __init__(self, tbox):
        self.idx = self.build_rdfs_index(tbox)

        self.parser = SPARQLParser()

    def rewrite_sparql_query(self, query: str) -> Query:
        """Rewrites the given SPARQL query based on implicit TBox knowledge and returns the rewritten Query object."""
        q = self.parser.parse(query)

        #
        bgp = self.extract_bgp(q)
        rewritten = self.rewrite_bgp(bgp, self.idx)
        union_set = self.build_union_ast(rewritten)
        q = self.inject_union(q, union_set)

        return q

    def rewrite(self, sparql: str) -> str:
        """Rewrites the given SPARQL query based on implicit TBox knowledge and returns the rewritten SPARQL string."""
        q = self.parser.parse(sparql)

        #
        bgp = self.extract_bgp(q)
        rewritten = self.rewrite_bgp(bgp, self.idx)
        union_set = self.build_union_ast(rewritten)
        q = self.inject_union(q, union_set)

        # algebra translate to SPARQL-String
        rewritten_query = self.parser.get_sparql_string(q)
        return rewritten_query

    def build_rdfs_index(self, tbox):
        idx = {
            "subClass": {},
            "subProperty": {},
            "domain": {},
            "range": {}
        }

        for s, _, o in tbox.triples((None, RDFS.subClassOf, None)):
            idx["subClass"].setdefault(o, set()).add(s)

        for s, _, o in tbox.triples((None, RDFS.subPropertyOf, None)):
            idx["subProperty"].setdefault(o, set()).add(s)

        for s, _, o in tbox.triples((None, RDFS.domain, None)):
            idx["domain"][s] = o

        for s, _, o in tbox.triples((None, RDFS.range, None)):
            idx["range"][s] = o

        return idx

    def rewrite_bgp(self, patterns, idx):
        """ Basic Graph Pattern rewriting """
        rewritten = []

        for s, p, o in patterns:
            alts = self.rewrite_triple(s, p, o, idx)
            rewritten.append(alts)

        return rewritten

    def rewrite_triple(self, s, p, o, idx):
        alts = []

        # CASE 1: rdf:type C
        if p == RDF.type:
            classes = idx["subClass"].get(o, set()) | {o}
            for c in classes:
                alts.append((s, RDF.type, c))

        # CASE 2: Property
        else:
            props = idx["subProperty"].get(p, set()) | {p}
            for pr in props:
                alts.append((s, pr, o))

                # DOMAIN
                if pr in idx["domain"]:
                    alts.append((s, RDF.type, idx["domain"][pr]))

                # # RANGE
                # if pr in idx["range"]:
                #     alts.append((o, RDF.type, idx["range"][pr]))

        return list(alts)

    def build_union_ast(self, alternatives_per_triple):
        """
        alternatives_per_triple = [
            [(s,p,o), (s,p,o2)],   # Triple 1 alternatives
            [(s2,p2,o2)],          # Triple 2 alternatives
        ]
        """
        ## TODO pruning avoid combinatorial explosion of alternatives per triple

        all_combinations = product(*alternatives_per_triple)

        seen = set()
        bgps = []
        ## remove duplicates
        for combo in all_combinations:
            canon = tuple(sorted(combo))   # canonical form
            if canon not in seen:
                seen.add(canon)
                bgps.append(BGP(list(combo)))

        # All BGPs to a nested Union
        if not bgps:
            return None

        u = bgps[0]
        for b in bgps[1:]:
            u = Union(u, b)
        return u

    # def extract_bgp(self, q):
    #     """Extracts triples from the WHERE clause of a SPARQL query."""
    #     for project in q.algebra.values():
    #         test = project.values()
    #         for p in project.values():
    #             if p.name == 'BGP':
    #                 return p.triples
    #     raise ValueError("No BGP found")

    def extract_bgp(self, q):
        """Extracts triples from the WHERE clause of a SPARQL query."""
        bgps = []

        def finder(node):
            # algebra nodes have .name
            if hasattr(node, "name") and node.name == "BGP":
                bgps.append(node.triples)
            return None  # keep everything else

        algebra.traverse(q.algebra, finder)
        if not bgps:
            raise ValueError("No BGP found")
        elif len(bgps) == 1:
            return bgps[0]
        else:
            # merge multiple BGPs
            merged = []
            for b in bgps:
                merged.extend(b)
            return merged

    def inject_union(self, q, union_node):
        """Injects the union node into the query algebra, replacing the original BGP."""

        def updater(node):
            # algebra nodes have .name
            if hasattr(node, "name") and node.name == "BGP":
                return union_node   # replace BGP
            return None             # keep everything else

        q.algebra = algebra.traverse(q.algebra, updater)
        return q


class SPARQLParser:
    def parse(self, sparql: str):
        parsed = parser.parseQuery(sparql)
        return algebra.translateQuery(parsed)

    def get_sparql_string(self, query) -> str:

        return algebra.translateAlgebra(query)