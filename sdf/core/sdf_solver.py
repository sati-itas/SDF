from typing import Any
from typing import List
from typing import Tuple

from rdflib import Graph

from sdf.core.rdf_wrapper import RDFUtils
from sdf.core.sdf_core import Action
from sdf.core.sdf_core import Scene
from sdf.core.sdf_core import SDUtils


class Solver:
    @staticmethod
    def dfs_sdscene(
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

        if SDUtils.check_subset_pair(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))

        for action in action_list:
            action.init_action()

        while queue:
            parent_node = queue.pop()  # stack: last-in, first-out
            for action in action_list:
                new_scene_action_dict = action.execute_action_on_sdscene(
                    parent_node.state, debug=False
                )
                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        # new_node = SearchNode(action, next_scene, parent_node)

                        if SDUtils.check_subset_pair(goal_scene, next_scene):
                            solution = True
                            # path = new_node.path()
                            plan = new_node.act_sequence()
                            return (plan, solution)
                        elif parent_node.in_path(next_scene, SDUtils.check_identical_scenes
                        ):  # pruning rule1: do not consider any path that visits the same state twice
                            pass
                        else:
                            queue.append(new_node)
        return (plan, solution)

    @staticmethod
    def bfs_sdscene(
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

        if SDUtils.check_subset_pair(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        for action in action_list:
            action.init_action()

        while queue:
            parent_node = queue.pop(0)  # first-in, first-out

            for action in action_list:
                new_scene_action_dict = action.execute_action_on_sdscene(
                    parent_node.state, debug=False
                )  # pruning Scenes: which action is executable in Scene, if executable generate Scene

                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        for scene in visited:
                            if SDUtils.check_identical_scenes(next_scene, scene):
                                visited_check = True
                                break
                        if SDUtils.check_subset_pair(goal_scene, next_scene):
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

    @staticmethod
    def initialize_rdf(
        current_scene: Scene, goal_scene: Scene, action_list: List[Action]
    ) -> Tuple[Graph, Graph]:
        # Initialize RDF graphs for current and goal scenes
        current_scene_rdf_wrapper = current_scene.init_rdf_wrapper()
        current_scene_rdf_graph = current_scene_rdf_wrapper.graph

        goal_rdf_wrapper = goal_scene.init_rdf_wrapper()
        goal_rdf_graph = goal_rdf_wrapper.graph

        # Initialize actions with the current scene's RDF wrapper
        for action in action_list:
            action.init_action_with_rdf(current_scene_rdf_wrapper)

        return goal_rdf_graph, current_scene_rdf_graph

    @staticmethod
    def dfs_rdf(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
    ) -> Tuple[List[Any], bool]:
        """Deep First Search algorithm for finding path between current_scene and goal_scene in
            discrete state transition system (nodes: Scenes, transitions: actions).

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

        # Init RDF graphs from current and goal scene
        goal_scene, current_scene = Solver.initialize_rdf(current_scene, goal_scene, action_list)

        if RDFUtils.is_subset(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))

        while queue:
            parent_node = queue.pop()  # stack: last-in, first-out
            for action in action_list:
                new_rdf_scene_action_dict = action.execute_action_on_rdf(
                    parent_node.state, debug=False
                )
                if new_rdf_scene_action_dict:
                    for next_rdf_scene, action_eff in new_rdf_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_rdf_scene, parent_node
                        )
                        # new_node = SearchNode(action, next_scene, parent_node)

                        if RDFUtils.is_subset(goal_scene, next_rdf_scene):
                            solution = True
                            # path = new_node.path()
                            plan = new_node.act_sequence()
                            return (plan, solution)
                        elif parent_node.in_path(next_rdf_scene, RDFUtils.is_equal
                        ):  # pruning rule1: do not consider any path that visits the same state twice
                            pass
                        else:
                            queue.append(new_node)
        return (plan, solution)

    @staticmethod
    def bfs_rdf(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
    ) -> Tuple[List[Any], bool]:
        """Breadth First Search algorithm for finding path between current_scene and goal_scene in
            discrete state transition system (nodes: Scenes, transitions: actions).

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
        #Init RDF graphs from current and goal scene
        goal_scene, current_scene = Solver.initialize_rdf(current_scene, goal_scene, action_list)

        if RDFUtils.is_subset(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        while queue:
            parent_node = queue.pop(0)  # first-in, first-out

            for action in action_list:
                new_scene_action_dict = action.execute_action_on_rdf(
                    parent_node.state, debug=False
                )  # pruning Scenes: which action is executable in Scene, if executable generate Scene

                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        for scene in visited:
                            if RDFUtils.is_equal(next_scene, scene):
                                visited_check = True
                                break
                        if RDFUtils.is_subset(goal_scene, next_scene):
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

    def in_path(self, state, equality_check: callable):
        """Checks if a given state exists anywhere in the path from the current node
        back to the root node.
        Pruning reason: do not consider any path that visits the same state twice."""
        if equality_check(self.state, state):
            return True
        elif self.parent is None:
            return False
        else:
            return self.parent.in_path(state, equality_check)
