from typing import Any
from typing import List
from typing import Tuple

from sdf.core.sdf_core import Action
from sdf.core.sdf_core import Scene


class Solver:
    @staticmethod
    def dfs_list(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
    ) -> Tuple[List[Any], bool]:
        """Deep First Search algorithm for finding path between current_scene and goal_scene in
            discrete state transition system (nodes: Scenes, transitions: actions).
            The execution method for actions is execute_select_dict_list().

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible actions

        Returns:
            plan, solution (Tuple[List[Any], bool]): returns a tupel with list of actions and a bool wich indicates if solution was found
        """
        plan = []
        queue = []
        solution = False

        if check_subset_pair(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))

        for action in action_list:
            action.init_action()

        while queue:
            parent_node = queue.pop()  # stack: last-in, first-out
            for action in action_list:
                new_scene_action_dict = action.execute_select_dict_list(
                    parent_node.state, debug=False
                )
                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        # new_node = SearchNode(action, next_scene, parent_node)

                        if check_subset_pair(goal_scene, next_scene):
                            solution = True
                            # path = new_node.path()
                            plan = new_node.act_sequence()
                            return (plan, solution)
                        elif parent_node.in_path(
                            next_scene
                        ):  # pruning rule1: do not consider any path that visits the same state twice
                            pass
                        else:
                            queue.append(new_node)
        return (plan, solution)

    @staticmethod
    def bfs_list(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
    ) -> Tuple[List[Any], bool]:
        """Breadth First Search algorithm for finding path between current_scene and goal_scene in
            discrete state transition system (nodes: Scenes, transitions: actions).
            The execution method for actions is execute_select_dict_list().

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible actions

        Returns:
            List[Action]: plan
        """

        plan = []
        queue = []
        visited = {}
        visited_check = False
        solution = False

        if check_subset_pair(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        for action in action_list:
            action.init_action()

        while queue:
            parent_node = queue.pop(0)  # first-in, first-out

            for action in action_list:
                new_scene_action_dict = action.execute_select_dict_list(
                    parent_node.state, debug=False
                )  # pruning Scenes: which action is executable in Scene, if executable generate Scene

                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        for scene in visited:
                            if check_identical_scenes(next_scene, scene):
                                visited_check = True
                                break
                        if check_subset_pair(goal_scene, next_scene):
                            solution = True
                            plan = new_node.act_sequence()
                            return (plan, solution)
                        elif visited_check:  # pruning rule: do not consider any path that visits a state that you have already visited via some other path.
                            visited_check = False
                            pass
                        else:
                            visited[next_scene] = True
                            queue.append(new_node)
        return (plan, solution)


class SearchNode:
    """Represent each node in the tree as an instance of class SearchNode. For BFS"""

    def __init__(self, action, state, parent=None):
        self.action = action
        self.state = state
        self.parent = parent

    def path(self):
        """returns a sequence of a 2-tubel with action-state pairs"""
        if self.parent is None:
            return [(self.action, self.state)]
        else:
            return [*self.parent.path(), (self.action, self.state)]

    def act_sequence(self):
        """returns a sequence of a action"""
        if self.parent is None:
            return [(self.action)]
        else:
            return [*self.parent.act_sequence(), self.action]

    def in_path(self, state):
        """checks if next state is equal to parent state.
        for pruning reason: do not consider any path that visits the same state twice."""
        if (
            self.state.scene_relations.items() == state.scene_relations.items()
        ):  # check_identical_scenes
            return True
        elif self.parent is None:
            return False
        else:
            return self.parent.in_path(state)


def check_identical_scenes(scene1: Scene, scene2: Scene) -> bool:
    """checks if scene1.scene_relations is equal to scene2.scene_relations
    Args:
        scene1 (Scene): scene 1
        scene2 (Scene): scene 2
    Returns:
        bool: True if scenes are identical
    """
    return scene1.scene_relations.items() == scene2.scene_relations.items()


def check_subset_scenes(goal_scene: Scene, scene: Scene) -> bool:
    """checks if goal_scene.scene_relations is a subset or equal to scene.scene_relations
    Args:
        goal_scene (Scene): goal scene
        scene (Scene): scene
    Returns:
        bool: True if goal_scene.scene_relations is a subset or equal to scene.scene_relations
    """
    return goal_scene.scene_relations.items() <= scene.scene_relations.items()


def check_common_keys(scene1: Scene, scene2: Scene) -> bool:
    common_keys = scene1.scene_relations.keys() & scene2.scene_relations.keys()
    return common_keys


def check_subset_pair(goal: Scene, scene: Scene) -> bool:
    """while with goal.scene_relations.items() <= scene.scene_relations.items() the individual values are compared,
    now the comparison is done in pairs. This corresponds to the pairwise relationship"""
    common_keys = goal.scene_relations.keys() & scene.scene_relations.keys()
    if common_keys:
        for key in common_keys:
            # generate list of tuples
            set1 = {tuple(sublist) for sublist in goal.scene_relations[key]}

            set2 = {tuple(sublist) for sublist in scene.scene_relations[key]}

            # set1 = set(dict1[key])  # TODO:Tupel direkt verwenden
            # set2 = set(dict2[key])  # TODO:Tupel direkt verwenden

            # calculate subset
            # subset = set1.issubset(set2)
            if not set1 <= set2:
                return False
        return True
