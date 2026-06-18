from logging import DEBUG
from logging import getLogger
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from rdflib import Graph

from .utility.timing_utils import time_tracker


logger = getLogger(__name__)


class Thing:
    """base class 'Thing' for Object and Predicate class.
    name:str, ident:int are the (unique) key's to each Thing.
    """

    # name:str, ident:int should be unique and to each name belongs one identification number (ident).
    # TODO But than action and scene class are not able to use name and ident

    _id_counter = 0

    def __init__(self, name=None, ident=None):
        type(self)._id_counter += 1
        self.name = name
        self.__ident = type(self)._id_counter

    @property
    def id(self):
        return self.__ident


class SDObject(Thing):
    """Object class for creating dynamic and static objects in scene.

    Args:
        object_name (str): name of the object
        object_type: type of object corresponding to domain
        position(int): position of object in environment (default=None)
    """

    def __init__(self, object_name: str, object_type, **kwargs):
        """Initialize the SDObject with a name and an object type."""
        self.object_type = object_type
        Thing.__init__(self, name=object_name)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f'object | name={self.name}'  # id: {self.id} object type: {self.object_type}")#\n \

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # return self.id == other.id
            return self.name == other.name
        else:
            return False

    def __hash__(
        self,
    ):  # This method is necessary to be able to use the class as a key in a dictionary
        return hash(self.name)


class Predicate(Thing):
    """Predicate class for defining predicates (properties or relations) of single or between several objects

    Args:
        predicate_name (str): name of the object
        ident (int): identification of instance
    """

    def __init__(self, predicate_name: str):
        Thing.__init__(self, name=predicate_name)

    def __repr__(self) -> str:
        return f'predicate | name={self.name}, ident={self.id}'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def __hash__(
        self,
    ):  # This method is necessary to be able to use the class as a key in a dictionary
        return hash(self.name)

    @classmethod
    def gen_predicates(cls, predicates: set) -> Dict[str, "Predicate"]:
        """Generate Predicate instances from an iterable of names."""
        predicate_dict: Dict[str, "Predicate"] = {}
        for pred_str in predicates:
            predicate = cls(pred_str)
            predicate_dict[pred_str] = predicate
        return predicate_dict


