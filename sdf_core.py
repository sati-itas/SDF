from enum import Enum, unique
from typing import List, Dict
from rdflib import Graph, Namespace
from dict_helper import merge_dicts

@unique
class OType(Enum):
    NONE=0
    EGO=1
    LANE=2
    VEHICLE=3
    SEGMENT=4

@unique
class ReferencePosition(Enum):
    UNKNOWN_REF_POS=0
    CENTER = 1
    REAR_MID = 2
    REAR_LEFT = 3
    LEFT_MID = 4
    FRONT_LEFT = 5
    FRONT_MID = 6
    FRONT_RIGHT = 7
    RIGHT_MID = 8
    REAR_RIGHT = 9

@unique 
class MovingDirection(Enum):
    UNKNOWN_MOVING_DIRECTION= 0
    PROBABLE_SAME_DIRECTION = 1
    SAME_DIRECTION = 2
    PROBABLE_OPPOSITE_DIRECTION = 3 
    OPPOSITE_DIRECTION = 4
    PROBABLE_LEFT_TO_RIGHT_CROSSING = 5
    LEFT_TO_RIGHT_CROSSING = 6
    PROBABLE_RIGHT_TO_LEFT_CROSSING = 7
    RIGHT_TO_LEFT_CROSSING = 8

@unique 
class MovingState(Enum):
    UNKNOWN_MOVING_STATE = 0
    PROBABLE_STATIC = 1
    STATIC_OBJ = 2
    PROBABLE_DYNAMIC = 3
    DYNAMIC = 4
    MOVABLE = 5

# SDL
class Thing:
    """base class 'Thing' for Object and Predicate class.
    name:str, ident:int are the (unique) key's to each Thing.
    """
    #TODO name:str, ident:int should be unique and to each name belongs one identification number (ident).
    #TODO But than action and scene class are not able to use name and ident
    def __init__(self, name=None, ident=None):
        self.name=name
        self.ident=ident

