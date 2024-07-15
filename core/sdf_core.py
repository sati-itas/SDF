import timeit
from enum import Enum
from enum import unique
from typing import Dict
from typing import List

from rdflib import Graph
from rdflib import Namespace

from core.utility.dict_helper import merge_dicts


@unique
class OType(Enum):
    # TODO: the object type are specific to one domain. idea -> parse an ontology to enable different domain for sdf.
    NONE = 0
    EGO = 1
    LANE = 2
    VEHICLE = 3
    SEGMENT = 4


class Thing:
    '''base class 'Thing' for Object and Predicate class.
    name:str, ident:int are the (unique) key's to each Thing.
    '''

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
    '''Object class for creating dynamic and static objects in scene.

    Args:
        object_name (str): name of the object
        object_type(enum): type of object corresponding to enum in OType class
        position(int): position of object in environment (default=None)
    '''

    def __init__(self, object_name: str, object_type: OType):
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
        return f"object | name={self.name}"  # id: {self.id} object type: {self.object_type}")#\n \

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # TODO change to ident!!
            return self.name == other.name
        else:
            return False

    def __hash__(self):  # This method is necessary to be able to use the class as a key in a dictionary
        return hash(self.id)

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
    '''Predicate class for defining predicates (properties or relations) of single or between several objects

    Args:
        predicate_name (str): name of the object
        ident (int): identification of instance
        o1type (enum): (reference: OType class) for filter reasons
        o2type (enum): (reference: OType class) for filter reasons
    '''

    def __init__(self, predicate_name: str, o1type: OType, o2type: OType):
        Thing.__init__(self, name=predicate_name)
        self.o1type = o1type
        self.o2type = o2type

    def __repr__(self) -> str:
        return f"predicate | name={self.name}, ident={self.id}"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False

    def __hash__(self):  # This method is necessary to be able to use the class as a key in a dictionary
        return hash(self.id)


class Scene(Thing):
    '''Scene class for creating scenes from existing objects and predicates.

    Args:
        object_list ([Object]): list of all existing objects in scene
        scene_relations (Dict): dict of all related objects (key: predicate, value: (nested) list of linked objects)
        ident (int): identification of scene
        predciate_list ([Predicate]) : list of all instanciated predicates between objects in scene
    '''

    def __init__(
        self, object_list: List[SDObject], scene_relations: Dict[Predicate, List[SDObject]], preds: List[Predicate]
    ):
        Thing.__init__(self)
        self.scene_relations = scene_relations
        self.pred_list = preds
        self.object_list = object_list

    def __repr__(self) -> str:
        return f"scene | name={self.name}, ident={self.id}"

    def __str__(self):
        str_to_print = ""
        for key, value in self.scene_relations.items():
            str_to_print = str_to_print + key.name + ":" + " "
            for item in value:
                if not isinstance(item, list):
                    str_to_print = str_to_print + item.name + " "
                if isinstance(item, list):
                    for itemitem in item:
                        str_to_print = str_to_print + itemitem.name + " "
                    str_to_print = str_to_print + "\n"
            str_to_print = str_to_print + "\n"

        return f"scene | name={self.name}, ident={self.id}\n\n{str_to_print}"

    def __hash__(self):  # This method is necessary to be able to use the class as a key in a dictionary
        return hash(self.id)

    def search_relation(self, predicate: Predicate) -> List[SDObject]:
        '''Searching a SDObject in scene_relation with the given predicate and returns SDObject instance

        Args:
            predicate (Predicate): predicate instance

        Returns:
            List[SD_Object]: _description_
        '''
        return self.scene_relations[predicate]

    def search_object(self, object_name: str):
        '''Searching a SDObject in a scene with the given name. Returns the first matching SDObject instance in scene.

        Args:
            object_name (str): name of scene object to be found

        Returns:
            Object: object instance with given name
        '''
        counter = 0
        try:
            for scene_object in self.object_list:
                if scene_object.name == object_name:
                    return scene_object
                else:
                    counter += 1

        except Exception as e:
            print(f'{e}: Exception occured: {object_name} not an member of self.object_list')

    def search_all_individuals_of_class(self, o_type) -> List[SDObject]:
        '''gets all individuals of given class-object

        Args:
            o_type (LITERAL): Literal of OType class to be found

        Returns:
            List[Object]: list of objects with given object type
        '''
        _obj_list = []
        for scene_object in self.object_list:
            if scene_object.object_type == o_type:
                _obj_list.append(scene_object)
        return _obj_list