class Scene(Thing):
    """Scene class for creating scenes from existing objects and predicates.

    Args:
        object_list ([Object]): list of all existing objects in scene
        scene_relations (Dict): dict of all related objects (key: predicate, value: (nested) list of linked objects)
    """

    def __init__(
        self,
        object_map: Dict[str, SDObject],
        scene_relations: Dict[Predicate, List[Union[List[int], Tuple[int, int]]]],
    ):
        Thing.__init__(self)

        # validate scene_relations
        if not isinstance(scene_relations, dict):
            raise TypeError('scene_relations have to be a dictionary')

        for key, value in scene_relations.items():
            if not isinstance(value, list):
                raise TypeError(f"The value for key '{key}' must be a list")

            for item in value:
                if (
                    not isinstance(item, (list, tuple))
                    or len(item) != 2
                    or not all(isinstance(i, SDObject) for i in item)
                ):
                    raise ValueError(
                        f"Invalid element {item} under key '{key}'. Expected (SDObject, SDObject) or [SDObject, SDObject]."
                    )

        self.scene_relations = scene_relations
        self.object_map = object_map

        self.graph_processing_time = 0.0

    def __repr__(self) -> str:
        """call with repr()"""
        str_to_print = ''
        for key, value in self.scene_relations.items():
            str_to_print = str_to_print + key.name + ':' + ' '
            for item in value:
                if not isinstance(item, list):
                    str_to_print = str_to_print + item.name + ' '
                if isinstance(item, list):
                    for itemitem in item:
                        str_to_print = str_to_print + itemitem.name + ' '
                    str_to_print = str_to_print + '\n'
            str_to_print = str_to_print + '\n'
        return f'scene | name={self.name}, ident={self.id}\n\n{str_to_print}'

    def __str__(self):
        """call with print() or str()"""
        return f'scene | name={self.name}, ident={self.id}'

    def __hash__(
        self,
    ):  # This method is necessary to be able to use the class as a key in a dictionary
        return hash(self.id)

    def get_relations_for_object(
        self, object_name: str
    ) -> Dict[Predicate, List[Union[List[int], Tuple[int, int]]]]:
        """Get all relations for a specific object in the scene.

        Args:
            object_name (str): name of the object to search for

        Returns:
            Dict[Predicate, List[Union[List[int], Tuple[int, int]]]]: Dictionary of predicates and their corresponding relations
        """
        relations = {}

        for predicate, objects in self.scene_relations.items():
            for obj_pair in objects:
                if isinstance(obj_pair, list):
                    if any(o.name == object_name for o in obj_pair):
                        relations.setdefault(predicate, []).append(obj_pair)

        return relations

    def search_relation(self, predicate: Predicate) -> List[SDObject]:
        """Searching a SDObject in scene_relation with the given predicate and returns SDObject instance

        Args:
            predicate (Predicate): predicate instance

        Returns:
            List[SD_Object]: _description_
        """
        return self.scene_relations[predicate]

    def search_object(self, object_name: str):
        """Searching a SDObject in a scene with the given name. Returns the first matching SDObject instance in scene.

        Args:
            object_name (str): name of scene object to be found

        Returns:
            Object: object instance with given name
        """
        counter = 0
        try:
            if object_name in self.object_map:
                return self.object_map[object_name]
            else:
                counter += 1

        except Exception as e:
            logger.info(
                f'{e}: Exception occured: {object_name} not an member of self.object_map'
            )

    def search_all_individuals_of_class(self, otype) -> List[SDObject]:
        """gets all individuals of given class-object

        Args:
            otype (LITERAL): Literal of object type to be found

        Returns:
            List[Object]: list of objects with given object type
        """
        obj_list = [
            scene_object
            for scene_object in self.object_map.values()
            if scene_object.object_type == otype
        ]
        return obj_list

    def init_rdf_wrapper(self, template=None, rules=None, predicates=None, knowledge_graph=None):
        """Initialize the RDF wrapper with the current scene
        and generate the corresponding RDF graph.
        Returns:
            rdf_wrapper (RDFWrapper): The initialized RDF wrapper.
        """
        from sdf.core.rdf_wrapper import RDFWrapper

        self.rdf_wrapper = RDFWrapper(self)
        if template is None:
            # Generate RDF graph and record processing time
            self.rdf_wrapper.generate_graph()
            self.graph_processing_time = self.rdf_wrapper.gen_rdf_graph_processing_time
        elif template is not None and predicates is not None:
            # Generate RDF graph with a specific template and record processing time
            self.rdf_wrapper.generate_graph(object_template=template, predicates=predicates)
            self.graph_processing_time = self.rdf_wrapper.gen_rdf_graph_processing_time

            if rules is not None:
                self.rdf_wrapper.init_ruler(rules=rules)

        elif knowledge_graph is not None:
            # loaded_graph = self.rdf_wrapper.load_rdf_graph(knowledge_graph)
            # attributes, predicates = self.rdf_wrapper.prepare_knowledge_graph(loaded_graph)
            # # predicates = Predicate.gen_predicates(predicates)

            # self.rdf_wrapper.generate_data_graph(object_attributes=attributes)
            # self.graph_processing_time = self.rdf_wrapper.gen_rdf_graph_processing_time

            if rules is not None:
                self.rdf_wrapper.init_ruler(rules=rules)

        else:
            raise ValueError(
                '[SDF.SCENE.init_rdf_wrapper] If arguments are provided, either template and predicates or knowledge_graph must be provided.'
            )

        return self.rdf_wrapper

    def get_scene_wrapper(self):
        """Get the RDF wrapper for the current scene.

        Returns:
            rdf_wrapper (RDFWrapper): The RDF wrapper associated with the scene.
        """
        if not hasattr(self, 'rdf_wrapper'):
            raise ValueError(
                'RDF wrapper is not initialized. Call init_rdf_wrapper() first.'
            )
        return self.rdf_wrapper

    def get_graph_processing_time(self):
        """graph_processing_time time of rdf-graph generation
        Returns (float): self.graph_processing_time
        """
        return self.graph_processing_time


