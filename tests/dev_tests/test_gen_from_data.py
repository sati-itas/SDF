import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)

from sdf.core.gen_data import DataGenerator


def test_gen():
    generator = DataGenerator('test_scene.ttl')

    ##########
    py_file_otypes = 'domain_otypes'
    class_domain_type = 'DomainTypes'
    Dtype = generator.gen_enum_types(class_domain_type, py_file_otypes, True)
    print(Dtype.LANETYPE.value)
    print(Dtype.LANETYPE.name)
    print(Dtype.LANETYPE.value('biking'))

    dtype = generator.gen_types(class_domain_type)
    print(dtype)
    
    ##########
    py_file_scenery = 'domain_scenery'
    class_scenery = 'Scenery'
    Scenery = generator.gen_enum_types(class_scenery, py_file_scenery, True)
    print(Scenery.LANESEGMENT.value)

    scenery = generator.gen_types(class_scenery)
    print(scenery)

    ##########
    py_file_location = 'domain_location'
    class_location = 'Location'
    Location = generator.gen_enum_types(class_location, py_file_location, True)
    print(Location.LANEASSIGNMENT.value)

    location = generator.gen_types(class_location)
    print(location)

    ##########
    py_file_dyn_object = 'domain_dyn_object'
    class_dyn_object = 'DynamicObject'
    DynamicObject = generator.gen_enum_types(class_dyn_object, py_file_dyn_object, True)
    print(DynamicObject.OBSTACLE.value)

    dyn_object = generator.gen_types(class_dyn_object)
    print(dyn_object)

    ##########
    py_file_self = 'domain_self'
    class_self = 'SelfRepresentation'
    SelfRepresentation = generator.gen_enum_types(class_self, py_file_self, True)
    print(SelfRepresentation.EGO.value)

    self = generator.gen_types(class_self)
    print(self)

    ##########
    predicates_list = 'gen_pred_list.txt'
    predicate_dict = generator.gen_predicates(predicates_list)
    print(predicate_dict)

def enum_gen():
    generator = DataGenerator('test_scene.ttl')

    ##########
    py_file_otypes = 'domain_otypes'
    class_domain_type = 'DomainTypes'
    generator.gen_enum_types(class_domain_type, py_file_otypes)
    
    ##########
    py_file_scenery = 'domain_scenery'
    class_scenery = 'Scenery'
    generator.gen_enum_types(class_scenery, py_file_scenery)

    ##########
    py_file_location = 'domain_location'
    class_location = 'Location'
    generator.gen_enum_types(class_location, py_file_location)

    ##########
    py_file_dyn_object = 'domain_dyn_object'
    class_dyn_object = 'DynamicObject'
    generator.gen_enum_types(class_dyn_object, py_file_dyn_object)

    ##########
    py_file_self = 'domain_self'
    class_self = 'SelfRepresentation'
    generator.gen_enum_types(class_self, py_file_self)




if __name__ == "__main__":
    test_gen()
    # enum_gen()