class SDL_Object(Thing):
    """Object class for creating dynamic and static objects in scene. 

    Args:
        object_name (str): name of the object 
        object_type(enum): type of object corresponding to enum in OType class 
        position(int): position of object in environment (default=None)
    """
    def __init__(self, object_name:str, object_ident:int , object_type=OType.EGO.value):
        self.object_type=object_type
        Thing.__init__(self, name=object_name, ident=object_ident)

        self.course_angle=None
        self.object_length=None
        self.object_width=None

        self.RelPos_x=None
        self.RelPos_y=None
        self.RelPos_z=None

        self.RelAcc=None
        self.RelAcc_x=None
        self.RelAcc_y=None
        self.RelAcc_z=None

        self.AbsSpeed=None
        self.AbsSpeed_x=None
        self.AbsSpeed_y=None
        self.AbsSpeed_z=None

        self.RelSpeed=None
        self.RelSpeed_x=None
        self.RelSpeed_y=None
        self.RelSpeed_z=None

        self.MovingDirection=None
        self.MovingState=None
        self.RefPos=None

        self.YawRate=None
        self.Vel_x=None
        self.Vel_y=None
        self.Acc_x=None
        self.Acc_y=None

    def __repr__(self)->str:
        return (f"name: {self.name}")#\nid: {self.ident}\nobject type: {self.object_type}")#\n \
                # ---\n \
                # optional attributes:\n \
                # course_angle={self.course_angle}\n \
                # object_length={self.object_length}\n \
                # object_width={self.object_width}\n \
                # RelPos_x={self.RelPos_x}\n \
                # RelPos_y={self.RelPos_y}\n \
                # RelPos_z={self.RelPos_z}\n \
                # RelAcc={self.RelAcc}\n \
                # RelAcc_x={self.RelAcc_x}\n \
                # RelAcc_y={self.RelAcc_y}\n \
                # RelAcc_z={self.RelAcc_z}\n \
                # AbsSpeed={self.AbsSpeed}\n \
                # AbsSpeed_x={self.AbsSpeed_x}\n \
                # AbsSpeed_y={self.AbsSpeed_y}\n \
                # AbsSpeed_z={self.AbsSpeed_z}\n \
                # RelSpeed={self.RelSpeed}\n \
                # RelSpeed_x={self.RelSpeed_x}\n \
                # RelSpeed_y={self.RelSpeed_y}\n \
                # RelSpeed_z={self.RelSpeed_z}\n \
                # MovingDirection={self.MovingDirection}\n \
                # MovingState={self.MovingState}\n \
                # RefPos={self.RefPos}\n \
                # YawRate={self.YawRate}\n \
                # Vel_x={self.Vel_x}\n \
                # Vel_y={self.Vel_y}\n \
                # Acc_x={self.Acc_x}\n \
                # Acc_y={self.Acc_y}")
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False
        
    def __hash__(self):  # Diese Methode ist notwendig, um die Klasse als Schlüssel in einem Wörterbuch verwenden zu können
        return hash(self.ident)

    def add_rel_speed(self, RelSpeed): self.RelSpeed=RelSpeed
    def add_rel_speed_x(self, RelSpeed_x): self.RelSpeed_x=RelSpeed_x
    def add_rel_speed_y(self, RelSpeed_y): self.RelSpeed_y=RelSpeed_y
    def add_rel_speed_z(self, RelSpeed_z): self.RelSpeed_z=RelSpeed_z

    def add_abs_speed(self, AbsSpeed): self.AbsSpeed=AbsSpeed
    def add_abs_speed_x(self, AbsSpeed_x): self.AbsSpeed_x=AbsSpeed_x
    def add_abs_speed_y(self, AbsSpeed_y): self.AbsSpeed_y=AbsSpeed_y
    def add_abs_speed_z(self, AbsSpeed_z): self.AbsSpeed_y=AbsSpeed_z

    def add_rel_acc(self, RelAcc): self.RelAcc=RelAcc
    def add_rel_acc_x(self, RelAcc_x): self.RelAcc_x=RelAcc_x
    def add_rel_acc_y(self, RelAcc_y): self.RelAcc_y=RelAcc_y
    def add_rel_acc_z(self, RelAcc_z): self.RelAcc_z=RelAcc_z

    def add_rel_pos_x(self, RelPos_x): self.RelPos_x=RelPos_x
    def add_rel_pos_y(self, RelPos_y): self.RelPos_y=RelPos_y
    def add_rel_pos_z(self, RelPos_z): self.RelPos_z=RelPos_z

    def add_moving_direction(self, moving_direction): self.MovingDirection=moving_direction
    def add_moving_state(self, moving_state): self.MovingState=moving_state
    def add_ref_pos(self, ref_pos): self.RefPos=ref_pos

    def add_yaw_rate(self, yaw_rate): self.YawRate=yaw_rate
    def add_vel_x(self, vel_x): self.Vel_x=vel_x
    def add_vel_y(self, vel_y): self.Vel_y=vel_y
    def add_acc_x(self, acc_x): self.Acc_x=acc_x
    def add_acc_y(self, acc_y): self.Acc_y=acc_y

# class Object(Thing):
#     """Object class for creating dynamic and static objects in scene. 

#     Args:
#         object_name (str): name of the object 
#         object_type(enum): type of object corresponding to enum in OType class 
#         position(int): position of object in environment (default=None)
#     """
#     def __init__(self, object_name:str, object_type=OType.EGO.value, position=None): 
#         self.object_type=object_type
#         self.position=position
#         Thing.__init__(self, name=object_name)

class Predicate(Thing):
    """Predicate class for defining predicates (properties or relations) of single or between several objects
    
    Args:
        predicate_name (str): name of the object 
        ident (int): identification of instance 
        o1type (enum): Type of object1. Distinguish only between object types (reference: OType class) for filter reasons
        o2type (enum): Type of object2. Distinguish only between object types (reference: OType class) for filter reasons
    """
    def __init__(self, predicate_name:str, predicate_ident:int, o1type=OType.EGO.value, o2type=OType.LANE.value):
        Thing.__init__(self, name=predicate_name, ident=predicate_ident)
        self.o1type=o1type
        self.o2type=o2type

    def __repr__(self) -> str:
        return (f"predicate name:{self.name}")#\nident={self.ident}\nobject 1 type: {self.o1type}\nobject 2 type: {self.o2type}")
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.ident == other.ident
        else:
            return False
        
    def __hash__(self):  # Diese Methode ist notwendig, um die Klasse als Schlüssel in einem Wörterbuch verwenden zu können
        return hash(self.ident)