class Action(Thing):
    '''Action class for defining action template

    Args:
        name (str): action name
        precondition (str): SPARQL query that needs to be fulfilled in scene
        a_list (List[Dict]): List of relations to be added to scene after execution of action
            (key: Predicate instance, value: List of Strings representing selected values from query)
        d_list (List[Dict]): List of scene relations to be removed from scene after execution of action
            (e.g.: {is_on_lane: ["e", "x"]} | key (Predicate) = predicate, value (str) = List of variables representing
            selected values from query)
        select (List[str]): List of Variable names from SPARQL Query (?x etc.)
    '''

    def __init__(self, action_name: str, precondition: str, a_list: List, d_list: List, select: List[str]):
        Thing.__init__(self, name=action_name)
        self.precondition = precondition
        self.a_list = a_list
        self.d_list = d_list
        self.select = select

        # self.graph_processing_time = 0.0
        # self.query_processing_time = 0.0
        # self.effect_execute_processing_time = 0

    def __repr__(self) -> str:
        return f"action | name={self.name}"

    def check_precondition(self, scene: Scene, debug=True) -> bool:
        '''check if precondition is satisfied in current scene

        Args:
            scene (Scene): current scene model

        Returns:
            Bool: whether precondition in current scene is satisfied or not.
        '''

        self.graph_processing_time = 0.0
        self.query_processing_time = 0.0

        self.select_dict = {}

        # generate rdf data and rdf graph based on scene
        start_generate_graph = timeit.default_timer()
        self.Wrapper = RDFWrapper(OType, scene)
        rdf_graph = self.Wrapper.gen_rdf_graph()
        end_generate_graph = timeit.default_timer()
        self.graph_processing_time = end_generate_graph - start_generate_graph

        # carry out SPARQL Query
        start_query = timeit.default_timer()
        result = rdf_graph.query(self.precondition)
        end_query = timeit.default_timer()
        self.query_processing_time = end_query - start_query

        # if query found at least 1 match
        if len(result.bindings) > 0:
            for row in result:
                for var in self.select:
                    selected = row[var]
                    self.select_dict = {**self.select_dict, **{var: selected}}
            # if debug:
            print(f'self.select_dict: {self.select_dict}')
            return True
        else:
            # print("precondition not satisfied")
            return False

    def execute(self, scene: Scene, debug=False):
        '''executes the action in a given scene if possible.
        This includes action precondition checks and generating the follow-up scene.

        Args:
            scene (Scene): scene, in which action shell by executed
            debug (bool, optional): _description_. Defaults to False.

        Raises:
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: Scene: new scene created by executing action
            If preconditions for action not fullfilled return Bool:False
        '''
        self.effect_execute_processing_time = 0.0
        if self.check_precondition(scene, debug=debug):
            start_effect_execute = timeit.default_timer()

            '''
            remove the RDF triplet from the graph from d_list
            d_list: Dict {SD_Predicate: [select param 1 (type: string), select param 2 (type: string)]}
            1. map SELECT parameter to RDF subjects/objects-> result: rdf_rel={Predicate:[rdflib subject,rdflib object]}
            2. map RDF subjects/objects to SD_Object instances-> result: sd_rel={Predicate:[SD subject,SD object]}
            3. map SD relation to a RDF Tuple (RDF subject, RDF predicate, RDF object)
            4. remove triplet from graph
            '''
            for d_dictonary in self.d_list:

                if debug:
                    print("execute: --- delete list:")

                for pred, select_parameters in d_dictonary.items():
                    # iterate over all elements in d_list (Dict -> key: predicate, value: list of 2 SELECT parameters)
                    # and get the RDF equivalents of their values
                    # self.select_dict: mapping of SELECT variables to corresponding RDF objects (from SPARQL query)
                    for item in select_parameters:
                        if not isinstance(item, list):
                            sub = self.select_dict[select_parameters[0]]
                            obj = self.select_dict[select_parameters[1]]
                            if debug:
                                print(f'execute: \n\tsubject: {sub}\n\t object: {obj}\n')
                            break
                        else:
                            for nested_index in item:
                                if not isinstance(nested_index, list):
                                    sub = self.select_dict[item[0]]
                                    obj = self.select_dict[item[1]]
                                    if debug:
                                        print(f'execute: \n\tsubject: {sub}\n\t object: {obj}\n')
                                    break
                    rdf_rel = {pred: [sub, obj]}  # rdf_rel: dict = {Predicate:[rdflib subject, rdflib object]}
                    sd_rel = {}

                    # map the RDF subject/object pair of rdf_rel to according SD objects
                    for sd_pred, rdf_sub_obj in rdf_rel.items():
                        # mapping of RDF subjects/objects to SD objects
                        for mapping_key, mapping_value in self.Wrapper.sd_rdf_dict.items():
                            if rdf_sub_obj[0] == mapping_value:
                                sd_sub = mapping_key
                            if rdf_sub_obj[1] == mapping_value:
                                sd_obj = mapping_key
                        try:
                            # if all SD_Objects were mapped from their RDF subject/object equivilants:
                            # build an according RDF triplet from the SD relation
                            sd_rel = {sd_pred: [sd_sub, sd_obj]}  # sd_rel: dict = {Predicate:[SD subject,SD object]}
                            triplet = self.Wrapper.triplet_from_relation(sd_rel)

                            # remove all mapped triplets from the given d_list from the current RDF Database
                            new_graph = self.Wrapper.remove_triplets_from_rdf_database([triplet])
                        except Exception as e:
                            print(f'{e}: Error while removing d_list from current scene')

            '''
            add the RDF triplet to the graph from a_list
            1. map SELECT parameter to RDF subjects/objects-> result: rdf_rel={Predicate:[rdflib subject,rdflib object]}
            2. map RDF subjects/objects to SD_Object instances-> result: sd_rel={Predicate:[SD subject,SD object]}
            3. map SD relation to a RDF Tuple (RDF subject, RDF predicate, RDF object)
            4. add the triplet to the graph
            '''
            for a_dictonary in self.a_list:

                if debug:
                    print("execute: --- add list:")

                for pred, select_parameters in a_dictonary.items():
                    for item in select_parameters:
                        if not isinstance(item, list):
                            sub = self.select_dict[select_parameters[0]]
                            obj = self.select_dict[select_parameters[1]]
                            if debug:
                                print(f"execute: \n\tsubject: {sub}\n\t object: {obj}\n")
                            break
                        else:
                            for nested_index in item:
                                if not isinstance(nested_index, list):
                                    sub = self.select_dict[item[0]]
                                    obj = self.select_dict[item[1]]
                                    if debug:
                                        print(f"execute: \n\tsubject: {sub}\n\t object: {obj}\n")
                                    break
                    sd_rel = {}
                    rdf_rel = {pred: [sub, obj]}

                    for sd_pred, rdf_sub_obj in rdf_rel.items():
                        for mapping_key, mapping_value in self.Wrapper.sd_rdf_dict.items():

                            if rdf_sub_obj[0] == mapping_value:
                                sd_sub = mapping_key
                            if rdf_sub_obj[1] == mapping_value:
                                sd_obj = mapping_key
                        try:
                            sd_rel = {sd_pred: [sd_sub, sd_obj]}
                            triplet = self.Wrapper.triplet_from_relation(sd_rel)

                            # add all triplets from a_list to current RDF Database
                            new_graph = self.Wrapper.add_triplets_to_rdf_database([triplet])
                        except Exception as e:
                            print(f'{e}:Error while adding a_list to new scene')

            # map RDF Database in SD scene
            new_scene = self.Wrapper.gen_sd_scene_from_rdf_database(new_graph)
            end_effect_execute = timeit.default_timer()
            self.effect_execute_processing_time = end_effect_execute - start_effect_execute
            return new_scene
        else:
            return False

    def graph_processing_time(self):
        '''graph_processing_time time of rdf-graph generation
        Returns (float): self.graph_processing_time
        '''
        return self.graph_processing_time

    def query_processing_time(self):
        '''processing time of query
        Returns (float): self.query_processing_time
        '''
        return self.query_processing_time

    def effect_execute_processing_time(self):
        '''processing time effect execution
        Returns (float): self.effect_execute_processing_time]
        '''
        return self.effect_execute_processing_time


