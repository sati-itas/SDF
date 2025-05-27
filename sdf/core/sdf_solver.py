import heapq  # https://docs.python.org/3/library/heapq.html
from collections import deque # https://docs.python.org/3/library/collections.html#deque-objects
from typing import Any
from typing import List
from typing import Optional
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

        # Init actions
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
                        elif parent_node.in_path(
                            next_scene, SDUtils.check_identical_scenes
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
        queue = deque()  # using deque for efficient FIFO queue operations
        visited = {}
        solution = False

        if SDUtils.check_subset_pair(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        # Init actions
        for action in action_list:
            action.init_action()

        while queue:
            parent_node = queue.popleft()  # first-in, first-out

            for action in action_list:
                new_scene_action_dict = action.execute_action_on_sdscene(
                    parent_node.state, debug=False
                )  # pruning Scenes: which action is executable in Scene, if executable generate Scene

                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        if SDUtils.check_subset_pair(goal_scene, next_scene):
                            solution = True
                            plan = new_node.act_sequence()
                            return (plan, solution)
                        # Check if the next scene has already been visited
                        next_key = SDUtils.canonical_scene_signature(next_scene)
                        if next_key in visited:
                            pass  # already visited, skip! do not consider any path that visits a state that you have already visited via some other path.
                        else:
                            visited[next_key] = True
                            queue.append(new_node)
        return (plan, solution)

    @staticmethod
    def astar_sdscene(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        heuristic: Optional[callable] = None,
    ) -> Tuple[List[Any], bool]:
        plan = []
        solution = False

        if SDUtils.check_subset_pair(goal_scene, current_scene):
            return (plan, True)

        open_list = []

        # astar without heuristic is equivalent to uniform cost search (or Dijkstra's algorithm)
        if heuristic is None:
            h = 0
        else:
            h = heuristic(goal_scene, current_scene)

        # Initialize the open list (priority queue) for A* search
        start_node = SearchNode(
            None, current_scene, None, g=0, h=h
        ) 
        heapq.heappush(open_list, start_node)
        visited = set()

        # Init actions
        for action in action_list:
            action.init_action()

        while open_list:
            parent_node = heapq.heappop(open_list)

            if SDUtils.check_subset_pair(goal_scene, parent_node.state):
                solution = True
                plan = parent_node.act_sequence()
                return (plan, solution)

            # Check if the state has already been visited
            key = SDUtils.canonical_scene_signature(parent_node.state)
            if key in visited:
                continue
            visited.add(key)

            for action in action_list:
                new_scene_action_dict = action.execute_action_on_sdscene(
                    parent_node.state, debug=False
                )  #
                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        g_new = (
                            parent_node.g + action.weight
                        )  # accumulate action cost
                        # astar without heuristic is equivalent to uniform cost search (or Dijkstra's algorithm)
                        if heuristic is None:
                            h_new = 0
                        else:
                            h_new = heuristic(goal_scene, next_scene) # Heuristic value for the new state
                        new_node = SearchNode(
                            [action, action_eff],
                            next_scene,
                            parent_node,
                            g=g_new,
                            h=h_new,
                        )
                        heapq.heappush(open_list, new_node)
        return None

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
        goal_scene, current_scene = Solver.initialize_rdf(
            current_scene, goal_scene, action_list
        )

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
                        elif parent_node.in_path(
                            next_rdf_scene, RDFUtils.is_equal
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
        queue = deque()  # using deque for efficient FIFO queue operations
        visited = {}
        solution = False
        # Init RDF graphs from current and goal scene
        goal_scene, current_scene = Solver.initialize_rdf(
            current_scene, goal_scene, action_list
        )

        if RDFUtils.is_subset(goal_scene, current_scene):
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        while queue:
            parent_node = queue.popleft()  # first-in, first-out

            for action in action_list:
                new_scene_action_dict = action.execute_action_on_rdf(
                    parent_node.state, debug=False
                )  # pruning Scenes: which action is executable in Scene, if executable generate Scene

                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        if RDFUtils.is_subset(goal_scene, next_scene):
                            solution = True
                            plan = new_node.act_sequence()
                            return (plan, solution)
                        # Check if the next scene has already been visited
                        next_key = RDFUtils.canonical_rdf_signature(next_scene)
                        if next_key in visited:
                            pass
                        else:
                            visited[next_key] = True
                            queue.append(new_node)
        return (plan, solution)

    @staticmethod
    def astar_rdf(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        heuristic: Optional[callable] = None,
    ) -> Tuple[List[Any], bool]:
        plan = []
        solution = False

        if SDUtils.check_subset_pair(goal_scene, current_scene):
            return (plan, True)

        # Init RDF graphs from current and goal scene
        goal_scene, current_scene = Solver.initialize_rdf(
            current_scene, goal_scene, action_list
        )
        # Initialize the open list (priority queue) for A* search
        open_list = []

        # astar without heuristic is equivalent to uniform cost search (or Dijkstra's algorithm)
        if heuristic is None:
            h = 0
        else:
            h = heuristic(goal_scene, current_scene)
        # Initialize the start node with the current scene and heuristic value
        start_node = SearchNode(
            None, current_scene, None, g=0, h=h
        )

        heapq.heappush(open_list, start_node)
        visited = set()

        while open_list:
            parent_node = heapq.heappop(open_list)

            if RDFUtils.is_subset(goal_scene, parent_node.state):
                solution = True
                plan = parent_node.act_sequence()
                return (plan, solution)

            # Check if the state has already been visited
            key = RDFUtils.canonical_rdf_signature(parent_node.state)
            if key in visited:
                continue
            visited.add(key)

            for action in action_list:
                new_scene_action_dict = action.execute_action_on_rdf(
                    parent_node.state, debug=False
                )  #
                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        g_new = parent_node.g + action.weight  # accumulate action cost

                        # astar without heuristic is equivalent to uniform cost search (or Dijkstra's algorithm)
                        if heuristic is None:
                            h_new = 0
                        else:
                            h_new = heuristic(goal_scene, next_scene) # Heuristic value for the new state

                        new_node = SearchNode(
                            [action, action_eff],
                            next_scene,
                            parent_node,
                            g=g_new,
                            h=h_new,
                        )
                        heapq.heappush(open_list, new_node)
        return None


class SearchNode:
    """Represent each node in the tree as an instance of class SearchNode. For BFS"""

    def __init__(self, action, state, parent=None, g=0, h=0):
        self.action = action
        self.state = state
        self.parent = parent

        self.g = g  # Cost so far
        self.h = h  # Heuristic value
        self.f = g + h  # Total estimated cost (f = g + h)

    def __lt__(self, other):
        """Less than operator for SearchNode to allow comparison based on f value.
        This is used to prioritize nodes in a priority queue (e.g., heapq or sorted)."""
        return self.f < other.f

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