class Action(Thing):
    """Action class for defining action template

    Args:
        name (str): action name
        precondition (str): SPARQL query that needs to be fulfilled in scene
        a_list (List[Dict]): List of relations to be added to scene after execution of action
            (key: Predicate instance, value: List of Strings representing selected values from query)
        d_list (List[Dict]): List of scene relations to be removed from scene after execution of action
            (e.g.: {is_on_lane: ["e", "x"]} | key (Predicate) = predicate, value (str) = List of variables representing
            selected values from query)
        select (List[str]): List of Variable names from SPARQL Query (?x etc.)
    """

    def __init__(
        self,
        action_name: str,
        precondition: str,
        a_list: List,
        d_list: List,
        select: List[str],
        weight: float = 1.0,
    ):
        Thing.__init__(self, name=action_name)
        self.precondition = precondition
        self.a_list = a_list
        self.d_list = d_list
        self.select = select

        self.weight = weight

        self.rdf_wrapper = None
        self.prep_query = None

        self.query_processing_time = 0.0
        self.effect_processing_time = 0.0
        self.execute_processing_time = 0.0

    def __repr__(self) -> str:
        return f'action | name={self.name}'

    def init_action_with_rdf(self, rdf_wrapper, rewrite: bool = False):
        """Initialize the RDF wrapper with the given scene and prepare the SPARQL query.
        By generate a bytecode of the SPARQL query and store it in self.prep_query.

        Args:
            rdf_wrapper (RDFWrapper): The RDF wrapper to initialize with.

        """
        if self.rdf_wrapper is None:
            self.rdf_wrapper = rdf_wrapper
        if rewrite:
            self.prep_query = self.rdf_wrapper.rewrite_sparql_query(self.precondition)
        else:
            self.prep_query = self.rdf_wrapper.prepare_sparql_query(self.precondition)

    def check_precondition_on_rdf(self, rdf_scene: Graph) -> bool:
        self.select_dict = {}
        self.select_dict_list = []

        if not self.prep_query:
            raise ValueError(
                f'{self.name} action is not initialized with a valid SPARQL query: use init_action() or init_action_with_rdf() first.'
            )

        # Execute the SPARQL query and record query processing time
        result = self.rdf_wrapper.query_rdf_graph(
            rdf_scene, prepared_query=self.prep_query
        )
        #result = set(result)  #TODO Convert to set to remove duplicates
        self.query_processing_time = self.rdf_wrapper.query_rdf_graph_processing_time

        # If query successful, generate a list of dicts with the selected variables
        if len(result.bindings) > 0:
            for row in result:
                self.select_dict = {}
                for var in self.select:
                    selected = row[var]
                    self.select_dict.update({var: selected})
                self.select_dict_list.append(self.select_dict)
            logger.info(
                f'{self.name}.check_precondition(): self.select_dict_list={self.select_dict_list}\n')
            # print(f'{self.name}.check_precondition(): {True}')# --- IGNORE ---
            return True
        else:
            logger.info(f'{self.name}.check_precondition(): precondition not satisfied')
            # print(f'{self.name}.check_precondition(): {False}')# --- IGNORE ---
            return False

    @time_tracker('execute_processing_time')
    def execute_action_on_rdf(self, rdf_scene: Graph):
        """Executes the action in a given rdf graph if possible.
        This includes action precondition checks and generating the follow-up rdf_scenes.
        If the precondition check generate a list of possible actions,
        all follow-up rdf_scenes will be build.

        Args:
            scene (Graph): scene, in which action shell by executed

        Returns:
            new_scene_action_dict (Dict[Graph:{Predicate:[SD subject,SD object]}):
            A List includes new rdf_scene list created by executing actions
            and a list of Dicts of the effects by executing actions.
            If preconditions for action not fullfilled return Bool:False
        """
        # initialize processing time
        self.execute_processing_time = 0.0
        self.query_processing_time = 0.0
        self.effect_processing_time = 0.0

        # precondition of action
        if self.check_precondition_on_rdf(rdf_scene):
            # effect of action
            new_graph_list, sd_rel_action_effect_list = self.action_effect_on_rdf(rdf_scene)

            if len(new_graph_list) == len(sd_rel_action_effect_list):
                new_scene_action_dict = dict(
                    zip(new_graph_list, sd_rel_action_effect_list, strict=False)
                )
            else:
                raise Exception('Error: scene list and effect list are not coherent')
            return new_scene_action_dict
        else:
            return False

    @time_tracker('effect_processing_time')
    def action_effect_on_rdf(self, rdf_scene: Graph):
        new_graph_list = self.remove_triplets_from_rdf(rdf_scene)
        new_graph_list, sd_rel_action_effect_list = self.add_triplets_to_rdf(new_graph_list)
        return new_graph_list, sd_rel_action_effect_list

    def remove_triplets_from_rdf(self, rdf_scene):
        """
        remove the RDF triplet from the graph from self.d_list
        self.d_list: Dict {SD_Predicate: [[str, str]]}
        1. map SELECT parameter to RDF subjects/objects
        2. map RDF subjects/objects to SD_Object instances
        3. remove triplet from graph
        """
        new_graph_list = []
        for select_dict in self.select_dict_list:
            new_graph = self.rdf_wrapper.copy_rdf_graph(rdf_scene)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'[SDF.ACTION.remove_triplets_from_rdf] select_dict: {select_dict}')
                from sdf.core.rdf_wrapper import RDFUtils
                logger.debug(f'[SDF.ACTION.remove_triplets_from_rdf] RDF GRAPH: dlist before: \n {RDFUtils.show_graph(new_graph)}')
            for d_dictonary in self.d_list:
                for pred, select_parameters in d_dictonary.items():
                    # Process the select parameters to extract the subject (sub) and object (obj)
                    for item in select_parameters:
                        if isinstance(item, list):
                            sub, obj = self.process_select_parameters(
                                item, select_dict
                            )
                            # Retrieve the predicate URI from sd_rdf_dict
                            predicate_uri = self.rdf_wrapper.sd_rdf_dict.get(pred)

                            if not predicate_uri:
                                raise KeyError(f'Predicate {pred} not found in sd_rdf_dict.')

                            # Create and remove the RDF triplet
                            triplet = (sub, predicate_uri, obj)
                            try:
                                new_graph = self.rdf_wrapper.remove_triplets(
                                    new_graph, [triplet]
                                )
                                logger.debug(f'[SDF.ACTION.remove_triplets_from_rdf] Deleted RDF triplet: {triplet}')
                                # print(f'\n[SDF.ACTION.remove_triplets_from_rdf] Deleted RDF triplet: \n{triplet}')
                            except Exception as e:
                                logger.warning(f'Error while removing d_list from current scene: {e}')
                        else:
                            sub, obj = self.process_select_parameters(
                                select_parameters, select_dict
                            )
                            # Retrieve the predicate URI from sd_rdf_dict
                            predicate_uri = self.rdf_wrapper.sd_rdf_dict.get(pred)

                            if not predicate_uri:
                                raise KeyError(f'Predicate {pred} not found in sd_rdf_dict.')

                            # Create and remove the RDF triplet
                            triplet = (sub, predicate_uri, obj)
                            try:
                                new_graph = self.rdf_wrapper.remove_triplets(
                                    new_graph, [triplet]
                                )
                                logger.debug(f'[SDF.ACTION.remove_triplets_from_rdf] Deleted RDF triplet: {triplet}')
                                # print(f'\n[SDF.ACTION.remove_triplets_from_rdf] Deleted RDF triplet: \n{triplet}')
                            except Exception as e:
                                logger.warning(f'Error while removing d_list from current scene: {e}')

            if logger.isEnabledFor(DEBUG):
                from sdf.core.rdf_wrapper import RDFUtils
                logger.debug(f'[SDF.ACTION.remove_triplets_from_rdf] RDF GRAPH: dlist after == alist before: \n {RDFUtils.show_graph(new_graph)}')
            # add new_graph to new_graph_list
            new_graph_list.append(new_graph)
        return new_graph_list

    def add_triplets_to_rdf(self, new_graph_list):
        """
        add the RDF triplet to the graph from a_list
        1. map SELECT parameter to RDF subjects/objects
        2. map RDF subjects/objects to SD_Object instances
        4. add the triplet to the graph
        """
        sd_rel_action_effect = {}
        sd_rel_action_effect_list = []
        new_graph_list_ = []
        # Invert the sd_rdf_dict for direct lookups: {rdf_uri: sd_object}
        rdf_to_sd_dict = {v: k for k, v in self.rdf_wrapper.sd_rdf_dict.items()}
        for select_dict, new_graph in zip(self.select_dict_list, new_graph_list):
            for a_dictonary in self.a_list:
                for pred, select_parameters in a_dictonary.items():
                    # Process the select parameters to extract the subject (sub) and object (obj)
                    sub, obj = self.process_select_parameters(
                        select_parameters, select_dict)
                    rdf_rel = {pred: [sub, obj]}
                    for sd_pred, rdf_sub_obj in rdf_rel.items():
                        # Directly retrieve the SD objects using the inverted dictionary
                        sd_sub = rdf_to_sd_dict.get(rdf_sub_obj[0])
                        sd_obj = rdf_to_sd_dict.get(rdf_sub_obj[1])
                        # Construct RDF triplet
                        sd_rel = {sd_pred: [sd_sub, sd_obj]}
                        triplet = (
                            rdf_sub_obj[0],
                            self.rdf_wrapper.sd_rdf_dict[sd_pred],
                            rdf_sub_obj[1],
                        )
                        # Update the graph and the action effect
                        try:
                            new_graph = self.rdf_wrapper.add_triplets(
                                new_graph, [triplet]
                            )
                            # update sd relation action effect,
                            # if sd_sub and sd_obj are not None and mapping exists
                            if sd_sub is None or sd_obj is None:
                                logger.warning(
                                    f'SD Mapping for RDF subject/object not found: {rdf_sub_obj} \\ Construct sd_rel anyway, even if sd_sub({sd_sub}) or sd_obj({sd_obj}) is None '
                                )
                            # Construct sd_rel anyway, even if sd_sub or sd_obj is None
                            sd_rel = {sd_pred: [sd_sub, sd_obj]}
                            sd_rel_action_effect.update(sd_rel)
                        except Exception as e:
                            logger.warning(
                                f'Error while adding triplet {triplet} to new scene: {e}'
                            )
            # Apply rules ONCE after the full effect (all removes done in the
            # d_list pass, all adds done above) — not per-triple. Per-triple
            # apply_rules ran over intermediate "hole" states (a subject's old
            # fact removed, new not yet added) where additive forward-rules
            # (NAF: noVehicleAhead/noLeaderInRange, free_front/left/right) could
            # derive stale facts that survived the final pass.
            new_graph = self.rdf_wrapper.apply_rules(new_graph)
            sd_rel_action_effect_list.append(sd_rel_action_effect)
            sd_rel_action_effect = {}
            if logger.isEnabledFor(DEBUG):
                from sdf.core.rdf_wrapper import RDFUtils
                logger.debug(f'[SDF.ACTION.add_triplets_to_rdf] RDF GRAPH: alist after: \n {RDFUtils.show_graph(new_graph)}')
            new_graph_list_.append(new_graph)

        return [new_graph_list_, sd_rel_action_effect_list]

    def process_select_parameters(self, select_parameters, select_dict):
        """
        Recursively process select_parameters to extract subject (sub) and object (obj).

        Args:
            select_parameters (list): The list of parameters to process.
            select_dict (dict): The dictionary containing mappings for SELECT variables.

        Returns:
            Tuple: A tuple (sub, obj) representing the processed URIs
            of subject and object depenting from select List.
        """
        sub, obj = None, None

        for item in select_parameters:
            if isinstance(item, list): #TODO fix this to process nested lists in select_parameters
                # Recursively process nested lists
                sub, obj = self.process_select_parameters(item, select_dict)
                if sub is not None and obj is not None:
                    break  # Stop processing if valid sub and obj are found
            elif isinstance(item, str):
                if item.startswith('http://') or item.startswith('https://'):
                    sub = self.rdf_wrapper.to_uri(item)
                    obj = select_dict.get(select_parameters[1])
                    if obj is None and (isinstance(select_parameters[1], int) or isinstance(select_parameters[1], float)):
                        obj = self.rdf_wrapper.to_literal(select_parameters[1])
                    logger.debug(f'[SDF.ACTION.process_select_parameters] Processed item: {item}, sub: {sub}, obj: {obj}')
                elif len(select_parameters) >= 1:
                    sub = select_dict.get(select_parameters[0])
                    if obj is None and (isinstance(obj, int) or isinstance(obj, float)):
                        obj = self.rdf_wrapper.to_literal(select_parameters[1])
                    obj = select_dict.get(select_parameters[1])
                    logger.debug(f'[SDF.ACTION.process_select_parameters] Processed item: {item}, sub: {sub}, obj: {obj}')
                break

        return sub, obj

    def get_query_processing_time(self):
        """processing time of query for checking the preconditions
        Returns (float): self.query_processing_time
        """
        return self.query_processing_time

    def get_effect_processing_time(self):
        """processing time of effect of action
        Returns (float): self.effect_processing_time
        """
        return self.effect_processing_time

    def get_execute_processing_time(self):
        """processing time execution: execute = precondition + effect
        Returns (float): self.execute_processing_time
        """
        return self.execute_processing_time