class Scene(Thing): 
    """Scene class for creating scene from existing objects and predicates. 

    Args: 
        object_list ([Object]): list of all existing objects in scene 
        scene_relations (Dict): dict of all related objects (key: predicate, value: (nested) list of linked objects)
        ident (int): identification of scene
        predciate_list ([Predicate]) : list of all instanciated predicates between objects in scene 
    """
    def __init__(self, object_list:List[SDL_Object], scene_relations:Dict[Predicate,List[SDL_Object]], preds:List[Predicate], scene_ident:int):
        Thing.__init__(self, ident=scene_ident)
        self.scene_relations=scene_relations
        self.pred_list=preds
        self.object_list=object_list

    def __str__(self):
        str_to_print=""
        for key, value in self.scene_relations.items():
            str_to_print=str_to_print+key.name+":"+" "
            for item in value:
                if not isinstance(item, list): 
                    str_to_print=str_to_print+ item.name+" "
                if isinstance(item, list): 
                    for itemitem in item:
                        str_to_print=str_to_print+itemitem.name+" "
                    str_to_print=str_to_print+"\n"
            str_to_print=str_to_print+"\n"

        return f"{str_to_print}"
    
    def search_relation(self, predicate:Predicate) -> List[SDL_Object]:
        """Search an SDL Objects with the given predicate and returns SDL Objects

        Args:
            predicate (Predicate): predicate instance 

        Returns:
            List[SDL_Object]: _description_
        """
        return self.scene_relations[predicate]

    def search_object(self, object_name:str) -> SDL_Object:
        """Search an Object in the Ontology with the given name and returns the first matching Object

        Args:
            object_name (str): name of scene object to be found 

        Returns:
            Object: object instance with given name
        """
        counter=0
        for scene_object in self.object_list:
            if scene_object.name==object_name:
                return scene_object
            else:
                counter+=1
        if counter==len(self.object_list):
            return None 
    
    def search_all_individuals_of_class(self, o_type)->List[SDL_Object]:
        """gets all individuals of given class-object

        Args:
            o_type (LITERAL): Literal of OType class to be found 

        Returns:
            List[Object]: list of objects with given object type
        """
        _obj_list=[]
        for scene_object in self.object_list:
            if scene_object.object_type==o_type:
                _obj_list.append(scene_object)
        return _obj_list

