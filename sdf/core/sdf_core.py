from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from rdflib import Graph

from .utility.timing_utils import time_tracker


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

    def __init__(self, object_name: str, object_type):
        self.object_type = object_type
        Thing.__init__(self, name=object_name)

        self.course_angle = None
        self.object_length = None
        self.object_width = None

        self.RelPos_x = None
        self.RelPos_y = None
        self.RelPos_z = None

        self.RelAcc = None
        self.RelAcc_x = None
        self.RelAcc_y = None
        self.RelAcc_z = None

        self.AbsSpeed = None
        self.AbsSpeed_x = None
        self.AbsSpeed_y = None
        self.AbsSpeed_z = None

        self.RelSpeed = None
        self.RelSpeed_x = None
        self.RelSpeed_y = None
        self.RelSpeed_z = None

        self.MovingDirection = None
        self.MovingState = None
        self.RefPos = None

        self.YawRate = None
        self.Vel_x = None
        self.Vel_y = None
        self.Acc_x = None
        self.Acc_y = None

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

    def add_rel_speed(self, rel_speed):
        self.RelSpeed = rel_speed

    def add_rel_speed_x(self, rel_speed_x):
        self.RelSpeed_x = rel_speed_x

    def add_rel_speed_y(self, rel_speed_y):
        self.RelSpeed_y = rel_speed_y

    def add_rel_speed_z(self, rel_speed_z):
        self.RelSpeed_z = rel_speed_z

    def add_abs_speed(self, abs_speed):
        self.AbsSpeed = abs_speed

    def add_abs_speed_x(self, abs_speed_x):
        self.AbsSpeed_x = abs_speed_x

    def add_abs_speed_y(self, abs_speed_y):
        self.AbsSpeed_y = abs_speed_y

    def add_abs_speed_z(self, abs_speed_z):
        self.AbsSpeed_y = abs_speed_z

    def add_rel_acc(self, rel_acc):
        self.RelAcc = rel_acc

    def add_rel_acc_x(self, rel_acc_x):
        self.RelAcc_x = rel_acc_x

    def add_rel_acc_y(self, rel_acc_y):
        self.RelAcc_y = rel_acc_y

    def add_rel_acc_z(self, rel_acc_z):
        self.RelAcc_z = rel_acc_z

    def add_rel_pos_x(self, rel_pos_x):
        self.RelPos_x = rel_pos_x

    def add_rel_pos_y(self, rel_pos_y):
        self.RelPos_y = rel_pos_y

    def add_rel_pos_z(self, rel_pos_z):
        self.RelPos_z = rel_pos_z

    def add_moving_direction(self, moving_direction):
        self.MovingDirection = moving_direction

    def add_moving_state(self, moving_state):
        self.MovingState = moving_state

    def add_ref_pos(self, ref_pos):
        self.RefPos = ref_pos

    def add_yaw_rate(self, yaw_rate):
        self.YawRate = yaw_rate

    def add_vel_x(self, vel_x):
        self.Vel_x = vel_x

    def add_vel_y(self, vel_y):
        self.Vel_y = vel_y

    def add_acc_x(self, acc_x):
        self.Acc_x = acc_x

    def add_acc_y(self, acc_y):
        self.Acc_y = acc_y


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
            return self.id == other.id
        else:
            return False

    def __hash__(
        self,
    ):  # This method is necessary to be able to use the class as a key in a dictionary
        return hash(self.id)


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
            print(
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

    def init_rdf_wrapper(self):
        """Initialize the RDF wrapper with the current scene
        and generate the corresponding RDF graph.
        Returns:
            rdf_wrapper (RDFWrapper): The initialized RDF wrapper.
        """
        from sdf.core.rdf_wrapper import RDFWrapper

        rdf_wrapper = RDFWrapper(self)

        # Generate RDF graph and record processing time
        rdf_wrapper.gen_rdf_graph()
        self.graph_processing_time = rdf_wrapper.gen_rdf_graph_processing_time

        return rdf_wrapper

    def graph_processing_time(self):
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
    ):
        Thing.__init__(self, name=action_name)
        self.precondition = precondition
        self.a_list = a_list
        self.d_list = d_list
        self.select = select

        self.rdf_wrapper = None
        self.prep_query = None

    def __repr__(self) -> str:
        return f'action | name={self.name}'

    def init_action(self):
        """Initialize the RDF wrapper and prepare SPARQL Query.

        Args:
            scene (Scene): The scene to initialize the RDF wrapper with.
        """
        from sdf.core.rdf_wrapper import RDFWrapper

        self.rdf_wrapper = RDFWrapper()
        self.prep_query = self.rdf_wrapper.prepare_sparql_query(self.precondition)

    def init_action_with_rdf(self, rdf_wrapper):
        """Initialize the RDF wrapper with the given scene and prepare the SPARQL query.
        By generate a bytecode of the SPARQL query and store it in self.prep_query.

        Args:
            rdf_wrapper (RDFWrapper): The RDF wrapper to initialize with.

        """
        if self.rdf_wrapper is None:
            self.rdf_wrapper = rdf_wrapper
        self.prep_query = self.rdf_wrapper.prepare_sparql_query(self.precondition)

    def check_precondition_on_rdf(self, rdf_scene: Graph, debug=True) -> bool:

        self.select_dict = {}
        self.select_dict_list = []

        if not self.prep_query:
            raise ValueError(
                f'{self.name} action is not initialized with a valid SPARQL query'
            )

        # Execute the SPARQL query and record query processing time
        result = self.rdf_wrapper.query_rdf_graph(rdf_scene, prepared_query=self.prep_query)
        self.query_processing_time = self.rdf_wrapper.query_rdf_graph_processing_time

        # If query successful, generate a list of dicts with the selected variables
        if len(result.bindings) > 0:
            for row in result:
                self.select_dict = {}
                for var in self.select:
                    selected = row[var]
                    self.select_dict.update({var: selected})
                # if debug:
                #     print(f'{self.name}.check_precondition(): select_dict={self.select_dict}\n')
                self.select_dict_list.append(self.select_dict)
            if debug:
                # print(f'{self.name}.check_precondition(): scene database: {scene!r}')
                print(
                    f'{self.name}.check_precondition(): self.select_dict_list={self.select_dict_list}\n')
            return True
        else:
            if debug:
                print(f'{self.name}.check_precondition(): precondition not satisfied')
                # print(f'scene database: {scene!r}')
            return False

    @time_tracker('execute_processing_time')
    def execute_action_on_rdf(self, rdf_scene: Graph, debug=False):
        """Executes the action in a given rdf graph if possible.
        This includes action precondition checks and generating the follow-up rdf_scenes.
        If the precondition check generate a list of possible actions, all follow-up rdf_scenes will be build.

        Args:
            scene (Graph): scene, in which action shell by executed
            debug (bool, optional): _description_. Defaults to False.

        Returns:
            new_scene_action_dict (Dict[Graph:{Predicate:[SD subject,SD object]}):
            A List includes new rdf_scene list created by executing actions
            and a list of Dicts of the effects by executing actions.
            If preconditions for action not fullfilled return Bool:False
        """
        # precondition of action
        if self.check_precondition_on_rdf(rdf_scene, debug=debug):
            # effect of action
            new_graph_list, sd_rel_action_effect_list = self.action_effect_on_rdf(rdf_scene, debug=debug)

            if len(new_graph_list) == len(sd_rel_action_effect_list):
                new_scene_action_dict = dict(
                    zip(new_graph_list, sd_rel_action_effect_list, strict=False)
                )
            else:
                raise Exception('Error: scene list and effect list are not coherent')
            return new_scene_action_dict
        else:
            return False

    @time_tracker('execute_processing_time')
    def execute_action_on_sdscene(self, scene: Scene, debug=False):
        """Executes the action in a given scene if possible.
        Therefore, the scene is initialized with the RDF wrapper and the RDF graph is generated.
        The action is then executed on the RDF graph.
        This includes action precondition checks and generating the follow-up sd scenes.
        If the precondition check generate a list of possible actions, all follow-up scenes will be build.

        Args:
            scene (Scene): scene, in which action shell by executed
            debug (bool, optional): _description_. Defaults to False.

        Returns:
            new_scene_action_dict (Dict[Scene:{Predicate:[SD subject,SD object]}):
            A List includes new scene list created by executing actions
            and a list of Dicts of the effects by executing actions.
            If preconditions for action not fullfilled return Bool:False
        """
        # initialize the RDF wrapper with the current scene
        # and generate the corresponding RDF graph
        scene_rdf_wrapper = scene.init_rdf_wrapper()
        self.rdf_wrapper = scene_rdf_wrapper
        self.graph_processing_time = scene.graph_processing_time
        # precondition of action
        if self.check_precondition_on_rdf(scene_rdf_wrapper.graph, debug=debug):
            # effect of action
            new_graph_list, sd_rel_action_effect_list = self.action_effect_on_rdf(scene_rdf_wrapper.graph, debug=debug)
            # map RDF Database in SD scene
            new_scene_list = []
            for graph in new_graph_list:
                new_scene = self.rdf_wrapper.gen_sd_scene_from_rdf_database(graph)
                new_scene_list.append(new_scene)
            if len(new_scene_list) == len(sd_rel_action_effect_list):
                new_scene_action_dict = dict(
                    zip(new_scene_list, sd_rel_action_effect_list, strict=False)
                )
            else:
                raise Exception('Error: scene list and effect list are not coherent')
            return new_scene_action_dict
        else:
            return False

    @time_tracker('effect_processing_time')
    def action_effect_on_rdf(self, rdf_scene: Graph, debug=False):
        new_graph_list = self.remove_triplets_from_rdf(rdf_scene, debug=debug)
        new_graph_list, sd_rel_action_effect_list = self.add_triplets_to_rdf(new_graph_list, debug=debug)
        return new_graph_list, sd_rel_action_effect_list

    def remove_triplets_from_rdf(self, rdf_scene, debug=False):
        """
        remove the RDF triplet from the graph from d_list
        d_list: Dict {SD_Predicate: [select param 1 (type: string), select param 2 (type: string)]}
        1. map SELECT parameter to RDF subjects/objects-> result: rdf_rel={Predicate:[rdflib subject,rdflib object]}
        2. map RDF subjects/objects to SD_Object instances-> result: sd_rel={Predicate:[SD subject,SD object]}
        3. map SD relation to a RDF Tuple (RDF subject, RDF predicate, RDF object)
        4. remove triplet from graph
        """
        new_graph_list = []
        for select_dict in self.select_dict_list:
            _new_graph = self.rdf_wrapper.copy_rdf_graph(rdf_scene)
            if debug:
                print(f'select_dict: {select_dict}')
                print_graph = self.rdf_wrapper.gen_sd_scene_from_rdf_database(
                    _new_graph
                )
                print(f'print_graph: dlist before: \n {print_graph}')
            for d_dictonary in self.d_list:
                for pred, select_parameters in d_dictonary.items():
                    # Process the select parameters to extract the subject (sub) and object (obj)
                    sub, obj = self.process_select_parameters(select_parameters, select_dict, debug=debug)

                    # Retrieve the predicate URI from sd_rdf_dict
                    predicate_uri = self.rdf_wrapper.sd_rdf_dict.get(pred)

                    if not predicate_uri:
                        raise KeyError(f"Predicate {pred} not found in sd_rdf_dict.")

                    # Create and remove the RDF triplet
                    triplet = (sub, predicate_uri, obj)
                    try:
                        _new_graph = self.rdf_wrapper.remove_triplets(_new_graph, [triplet])
                        if debug:
                            print(f"Deleted RDF triplet: {triplet}")
                    except Exception as e:
                        print(f"Error while removing d_list from current scene: {e}")

            if debug:
                print_graph = self.rdf_wrapper.gen_sd_scene_from_rdf_database(
                    _new_graph
                )
                print(f'print_graph: dlist after == alist before: \n {print_graph}')
            # add new_graph to new_graph_list
            new_graph_list.append(_new_graph)
        return new_graph_list

    def add_triplets_to_rdf(self, new_graph_list, debug=False):
        """
        add the RDF triplet to the graph from a_list
        1. map SELECT parameter to RDF subjects/objects-> result: rdf_rel={Predicate:[rdflib subject,rdflib object]}
        2. map RDF subjects/objects to SD_Object instances-> result: sd_rel={Predicate:[SD subject,SD object]}
        3. map SD relation to a RDF Tuple (RDF subject, RDF predicate, RDF object)
        4. add the triplet to the graph
        """
        sd_rel_action_effect = {}
        sd_rel_action_effect_list = []
        _new_graph_list = []
        # Invert the sd_rdf_dict for direct lookups: {rdf_uri: sd_object}
        rdf_to_sd_dict = {v: k for k, v in self.rdf_wrapper.sd_rdf_dict.items()}

        for select_dict, _new_graph in zip(self.select_dict_list, new_graph_list):
            for a_dictonary in self.a_list:
                for pred, select_parameters in a_dictonary.items():
                    # Process the select parameters to extract the subject (sub) and object (obj)
                    sub, obj = self.process_select_parameters(select_parameters, select_dict, debug=debug)
                    rdf_rel = {pred: [sub, obj]}

                    for sd_pred, rdf_sub_obj in rdf_rel.items():
                        # Directly retrieve the SD objects using the inverted dictionary
                        sd_sub = rdf_to_sd_dict.get(rdf_sub_obj[0])
                        sd_obj = rdf_to_sd_dict.get(rdf_sub_obj[1])

                        if sd_sub is None or sd_obj is None:
                            print(f"Mapping for RDF subject/object not found: {rdf_sub_obj}")
                            continue

                        # Construct sd_rel and the RDF triplet
                        sd_rel = {sd_pred: [sd_sub, sd_obj]}
                        triplet = (rdf_sub_obj[0], self.rdf_wrapper.sd_rdf_dict[sd_pred], rdf_sub_obj[1])

                        # Update the graph and the action effect
                        try:
                            _new_graph = self.rdf_wrapper.add_triplets(_new_graph, [triplet])
                            sd_rel_action_effect.update(sd_rel)
                        except Exception as e:
                            print(f"Error while adding triplet {triplet} to new scene: {e}")

            sd_rel_action_effect_list.append(sd_rel_action_effect)
            sd_rel_action_effect = {}

            if debug:
                print_graph = self.rdf_wrapper.gen_sd_scene_from_rdf_database(_new_graph)
                print(f"print_graph: alist after: \n {print_graph}")

            _new_graph_list.append(_new_graph)

        return [_new_graph_list, sd_rel_action_effect_list]

    def process_select_parameters(self, select_parameters, select_dict, debug=False):
        """
        Recursively process select_parameters to extract subject (sub) and object (obj).

        Args:
            select_parameters (list): The list of parameters to process.
            select_dict (dict): The dictionary containing mappings for SELECT variables.
            debug (bool): Whether to print debug information.

        Returns:
            Tuple: A tuple (sub, obj) representing the processed URIs
            of subject and object depenting from select List.
        """
        sub, obj = None, None

        for item in select_parameters:
            if isinstance(item, list):
                # Recursively process nested lists
                sub, obj = self.process_select_parameters(item, select_dict, debug)
                if sub is not None and obj is not None:
                    break  # Stop processing if valid sub and obj are found
            elif isinstance(item, str):
                if item.startswith("http://") or item.startswith("https://"):
                    sub = self.rdf_wrapper.to_uri(item)
                    obj = select_dict.get(select_parameters[1])
                elif len(select_parameters) >= 1:
                    sub = select_dict.get(select_parameters[0])
                    obj = select_dict.get(select_parameters[1])
                if debug:
                    print(f"Processed item: {item}, sub: {sub}, obj: {obj}")
                break

        return sub, obj

    def query_processing_time(self):
        """processing time of query for checking the preconditions
        Returns (float): self.query_processing_time
        """
        return self.query_processing_time

    def effect_processing_time(self):
        """processing time of effect of action
        Returns (float): self.effect_processing_time
        """
        return self.effect_processing_time

    def execute_processing_time(self):
        """processing time execution: execute = precondition + effect
        Returns (float): self.execute_processing_time
        """
        return self.execute_processing_time


class SDUtils:
    """Utility class for Scene-related operations."""

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