class RDFWrapper:
    '''Wrapper for mapping SD structure to rdf (and vice versa)

    Args:
        object_types (OType class): class holding all enums for object types
        scene (Scene):  scene, whos representation in SD shell by transferred to rdf
    '''

    def __init__(self, object_types, scene: Scene):
        self.object_types = object_types
        self.graph = Graph()
        self.scene = scene
        self.scene_objects = scene.object_list
        self.scene_relation_dict = scene.scene_relations

        self.list_of_triplets = []
        self.rdf_triplet_list = []
        self.namespace_list = []

        self.object_mapping_dict = {}
        self.subject_mapping_dict = {}
        self.predicate_mapping_dict = {}
        self.sd_rdf_dict = {}

    def gen_namespace(self, debug=False) -> List:
        '''generates unique Namespace instances from object and predicate lists

        Args:
            object_types (OType class): ENUM of objects
            objects (list): list of unique objects

        Returns:
            list of rdflib.namespace.Namespace objects: list of unique Namespace objects for rdf
        '''
        for item in self.scene_objects:
            test = Namespace(self.object_types(item.object_type).name + ":")
            if test not in self.namespace_list:
                self.namespace_list.append(test)

        # generate one single predicate Namespace
        self.namespace_list.append(Namespace("predicate:"))

        if debug:
            print(f"\nWrapper.gen_namespace() - generate all rdf namespaces: {self.namespace_list}\n")
            for item in self.namespace_list:
                print(f"\tTyp des Namespace {item}: {type(item)}\n")
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

            # iterate over all generated Namespaces
            for namespace in self.namespace_list:
                if namespace == "predicate:":
                    self.predicate_mapping_dict = {sd_predicate: namespace.term(sd_predicate.name)}
                    # append all mappings of rdf instances with Namespace "predicate:"
                    # to SD Predicate instances to "sd_rdf_dict" mapping dict
                    self.sd_rdf_dict = {**self.sd_rdf_dict, **self.predicate_mapping_dict}

            # iterate over all values (sd_objects) in "scene_relation_dict"
            for objects in sd_value:
                if not isinstance(objects, list):
                    # if value is no nested list
                    sd_subject = sd_value[0]
                    sd_object = sd_value[1]

                    for namespace_item in self.namespace_list:
                        # iterate over namespaces
                        # if namespace name and object type is identical generate rdf item
                        if str(namespace_item) == self.object_types(sd_subject.object_type).name + ":":
                            self.subject_mapping_dict = {
                                sd_subject: namespace_item.term(sd_subject.name)
                            }  # generate rdf item
                            self.sd_rdf_dict = {**self.sd_rdf_dict, **self.subject_mapping_dict}

                        if str(namespace_item) == self.object_types(sd_object.object_type).name + ":":
                            self.object_mapping_dict = {sd_object: namespace_item.term(sd_object.name)}
                            self.sd_rdf_dict = {**self.sd_rdf_dict, **self.object_mapping_dict}

                        if str(namespace_item) == "predicate:":
                            self.predicate_mapping_dict = {sd_predicate: namespace_item.term(sd_predicate.name)}
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
                                if str(namespace_item) == self.object_types(sd_subject.object_type).name + ":":
                                    self.subject_mapping_dict = {sd_subject: namespace_item.term(sd_subject.name)}
                                    self.sd_rdf_dict = {**self.sd_rdf_dict, **self.subject_mapping_dict}

                                if str(namespace_item) == self.object_types(sd_object.object_type).name + ":":
                                    self.object_mapping_dict = {sd_object: namespace_item.term(sd_object.name)}
                                    self.sd_rdf_dict = {**self.sd_rdf_dict, **self.object_mapping_dict}

                                if str(namespace_item) == "predicate:":
                                    self.predicate_mapping_dict = {sd_predicate: namespace_item.term(sd_predicate.name)}
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
            print("\nWrapper.RDFTriplets - generate RDF-triplets from SD_Scene:")
            for item in self.list_of_triplets:
                print(f"\t{item}\n")
            print("\t\tTypes of triplet entries (given example: first triplet):")
            for triplet_item in self.list_of_triplets[0]:
                print(f"\t\t\t{triplet_item}: {type(triplet_item)}\n")
        return self.list_of_triplets

    def gen_rdf_graph(self):
        '''builds up RDF graph from RDF triplets

        Args:
            triplets (list of tuples): RDF triplets (subject, predicate, object)

        Returns:
            rdflib.graph.Graph : RDF ontology
        '''
        self.gen_namespace(debug=False)
        self.gen_rdf_database(debug=False)
        self.rdf_triplets(debug=False)

        for item in self.list_of_triplets:
            self.graph.add(item)
        return self.graph

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

        new_scene = Scene(
            object_list=self.scene.object_list, scene_relations=new_sd_relations, preds=self.scene.pred_list
        )
        return new_scene