class Action(Thing):
    """Action class for defining action template (reference: STRIPS and PDDL)

    Args:
            name (str): action name
            precondition (SPARQL query): SPARQL query that needs to be fulfilled in scene
            a_list: add list (relations that become true by executing)
            d_list: delete list (relations that are no longer true after execution) 
            select: variable list of queried objects (?x etc.) 
    """
    def __init__(self, action_name:str, precondition:str, a_list:List, d_list:List, select:List[str]):
        Thing.__init__(self, name=action_name)
        self.precondition=precondition
        self.a_list=a_list
        self.d_list=d_list
        self.select=select

    def __repr__(self) -> str:
        return (f"\n #action name: {self.name}\n\
                #preconditions: {self.precondition}\n\
                #add list: {self.a_list}\n\
                #delete list: {self.d_list}\n")

    def check_precondition(self, scene:Scene, debug=False)->bool:
        """check if precondition is satisfied in current scene

        Args:
            scene (Scene): current scene model
            select (List[str]): List of Variable names from SPARQL Query

        Returns:
            Bool: whether precondition is satisfied in current scene or not 
        """
        self.Wrapper=RDF_Wrapper(OType, scene)
        self.select_dict={}
        
        namesp_list=self.Wrapper.gen_namespace(objects=scene.object_list)
        if debug:
            print("-------check precondition-------\n")
            print(f"\nWrapper.gen_namespace() - generate all RDF namespaces: {namesp_list}\n")
            for item in namesp_list:
                print(f"\tTyp des Namespace {item}: {type(item)}\n")

        sdl_rdf_dict=self.Wrapper.generateRDFDatabase()
        if debug:
            print(f"\nWrapper.generateRDFDatabase() - mapping SDL to RDF. Key=SDL - Value=RDF\n")
            for key, value in sdl_rdf_dict.items():
                try:
                    print(f"\tKeyName: {key.name} Value: {value}\n")
                except:
                    print(f"\tKeyName: {key.name} Value: {value}\n")

        list_of_triplets=self.Wrapper.RDFTriplets()
        if debug:
            print(f"\nWrapper.RDFTriplets - generate RDF-Triplets from SDL_Scene:")
            for item in list_of_triplets:
                print(f"\t{item}\n")
            print(f"\t\tTypes of triplet entries (given example: first triplet):")
            for triplet_item in list_of_triplets[0]:
                print(f"\t\t\t{triplet_item}: {type(triplet_item)}\n")

        graph=self.Wrapper.RDF_graph()
        if debug:
            print("\nWrapper.RDF_graph() - generate RDF-Graph from RDF triplet list (serialized): {}".format(graph.serialize(format="turtle")))

        # carry out SPARQL Query
        result = graph.query(self.precondition)

        # if query found at least 1 match 
        if len(result.bindings) > 0:
            #print("precondition satisfied")
            for row in result:
                for var in self.select:
                    selected=row[var]
                    self.select_dict={**self.select_dict, **{var: selected}}
            return True
        else:  
            #print("precondition not satisfied")
            return False

    def execute(self, scene:Scene, debug = False):
        """_summary_

        Args:
            scene (Scene): scene, in which action shell by executed
            objects (List[Object]): list of all objects in scene 
            a_list (List[Dict]): List of relations to be added to scene after execution of action (key: Predicate instance, value: List of Strings representing selected values from query)
            d_list (List[Dict]): List of relations to be removed from scene after execution of action (key: Predicate instance, value: List of Strings representing selected values from query)

        Returns:
            Scene: new scene created by executing action | If preconditions for action not fullfilled return Bool:False
        """
        if self.check_precondition(scene, debug=debug):
            for item in self.d_list:
                if debug:
                    print("execute: --- delete list:")
                # item: Dict {is_on: ["e","l1"]}
                for key, value in item.items():
                    for index in value:
                        # iterate over all value entries in "item" Dict and look for RDF equivalents of value elemets in self.select_dict
                        # self.select_dict: allocation of SELECT variables from SPARLQ Queries to corresponding / found RDF objects  
                        if not isinstance(index, list):
                            sub=self.select_dict[value[0]]
                            obj=self.select_dict[value[1]]
                            if debug:
                                print(f"execute: \n\tsubject: {sub}\n\t object: {obj}\n")
                            break
                        else:
                            for nested_index in index:
                                if not isinstance(nested_index, list):
                                    sub=self.select_dict[index[0]]
                                    obj=self.select_dict[index[1]]
                                    if debug:
                                        print(f"execute: \n\tsubject: {sub}\n\t object: {obj}\n")
                                    break

                    # rdf_rel: Dict key: SDL Predicate, value: List of RDF Objects/Subjects
                    rdf_rel={key:[sub, obj]}
                    sdl_rel={}

                    for key, item in rdf_rel.items():
                        # mapping of RDF subjects/objects to SDL objects
                        sdl_pred=key
                        for mapping_key, mapping_value in self.Wrapper.sdl_rdf_dict.items():
                            if item[0]==mapping_value:
                                sdl_sub=mapping_key
                            if item[1]==mapping_value:
                                sdl_obj=mapping_key
                        try:
                            # if all SDL subjects and objects were mapped from RDF subjects/objects: build RDF Triplets from SDL relations
                            sdl_rel={sdl_pred:[sdl_sub, sdl_obj]}
                            #print(f"SDL Relation: {sdl_rel}")
                            Triplet=self.Wrapper.Triplet_from_relation(sdl_rel)

                            # remove all Triplets from given d_list in current RDF Database 
                            new_graph=self.Wrapper.remove_Triplets_from_RDFDatabase([Triplet])
                        except: 
                            raise Exception("Error while removing d_list from current scene")            

            for item in self.a_list:
                if debug:
                    print("execute: --- add list:")
                # same procedure as with d_list
                for key, value in item.items():
                    for index in value:
                        if not isinstance(index, list):
                            sub=self.select_dict[value[0]]
                            obj=self.select_dict[value[1]]
                            if debug:
                                print(f"execute: \n\tsubject: {sub}\n\t object: {obj}\n")
                            break    
                        else: 
                            for nested_index in index:
                                if not isinstance(nested_index, list):
                                    sub=self.select_dict[index[0]]
                                    obj=self.select_dict[index[1]]
                                    if debug:
                                        print(f"execute: \n\tsubject: {sub}\n\t object: {obj}\n")
                                    break
                    sdl_rel={}
                    rdf_rel={key:[sub, obj]}

                    for key, item in rdf_rel.items():
                        sdl_pred=key
                        for mapping_key, mapping_value in self.Wrapper.sdl_rdf_dict.items():

                            if item[0]==mapping_value:
                                sdl_sub=mapping_key
                            if item[1]==mapping_value:
                                sdl_obj=mapping_key
                        try:
                            sdl_rel={sdl_pred:[sdl_sub, sdl_obj]}
                            Triplet=self.Wrapper.Triplet_from_relation(sdl_rel)

                            # add all Triplets from a_list to current RDF Database
                            new_graph=self.Wrapper.add_Triplets_to_RDFDatabase([Triplet])
                        except: 
                            raise Exception("Error while adding a_list to new scene")            

            # mapp RDF Database in SDL scene
            new_scene=self.Wrapper.gen_SDL_scene_from_RDF_Database(new_graph)

            return new_scene
        else:
            return False


