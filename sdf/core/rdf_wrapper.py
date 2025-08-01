from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Dict
from urllib.parse import quote

from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib.compare import to_isomorphic
from rdflib.namespace import OWL
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import XSD
from rdflib.plugins.sparql import prepareQuery

from sdf.core.utility.timing_utils import time_tracker


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

        # Define data_graphs and namespace for data
        self.data_graph = Graph()
        self.DATA = Namespace(f'{self.base_uri}data#')
        self.data_graph.bind('data', self.DATA)
        # Define knowledge_graph namespac for knowledge
        self.knowledge_graph = Graph()
        self.KN = Namespace(f'{self.base_uri}knowledge#')
        self.knowledge_graph.bind('scene', self.KN)

    def set_base_uri(self, uri: str):
        self.base_uri = uri
        return self.base_uri

    def to_uri(self, value: str) -> URIRef:
        """Converts a string to an URIRef using RDFUtils."""
        return RDFUtils.to_uri(value)

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

    def load_rdf_graph(self, data_graph: str, format_: str):
        """loads RDF graph from file"""
        # https://rdflib.readthedocs.io/en/stable/plugin_parsers.html
        # https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph.parse
        loaded_graph = Graph().parse(f'sdf/data/{data_graph}', format=format_)
        return loaded_graph

    def load_and_prepare_knowledge_graph(self, load_graph: str):
        """Loads a knowledge graph from file, sets base URI, and binds the namespace."""
        self.knowledge_graph = self.load_rdf_graph(load_graph, 'ttl')
        self.get_base_uri(self.knowledge_graph)
        self.KN = Namespace(f'{self.base_uri}knowledge#')
        self.knowledge_graph.bind('scene', self.KN)
        print(self.knowledge_graph.serialize(format='turtle'))

    @time_tracker('gen_rdf_graph_processing_time')
    def generate_graph(self, object_template=None) -> Graph:
        """Generates a knowledge graph and data graph from the current scene.
        If no graph is provided, it generates a new knowledge graph based on the scene
        objects types and relations.
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

        # iterate over all relations in current scene and generate ObjectProperty
        for sd_predicate, pairs_list in self.scene_relation_dict.items():
            pred_uri = self.KN[sd_predicate.name]

            # add predicate mapping
            self.predicate_mapping_dict[sd_predicate] = pred_uri

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
        self.data_graph.bind('scene', self.KN)

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
        # TODO currently: static Template for object to RDF conversion
        #  instead of using knowledge graph to get properties of an object type.
        obj_data_triples = []

        if template is None:
            return obj_data_triples  # return empty list if no template is provided

        if knowledge_ns is None:
            knowledge_ns = self.KN
        if data_ns is None:
            data_ns = self.DATA

        object_uri = self.obj_uri(obj)

        # Typ-Tripel hinzufügen (z. B. ex:Vehicle)
        obj_type = getattr(obj, 'object_type', None)
        if obj_type:
            obj_data_triples.append((object_uri, RDF.type, knowledge_ns[obj_type]))

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
        return RDFUtils.copy_graph(g)

    def remove_triplets(self, _graph: Graph, d_list):
        """removes triplets from RDF graph using RDFUtils"""
        return RDFUtils.remove_triplets(_graph, d_list)

    def add_triplets(self, _graph: Graph, a_list):
        """adds triplets to the RDF graph using RDFUtils"""
        return RDFUtils.add_triplets(_graph, a_list)


class RDFUtils:
    """Utility class for RDF operations"""

    @staticmethod
    def show_graph(loaded_graph: Graph):
        """Prints the RDF graph in turtle format."""
        print(loaded_graph.serialize(format='turtle'))

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
        if not value.startswith('http://') and not value.startswith('https://'):
            raise ValueError(
                f"Invalid URI: {value}. Must start with 'http://' or 'https://'."
            )
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
            """
        )

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
