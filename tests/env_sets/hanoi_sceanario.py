import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)
from sdf.core.sdf_core import SDObject, Scene
from sdf.data.otype import OType 



def hanoi_classic(predicates, actions):
    """
        Peg 1        Peg 2        Peg 3
        --------------------------------
        |            |            |   
        |            |            |   
        |            |            |   
       ===           |            |   
      ======         |            |  
     ========        |            |   
        --------------------------------
        D3 (small)   Empty       Empty
        D2 (med)   
        D1 (large)
    """

    # instantiate sdf objects
    disc1 = SDObject("disc1", OType.DISK)
    disc2 = SDObject("disc2", OType.DISK)
    disc3 = SDObject("disc3", OType.DISK)
    peg1 = SDObject("peg1", OType.PEG)
    peg2 = SDObject("peg2", OType.PEG)
    peg3 = SDObject("peg3", OType.PEG)
    o_clear = SDObject("o_clear", OType.NONE)
    o_not_clear = SDObject("o_not_clear", OType.NONE)

    object_map = {obj.name: obj for obj in [disc1, disc2, disc3, peg1, peg2, peg3, o_clear, o_not_clear]}


    # generate init-scene
    rel_smaller = {
        predicates['smaller']: [
            [disc2, disc1],
            [disc3, disc1],
            [disc3, disc2],
            [disc1, peg1],
            [disc1, peg2],
            [disc1, peg3],
            [disc2, peg1],
            [disc2, peg2],
            [disc2, peg3],
            [disc3, peg1],
            [disc3, peg2],
            [disc3, peg3],
        ]
    }
    rel_is_on = {predicates['is_on']: [[disc1, peg1], [disc2, disc1], [disc3, disc2]]}
    # rel_clear = {clear: [[peg2, True], [peg1, True], [disc1, True]]}
    rel_clear = {predicates['clear']: [[peg2, o_clear], [peg3, o_clear], [disc3, o_clear]]}



    # goal_rel_is_on = {is_on: [[disc3, peg1], [disc2, disc3], [disc1, disc2]]}
    goal_rel_is_on = {predicates['is_on']: [[disc1, peg3], [disc2, disc1], [disc3, disc2]]}
    goal_scene = {**goal_rel_is_on}

    init_scene = {**rel_smaller, **rel_is_on, **rel_clear}
    InitScene = Scene(object_map, init_scene)
    GoalScene = Scene(object_map, goal_scene)

    CurrentScene = InitScene
    return CurrentScene, GoalScene, actions