class RDF_Wrapper:
    """Wrapper for mapping SDL structure to RDF (and vice versa)

    Args: 
        object_types (OType class): class holding all enums for object types 
        scene (Scene):  scene, whos representation in SDL shell by transferred to RDF
    """
    def __init__(self, object_types, scene:Scene):
        self.object_types=object_types
        self.graph=Graph()
        self.scene=scene
        self.scene_dict=self.scene.scene_relations

        self.list_of_triplets=[]
        self.rdf_triplet_list=[]
        self.namespace_list=[]

        self.object_mapping_dict={}
        self.subject_mapping_dict={}
        self.predicate_mapping_dict={}
        self.sdl_rdf_dict={}

    def gen_namespace(self, objects):
        """generates unique Namespace instances from object and predicate lists

        Args:
            object_types (OType class): ENUM of objects
            objects (list): list of unique objects 

        Returns:
            list of rdflib.namespace.Namespace objects: list of unique Namespace objects for RDF
        """
        for item in objects:
            test=Namespace(self.object_types(item.object_type).name+":")
            if test not in self.namespace_list:
                self.namespace_list.append(test)
        
        # generate one single predicate Namespace
        self.namespace_list.append(Namespace("predicate:"))

        return self.namespace_list

    def generateRDFDatabase(self):
        """mapping all SDL relations in RDF triplets 

        Args:
            scene_dict (_type_): list of rdf triplets 
        """

        #iterate over all relations in current scene
        for key, value in self.scene_dict.items():
            # "scene_dict" architecture: key=Predicate, value=(nested) List of SDL Object instances 
            sdl_predicate = key
            
            # iterate over all generated Namespaces
            for namespace in self.namespace_list:
                if namespace =="predicate:":
                    self.predicate_mapping_dict = {sdl_predicate: namespace.term(sdl_predicate.name)}
                    # append all mappings of RDF instances with Namespace "predicate:" with SDL Predicate instances to "sdl_rdf_dict" mapping dict
                    self.sdl_rdf_dict = {**self.sdl_rdf_dict,** self.predicate_mapping_dict}
            
            for value_item in value:
                # iterate over all value items in "scene_dict"
                if not isinstance(value_item, list):
                    # if value is no nested list
                    sdl_subject = value[0]
                    sdl_object = value[1]

                    for item in self.namespace_list:
                        # iterate over all Namespaces
                        if str(item) == self.object_types(sdl_object.object_type).name+":":
                            # if Namespace name and object type of second entry in value are identical
                            # generate RDF item and append mapping of RDF item and second value entry to "sdl_rdf_dict" 
                            self.object_mapping_dict = {sdl_object: item.term(sdl_object.name)}
                            self.sdl_rdf_dict = {**self.sdl_rdf_dict,** self.object_mapping_dict}

                        if str(item) == self.object_types(sdl_subject.object_type).name+":" :
                            # if Namespace name and object type of second entry in value are identical
                            # generate RDF item and append mapping of RDF item and first value entry to "sdl_rdf_dict" 
                            self.subject_mapping_dict = {sdl_subject: item.term(sdl_subject.name)}
                            self.sdl_rdf_dict = {**self.sdl_rdf_dict, **self.subject_mapping_dict}

                        if str(item) == "Predicate:":
                            # if Namespace is "Predicate:"
                            # generate RDF item and append mapping of RDF item and key from "scene_dict" to "sdl_rdf_dict" 
                            self.predicate_mapping_dict = {sdl_predicate: item.term(sdl_predicate.name)}
                            self.sdl_rdf_dict = {**self.sdl_rdf_dict, **self.predicate_mapping_dict}
        
                elif isinstance(value_item, list):
                    # if value is nested list
                    for index in range(len(value_item)): 
                        # iterate over all nested lists
                        sdl_subject = value_item[0]
                        sdl_object = value_item[1]

                        # same as above but one hierarchy level further down (not value[0] or value[0] but value[...][0] and value[...][1])
                        for item in self.namespace_list:
                            if str(item) == self.object_types(sdl_object.object_type).name+":":
                                self.object_mapping_dict = {sdl_object: item.term(sdl_object.name)}
                                self.sdl_rdf_dict = {**self.sdl_rdf_dict,** self.object_mapping_dict}

                            if str(item) == self.object_types(sdl_subject.object_type).name+":" :
                                self.object_mapping_dict = {sdl_object.name: item.term(sdl_object.name)}
                                self.subject_mapping_dict = {sdl_subject: item.term(sdl_subject.name)}
                                self.sdl_rdf_dict = {**self.sdl_rdf_dict, **self.subject_mapping_dict}

                            if str(item) == "Predicate:":
                                self.predicate_mapping_dict = {sdl_predicate: item.term(sdl_predicate.name)}
                                self.sdl_rdf_dict = {**self.sdl_rdf_dict, **self.predicate_mapping_dict}

        return self.sdl_rdf_dict

    def RDFTriplets(self):
        """Generating RDF Triplets from scene dict, Namespaces and Database

        Returns:
            List of Tuples: List of RDF Triplets
        """

        # iterate over all SDL relations in current scene
        for sdl_key, sdl_value in self.scene_dict.items():
                sdl_predicate=sdl_key

                for item in sdl_value: 
                    
                    if not isinstance(item, list):
                        # if value is no nested list
                        sdl_subject=sdl_value[0]
                        sdl_object=sdl_value[1]

                        # take value entries and find equivilants in "sdl_rdf_dict"
                        for rdf_key, rdf_value in self.sdl_rdf_dict.items():
                            if rdf_key==sdl_predicate:
                                rdf_predicate=self.sdl_rdf_dict[sdl_predicate]
                            if rdf_key==sdl_subject:
                                rdf_subject=self.sdl_rdf_dict[sdl_subject]
                            if rdf_key==sdl_subject:
                                rdf_object=self.sdl_rdf_dict[sdl_object]

                        triple=(rdf_subject, rdf_predicate, rdf_object)

                        # if triple is not already in "list_of_triplets": append it  
                        if triple not in self.list_of_triplets:
                            self.list_of_triplets.append(triple)
                        break

                    else: 
                        # if value is nested list

                        for item_item in item: 
                            # same as above but one hierarchy level further down (instead of sdl_value[0] and sdl_value[1]: sdl_value[...][0] and sdl_value[...][1])
                            if not isinstance(item_item, list):
                                sdl_subject=item[0]
                                sdl_object=item[1]
                                # hier: triple als SDL -> finde RDF Äquivalent
                                for rdf_key, rdf_value in self.sdl_rdf_dict.items():
                                    if rdf_key==sdl_predicate:
                                        rdf_predicate=self.sdl_rdf_dict[sdl_predicate]
                                    if rdf_key==sdl_subject:
                                        rdf_subject=self.sdl_rdf_dict[sdl_subject]
                                    if rdf_key==sdl_subject:
                                        rdf_object=self.sdl_rdf_dict[sdl_object]
                                triple=(rdf_subject, rdf_predicate, rdf_object)
                                if triple not in self.list_of_triplets:
                                    self.list_of_triplets.append(triple)
                                break

        return self.list_of_triplets

    def RDF_graph(self):
        """builds up RDF ontology from RDF triplets

        Args:
            triplets (list of tuples): RDF triplets (subject, predicate, object) 

        Returns:
            rdflib.graph.Graph : RDF ontology
        """

        for item in self.list_of_triplets:
            self.graph.add(item)
        return self.graph   

    def map_RDFObject_to_SDLObject(self, rdf_obj): 
        """maps given RDF object from database to SDL object from given scene

        Args:
            rdf_obj (RDF URI): RDF entity from Namespace

        Returns:
            Object: object instance equivilant of given RDF object  
        """
        for key, value in self.scene_dict.items():
            if value==rdf_obj:
                return key
 
    def remove_Triplets_from_RDFDatabase(self, d_list):
        for triplet in d_list: 
            self.graph.remove(triplet)
        return self.graph

    def add_Triplets_to_RDFDatabase(self, a_list):
        for tuple in a_list:
            self.graph.add(tuple)
        return self.graph

    def Triplet_from_relation(self, relation):
        """generates RDF Triplet from single SDL relation 

        Args:
            relation (Dict): Relation based on SDL Objects and Predicates 

        Returns:
            RDF Triplet
        """
        for sdl_rel_key, sdl_rel_value in relation.items():
            for mapping_key, mapping_value in self.sdl_rdf_dict.items():
                if sdl_rel_key==mapping_key:
                    pre=mapping_value
                if sdl_rel_value[0]==mapping_key:
                    sub=mapping_value
                if sdl_rel_value[1]==mapping_key:
                    obj=mapping_value

            triplet=(sub, pre, obj)
            return triplet

    def gen_SDL_scene_from_RDF_Database(self, new_graph) -> Scene:
        """generates new SDL scene from manipulated RDF Database (action manipulates RDF Database directly but not SDL scene). New SDL scene has to be generated based on RDF Database

        Args:
            new_graph (rdflib.graph.Graph): new RDF Database

        Returns:
            Scene: new SDL Scene
        """

        new_sdl_relations={}
        for triplet in new_graph:
            #print(f"Triplet: {triplet}")
            for key, value in self.sdl_rdf_dict.items():
                if triplet[0]==value: 
                    new_sub=key
                if triplet[1]==value:
                    new_pred=key
                if triplet[2]==value:
                    new_obj=key
            try:
                new_sdl_relations=merge_dicts(new_sdl_relations, {new_pred:[new_sub, new_obj]})
            except:
                raise Exception("Error while creating new SDL scene relations")

        new_scene=Scene(object_list=self.scene.object_list, scene_relations=new_sdl_relations, preds=self.scene.pred_list, scene_ident=...)
        return new_scene