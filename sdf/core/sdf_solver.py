import heapq  # https://docs.python.org/3/library/heapq.html
from collections import (
    deque,
)  # https://docs.python.org/3/library/collections.html#deque-objects
from logging import getLogger
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from rdflib import Graph

from sdf.core.rdf_wrapper import RDFUtils
from sdf.core.rdf_wrapper import RDFWrapper
from sdf.core.sdf_core import Action
from sdf.core.sdf_core import Predicate
from sdf.core.sdf_core import Scene
from sdf.core.sdf_core import SDUtils


logger = getLogger(__name__)

# logger.setLevel(DEBUG)  # Set logger to DEBUG level for detailed output


class Solver:
    """Solver class for solving discrete state transition systems (SDScenes) and RDF graphs."""

    def __init__(self, object_template=None, rdf_graph_rules=None, predicates: Dict[str, Predicate]=None, current_scene_rdf_wrapper:RDFWrapper=None, fo_rewrite = False):
        """Initialize the Solver class."""

        # Check object_template structure
        if object_template is not None:
            if not isinstance(object_template, list):
                raise TypeError("object_template must be a list of lists.")
            if len(object_template) == 1:
                self.object_template = object_template[0]
                self.goal_template = object_template[0]
                logger.warning("goal_template is set to object_template[0]. This is deprecated. " \
                "Please provide a separate goal_template for more controllability.")
            elif len(object_template) == 2:
                self.object_template = object_template[0]
                self.goal_template = object_template[1]
            else:
                raise ValueError("object_template must be a list containing one or two lists (for object and goal template).")
        else:
            self.object_template = None
            self.goal_template = None

        self.rdf_graph_rules = rdf_graph_rules
        self.predicates = predicates
        #self.KN_graph = knowledge_graph
        self.current_scene_rdf_wrapper = current_scene_rdf_wrapper
        self.fo_rewrite = fo_rewrite
        if fo_rewrite and self.current_scene_rdf_wrapper is None:
            raise Exception('[SDF.SOLVER] First-order logic rewriting is enabled but no current_scene_rdf_wrapper is provided.' \
            'Actions cannot be rewritten without loaded knowledge graph (TBox).')

    def dfs_sdscene(
        self,
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
                new_scene_action_dict = action.execute_action_on_sdscene(parent_node.state)
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

    def bfs_sdscene(
        self,
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
                new_scene_action_dict = action.execute_action_on_sdscene(parent_node.state)  # pruning Scenes: which action is executable in Scene, if executable generate Scene

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

    def astar_sdscene(
        self,
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
        start_node = SearchNode(None, current_scene, None, g=0, h=h)
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
                new_scene_action_dict = action.execute_action_on_sdscene(parent_node.state)  #
                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        g_new = parent_node.g + action.weight  # accumulate action cost
                        # astar without heuristic is equivalent to uniform cost search (or Dijkstra's algorithm)
                        if heuristic is None:
                            h_new = 0
                        else:
                            h_new = heuristic(
                                goal_scene, next_scene
                            )  # Heuristic value for the new state
                        new_node = SearchNode(
                            [action, action_eff],
                            next_scene,
                            parent_node,
                            g=g_new,
                            h=h_new,
                        )
                        heapq.heappush(open_list, new_node)
        return ([], solution)

    def initialize_rdf(
        self, current_scene: Union[Scene, Graph], goal_scene: Union[Scene, Graph], action_list: List[Action]
    ) -> Tuple[Graph, Graph]:
        """Initialize RDF graphs from SDScenes or use existing RDF graphs."""

        if isinstance(current_scene, Scene) and isinstance(goal_scene, Scene):
            logger.info('[SDF.SOLVER.initialize_rdf] Initializing RDF graphs from SDScenes.')
            # Initialize RDF graph for current scene
            current_scene_rdf_wrapper = current_scene.init_rdf_wrapper(
                template=self.object_template, rules=self.rdf_graph_rules, predicates=self.predicates
                )
            current_scene_rdf_graph = current_scene_rdf_wrapper.data_graph
            logger.info(f'[SDF.SOLVER.initialize_rdf] RDF STATE: \n {RDFUtils.show_graph(current_scene_rdf_graph)}')
            # Initialize RDF graph for goal scene
            goal_rdf_wrapper = goal_scene.init_rdf_wrapper(template=self.goal_template, rules=self.rdf_graph_rules, predicates=self.predicates)
            goal_rdf_graph = goal_rdf_wrapper.data_graph
            logger.info(f'[SDF.SOLVER.initialize_rdf] RDF GOAL: \n {RDFUtils.show_graph(goal_rdf_graph)}')

            # Initialize actions with the current scene's RDF wrapper
            for action in action_list:
                action.init_action_with_rdf(current_scene_rdf_wrapper)

        elif isinstance(current_scene, Graph) and isinstance(goal_scene, Graph):
            logger.info('[SDF.SOLVER.initialize_rdf] RDF graphs are already initialized.')
            goal_rdf_graph = goal_scene
            if self.rdf_graph_rules is not None:
                logger.info('[SDF.SOLVER.initialize_rdf] Applying RDF graph rules to the current scene graph.')
                current_scene_rdf_graph = self.current_scene_rdf_wrapper.apply_rules(current_scene, rules=self.rdf_graph_rules)
            else:
                current_scene_rdf_graph = current_scene
            # Initialize actions with the current scene's RDF wrapper
            for action in action_list:
                action.init_action_with_rdf(self.current_scene_rdf_wrapper, rewrite=self.fo_rewrite)
        else:
            raise TypeError("current_scene and goal_scene must both be either Scene or Graph instances.")

        return goal_rdf_graph, current_scene_rdf_graph

    def dfs_rdf(
        self,
        current_scene: Union[Scene, Graph],
        goal_scene: Union[Scene, Graph],
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
        goal_scene, current_scene = self.initialize_rdf(
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
                    parent_node.state)
                if new_rdf_scene_action_dict:
                    for next_rdf_scene, action_eff in new_rdf_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_rdf_scene, parent_node
                        )
                        # new_node = SearchNode(action, next_scene, parent_node)

                        if RDFUtils.is_subset(goal_scene, next_rdf_scene):
                            solution = True
                            # path = new_node.path()
                            plan = new_node.path()
                            return (plan, solution)
                        elif parent_node.in_path(
                            next_rdf_scene, RDFUtils.is_equal
                        ):  # pruning rule1: do not consider any path that visits the same state twice
                            pass
                        else:
                            queue.append(new_node)
        return (plan, solution)

    def bfs_rdf(
        self,
        current_scene: Union[Scene, Graph],
        goal_scene: Union[Scene, Graph],
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
        goal_scene, current_scene = self.initialize_rdf(
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
                    parent_node.state)  # pruning Scenes: which action is executable in Scene, if executable generate Scene

                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode(
                            [action, action_eff], next_scene, parent_node
                        )
                        if RDFUtils.is_subset(goal_scene, next_scene):
                            solution = True
                            plan = new_node.path()
                            return (plan, solution)
                        # Check if the next scene has already been visited
                        next_key = RDFUtils.canonical_rdf_signature(next_scene)
                        if next_key in visited:
                            pass
                        else:
                            visited[next_key] = True
                            queue.append(new_node)
        return (plan, solution)

    def astar_rdf(
        self,
        current_scene: Union[Scene, Graph],
        goal_scene: Union[Scene, Graph],
        action_list: List[Action],
        heuristic: Optional[callable] = None,
    ) -> Tuple[List[Any], bool]:

        plan = []
        solution = False
        # Initialize the open list (priority queue) for A* search
        open_list = []

        # Init RDF graphs from current and goal scene
        goal_scene, current_scene = self.initialize_rdf(
                current_scene, goal_scene, action_list
            )

        # Check if the goal is already achieved
        if RDFUtils.is_subset(goal_scene, current_scene):
            return (plan, True)
        # astar without heuristic is equivalent to uniform cost search (or Dijkstra's algorithm)
        if heuristic is None:
            h = 0
        else:
            h = heuristic(goal_scene, current_scene)
        # Initialize the start node with the current scene and heuristic value
        start_node = SearchNode(None, current_scene, None, g=0, h=h)

        heapq.heappush(open_list, start_node)
        visited = set()

        while open_list:
            parent_node = heapq.heappop(open_list)

            if RDFUtils.is_subset(goal_scene, parent_node.state):
                solution = True
                plan = parent_node.path()
                return (plan, solution)

            # Check if the state has already been visited
            key = RDFUtils.canonical_rdf_signature(parent_node.state)
            if key in visited:
                continue
            visited.add(key)

            for action in action_list:
                new_scene_action_dict = action.execute_action_on_rdf(parent_node.state)
                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        g_new = parent_node.g + action.weight  # accumulate action cost

                        # astar without heuristic is equivalent to uniform cost search (or Dijkstra's algorithm)
                        if heuristic is None:
                            h_new = 0
                        else:
                            h_new = heuristic(
                                goal_scene, next_scene
                            )  # Heuristic value for the new state

                        new_node = SearchNode(
                            [action, action_eff],
                            next_scene,
                            parent_node,
                            g=g_new,
                            h=h_new,
                        )
                        heapq.heappush(open_list, new_node)
        return ([], solution)


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