class SDUtils:
    """Utility class for Scene-related operations."""
    # TODO deprecated?

    @staticmethod
    def check_identical_scenes(scene1: Scene, scene2: Scene) -> bool:
        """Checks if scene1.scene_relations is equal to scene2.scene_relations."""
        return scene1.scene_relations.items() == scene2.scene_relations.items()

    @staticmethod
    def check_subset_scenes(goal_scene: Scene, scene: Scene) -> bool:
        """Checks if goal_scene.scene_relations is a subset or equal to scene.scene_relations."""
        return goal_scene.scene_relations.items() <= scene.scene_relations.items()

    @staticmethod
    def check_common_keys(scene1: Scene, scene2: Scene) -> bool:
        """Finds common keys between the scene relations of two scenes."""
        return scene1.scene_relations.keys() & scene2.scene_relations.keys()

    @staticmethod
    def check_subset_pair(goal: Scene, scene: Scene) -> bool:
        """Checks if goal.scene_relations is a subset of scene.scene_relations in a pairwise manner."""
        common_keys = goal.scene_relations.keys() & scene.scene_relations.keys()
        if common_keys:
            for key in common_keys:
                set1 = {tuple(sublist) for sublist in goal.scene_relations[key]}
                set2 = {tuple(sublist) for sublist in scene.scene_relations[key]}
                # set1 = set(dict1[key])  # TODO:Tupel direkt verwenden
                # set2 = set(dict2[key])  # TODO:Tupel direkt verwenden

                # calculate subset
                # subset = set1.issubset(set2)
                if not set1 <= set2:
                    return False
        return True

    @staticmethod
    def canonical_scene_signature(scene: Scene) -> Tuple:
        """Returns a hashable, canonical key for a Scene based on its facts."""
        facts = [
            (pred.name, *(obj.name for obj in objs))
            for pred, obj_list in scene.scene_relations.items()
            for objs in obj_list
        ]
        return tuple(sorted(facts))
