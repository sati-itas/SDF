from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

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
        object_list: List[SDObject],
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
        self.object_list = object_list

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
            for scene_object in self.object_list:
                if scene_object.name == object_name:
                    return scene_object
                else:
                    counter += 1

        except Exception as e:
            print(
                f'{e}: Exception occured: {object_name} not an member of self.object_list'
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
            for scene_object in self.object_list
            if scene_object.object_type == otype
        ]
        return obj_list


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

    def __repr__(self) -> str:
        return f'action | name={self.name}'

    def check_precondition(self, scene: Scene, debug=False) -> bool:
        """check if action precondition is satisfied in current scene.
        If precondition is satified the function generates:
        a dict (self.select_dict) or a list of dicts (self.select_dict_list) with the possible SELECT variables.

        Args:
            scene (Scene): current scene model
            debug (bool, optional): default to False.

        Returns:
            bool: whether precondition in current scene is satisfied or not.
        """

        self.graph_processing_time = 0.0
        self.query_processing_time = 0.0

        self.select_dict = {}
        self.select_dict_list = []

        # generate rdf data and rdf graph based on scene
        from sdf.core.rdf_wrapper import RDFWrapper

        self.rdf_wrapper = RDFWrapper(scene=scene)
        rdf_graph = self.rdf_wrapper.gen_rdf_graph()
        self.graph_processing_time = self.rdf_wrapper.gen_rdf_graph_processing_time
        
        #self.rdf_wrapper.serialize_rdf_graph(rdf_graph)
        # carry out SPARQL Query
        result = self.rdf_wrapper.query_rdf_graph(rdf_graph, self.precondition)
        self.query_processing_time = self.rdf_wrapper.query_rdf_graph_processing_time

        # if query gives a result
        if len(result.bindings) > 0:
            for row in result:
                self.select_dict = {}
                # if debug:
                #     print(f'result.bindings: {result.bindings}')
                #     print(f'Action.check_precondition(): SPARQL Object={result} \n SPARQL result={row} \n')
                for var in self.select:
                    selected = row[var]
                    # if debug:
                    #     print(f'\t var: {var}, selected: {selected} ')
                    self.select_dict.update({var: selected})
                if debug:
                    print(
                        f'{self.name}.check_precondition(): select_dict={self.select_dict}\n'
                    )
                self.select_dict_list.append(self.select_dict)
            if debug:
                print(f'{self.name}.check_precondition(): scene database: {scene!r}')
                print(
                    f'{self.name}.check_precondition(): self.select_dict_list={self.select_dict_list}\n'
                )
            return True
        else:
            if debug:
                print(f'{self.name}.check_precondition(): precondition not satisfied')
                print(f'scene database: {scene!r}')
            return False

    @time_tracker('effect_execute_processing_time')
    def execute_select_dict_list(self, scene: Scene, debug=False):
        """executes the action in a given scene if possible.
        This includes action precondition checks and generating the follow-up scenes.
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
        # print(f'check precondition of action: {self.name}')
        if self.check_precondition(scene, debug=debug):
            new_graph_list = self.execute_dlist()
            new_graph_list, sd_rel_action_effect_list = self.execute_alist(
                new_graph_list
            )

            # map RDF Database in SD scene
            new_scene_list = []

            for graph in new_graph_list:
                new_scene = self.rdf_wrapper.gen_sd_scene_from_rdf_database(graph)
                new_scene_list.append(new_scene)
            if len(new_scene_list) == len(sd_rel_action_effect_list):
                new_scene_action_dict = dict(
                    zip(new_scene_list, sd_rel_action_effect_list, strict=False)
                )
                # for scene, predcates in new_scene_action_dict.items():
                #     print(f'predcates {predcates}')
                #     print(f'scene {scene}')
            else:
                raise Exception('Error: scene list and effect list are not coherent')
            return new_scene_action_dict
        else:
            return False

    def execute_dlist(self, debug=False):
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
            _new_graph = self.rdf_wrapper.copy_rdf_graph()
            if debug:
                print(f'select_dict: {select_dict}')
                print_graph = self.rdf_wrapper.gen_sd_scene_from_rdf_database(
                    _new_graph
                )
                print(f'print_graph: dlist before: \n {print_graph}')
            for d_dictonary in self.d_list:
                # iterate over all elements in d_list (Dict -> key: predicate, value: list of 2 SELECT parameters)
                # and get the RDF equivalents of their values
                # self.select_dict_list: mapping of SELECT variables to corresponding RDF objects (from SPARQL query)
                for pred, select_parameters in d_dictonary.items():
                    sub, obj = None, None  # Initialize variables
                    # TODO: should be REFACTORED
                    for item in select_parameters:
                        if isinstance(item, list):
                            for nested_item in item:
                                if isinstance(nested_item, str):
                                    sub = select_dict.get(nested_item)
                                    obj = select_dict.get(item[1]) if len(item) > 1 else None
                                    if debug:
                                        print(
                                            f'execute delete: \n\tsubject: {sub}\n\tobject: {obj}\n'
                                        )
                                    break
                        elif isinstance(item, str):
                            if len(item) == 2:
                                sub = select_dict.get(select_parameters[0])
                                obj = select_dict.get(select_parameters[1])
                            # FIX: handle complete URIs in SPARQL
                            elif len(item) > 2:
                                sub = self.rdf_wrapper.to_uri(item)
                                obj = select_dict.get(select_parameters[1])
                            if debug:
                                print(
                                    f'execute delete: \n\tsubject: {sub}\n\tobject: {obj}\n'
                                )
                            break

                    if sub is None or obj is None:
                        raise ValueError(f"Invalid select_parameters: {select_parameters}")

                    rdf_rel = {
                        pred: [sub, obj]
                    }  # rdf_rel: dict = {Predicate:[rdflib subject, rdflib object]}
                    sd_rel = {}

                    # map the RDF subject/object pair of rdf_rel to according SD objects
                    for sd_pred, rdf_sub_obj in rdf_rel.items():
                        # mapping of RDF subjects/objects to SD objects
                        for (
                            mapping_key,
                            mapping_value,
                        ) in self.rdf_wrapper.sd_rdf_dict.items():
                            if rdf_sub_obj[0] == mapping_value:
                                sd_sub = mapping_key
                            if rdf_sub_obj[1] == mapping_value:
                                sd_obj = mapping_key
                        try:
                            # if all SD_Objects were mapped from their RDF subject/object equivilants:
                            # build an according RDF triplet from the SD relation
                            sd_rel = {
                                sd_pred: [sd_sub, sd_obj]
                            }  # sd_rel: dict = {Predicate:[SD subject,SD object]}
                            triplet = self.rdf_wrapper.triplet_from_relation(sd_rel)
                            # generate new graph by removing all mapped triplets from current RDF Database
                            _new_graph = self.rdf_wrapper.remove_triplets(
                                _new_graph, [triplet]
                            )
                            # if debug:
                            #     print(f'delete sd relation: {rel}')
                        except Exception as e:
                            print(
                                f'{e}: Error while removing d_list from current scene'
                            )
            if debug:
                print_graph = self.rdf_wrapper.gen_sd_scene_from_rdf_database(
                    _new_graph
                )
                print(f'print_graph: dlist after == alist before: \n {print_graph}')
            # add new_graph to new_graph_list
            new_graph_list.append(_new_graph)
        return new_graph_list

    def execute_alist(self, new_graph_list, debug=False):
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

        for select_dict, _new_graph in zip(self.select_dict_list, new_graph_list):
            for a_dictonary in self.a_list:
                for pred, select_parameters in a_dictonary.items():
                    sub, obj = None, None  # Initialize variables

                    for item in select_parameters:
                        if isinstance(item, list):
                            for nested_item in item:
                                if isinstance(nested_item, str):
                                    sub = select_dict.get(nested_item)
                                    obj = select_dict.get(item[1]) if len(item) > 1 else None
                                    if debug:
                                        print(
                                            f'execute add: \n\tsubject: {sub}\n\tobject: {obj}\n'
                                        )
                                    break
                        elif isinstance(item, str):
                            if len(item) == 2:
                                sub = select_dict.get(select_parameters[0])
                                obj = select_dict.get(select_parameters[1])
                            # FIX: handle complete URIs in SPARQL
                            elif len(item) > 2:
                                sub = self.rdf_wrapper.to_uri(item)
                                obj = select_dict.get(select_parameters[1])
                            if debug:
                                print(
                                    f'execute add: \n\tsubject: {sub}\n\tobject: {obj}\n'
                                )
                            break
                    if sub is None or obj is None:
                        raise ValueError(f"Invalid select_parameters: {select_parameters}")

                    sd_rel = {}
                    rdf_rel = {pred: [sub, obj]}

                    for sd_pred, rdf_sub_obj in rdf_rel.items():
                        for (
                            mapping_key,
                            mapping_value,
                        ) in self.rdf_wrapper.sd_rdf_dict.items():
                            if rdf_sub_obj[0] == mapping_value:
                                sd_sub = mapping_key
                            if rdf_sub_obj[1] == mapping_value:
                                sd_obj = mapping_key
                        try:
                            sd_rel = {sd_pred: [sd_sub, sd_obj]}
                            triplet = self.rdf_wrapper.triplet_from_relation(sd_rel)
                            sd_rel_action_effect.update(sd_rel)
                            # print(f'sd_rel_action_effect : {sd_rel_action_effect}')
                            # add all triplets from a_list to _new_graph
                            _new_graph = self.rdf_wrapper.add_triplets(
                                _new_graph, [triplet]
                            )
                        except Exception as e:
                            print(f'{e}:Error while adding a_list to new scene')
            sd_rel_action_effect_list.append(sd_rel_action_effect)
            sd_rel_action_effect = {}
            # print(f'sd_rel_action_effect_list : {sd_rel_action_effect_list}')

            if debug:
                print_graph = self.rdf_wrapper.gen_sd_scene_from_rdf_database(
                    _new_graph
                )
                print(f'print_graph: alist after: \n {print_graph}')
            _new_graph_list.append(_new_graph)
        return [_new_graph_list, sd_rel_action_effect_list]

    def graph_processing_time(self):
        """graph_processing_time time of rdf-graph generation
        Returns (float): self.graph_processing_time
        """
        return self.graph_processing_time

    def query_processing_time(self):
        """processing time of query
        Returns (float): self.query_processing_time
        """
        return self.query_processing_time

    def effect_execute_processing_time(self):
        """processing time effect execution
        Returns (float): self.effect_execute_processing_time]
        """
        return self.effect_execute_processing_time
