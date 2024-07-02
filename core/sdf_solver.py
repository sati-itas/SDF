import timeit
from typing import Any
from typing import List
from typing import Union

from analyse.data_storage import DataStorage
from core.sdf_core import Action
from core.sdf_core import Scene


class Solver:

    @staticmethod
    def simple_dfs(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        data_logger: DataStorage = DataStorage('simple_dfs'),
    ) -> Union[List[Any], bool]:
        """Deep First Search algorithm for finding path between current_scene and goal_scene in discrete state transition
            system (nodes: Scenes, transitions: actions)

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible basic maneuver

        Returns:
            List[Action]: plan
        """
        # TODO setup data logger

        data_simple_dfs = data_logger

        plan = []
        queue = []
        solution = False

        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            solution = True
            return [plan, solution]

        queue.append(SearchNode(None, current_scene, None))

        while queue:
            parent_node = queue.pop()  # stack: last-in, first-out
            for action in action_list:

                next_scene = action.execute(parent_node.state)
                if next_scene:
                    new_node = SearchNode(action, next_scene, parent_node)

                    if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
                        solution = True
                        # path = new_node.path()
                        plan = new_node.act_sequence()
                        return [plan, solution]
                    # elif parent_node.in_path(next_scene): # pruning rule1: do not consider any path that visits the same state twice
                    #     pass
                    else:

                        queue.append(new_node)
        return [plan, solution]

    @staticmethod
    def simple_bfs(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        data_logger: DataStorage = DataStorage('simple_bfs'),
        debug=False,
    ) -> Union[List[Any], bool]:
        """Breadth First Search algorithm for finding path between current_scene and goal_scene in discrete
        state transition system (nodes: Scenes, transitions: actions)

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible basic maneuver

        Returns:
            List[Action]: plan
        """
        data_simple_bfs = data_logger

        plan = []
        queue = []
        solution = False
        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            return [plan, solution]

        queue.append(SearchNode(None, current_scene, None))

        # datalogger: reset
        data_simple_bfs.state_count = 0
        data_simple_bfs.graph_processing_time = []
        data_simple_bfs.query_processing_time = []
        data_simple_bfs.effect_execute_processing_time = []
        data_simple_bfs.execute_processing_time = []

        while queue:
            start_state_time = timeit.default_timer()
            parent_node = queue.pop(0)  # queue: first-in, first-out

            # datalogger: state count
            data_simple_bfs.state_count += 1

            for action in action_list:
                start_execute_time = timeit.default_timer()
                next_scene = action.execute(
                    parent_node.state
                )  # pruning of states (Scenes) -> which action is executable in Scene -> proof if executable and if excutable generate Scene
                end_execute_time = timeit.default_timer()

                # datalogger: log execute
                data_simple_bfs.graph_processing_time.append(action.graph_processing_time)
                data_simple_bfs.query_processing_time.append(action.query_processing_time)
                data_simple_bfs.effect_execute_processing_time.append(action.effect_execute_processing_time)
                data_simple_bfs.execute_processing_time.append(end_execute_time - start_execute_time)

                # analyse
                # print(f'graph_processing_time : {action.graph_processing_time*1000} [msec]')
                # print(f'query_processing_time : {action.query_processing_time*1000} [msec]')
                # print(f'effect_execute_processing_time : {action.effect_execute_processing_time*1000} [msec]')
                # print(f'execute processing_time : {(end_execute_time-start_execute_time)*1000} [msec]')
                # debug
                # print(f'action.name: {action.name}')
                # print(f' parent_Node.state: {parent_Node.state}\n')
                # print(f' NextScene: {execution_return}')
                # print(f' goal_scene: {goal_scene}')

                if next_scene:
                    new_node = SearchNode(action, next_scene, parent_node)
                    if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
                        solution = True
                        # path = new_node.path()
                        plan = new_node.act_sequence()
                        end_state_time = timeit.default_timer()

                        # datalogger: log solution
                        data_simple_bfs.solution.append(solution)
                        data_simple_bfs.state_count_per_testloop.append(data_simple_bfs.state_count)
                        data_simple_bfs.state_processing_time.append(end_state_time - start_state_time)
                        data_simple_bfs.mean_graph_processing_time.append(
                            data_simple_bfs.mean_value(data_simple_bfs.graph_processing_time)
                        )
                        data_simple_bfs.mean_query_processing_time.append(
                            data_simple_bfs.mean_value(data_simple_bfs.query_processing_time)
                        )
                        data_simple_bfs.mean_effect_execute_processing_time.append(
                            data_simple_bfs.mean_value(data_simple_bfs.effect_execute_processing_time)
                        )
                        data_simple_bfs.mean_execute_processing_time.append(
                            data_simple_bfs.mean_value(data_simple_bfs.execute_processing_time)
                        )

                        return [plan, solution]
                    # elif parent_node.in_path(next_scene): # pruning rule1: do not consider any path that visits the same state twice
                    #     pass
                    # elif next_scene in new_child_states: # pruning rule2: if multiple actions lead to the same state, consider only one of them
                    #     pass
                    else:
                        queue.append(new_node)
            end_state_time = timeit.default_timer()

            # datalogger: log processing time
            data_simple_bfs.state_processing_time.append(end_state_time - start_state_time)
        return [plan, solution]

    @staticmethod
    def bfs_dp(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        data_logger: DataStorage = DataStorage('bfs_dp'),
        debug=False,
    ) -> Union[List[Any], bool]:
        """Breadth First Search algorithm for finding path between current_scene and goal_scene in
        discrete state transition system (nodes: Scenes, transitions: actions)

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible basic maneuver

        Returns:
            List[Action]: plan
        """
        data_bfs_dp = data_logger

        plan = []
        queue = []
        visited = {}
        solution = False

        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            return [plan, solution]

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        while queue:  # not goal_scene.scene_relations.items() <= current_scene.scene_relations.items() and
            parent_node = queue.pop(0)  # first-in, first-out

            for action in action_list:
                # start_execute_time = timeit.default_timer()
                next_scene = action.execute(
                    parent_node.state
                )  # pruning of states (Scenes) -> which action is executable in Scene -> proof if executable and if excutable generate Scene
                # end_execute_time = timeit.default_timer()
                # print(f'execute processing_time : {(end_execute_time-start_execute_time)*1000} [msec]')

                # debug
                # print(f'action.name: {action.name}')
                # print(f' parent_Node.state: {parent_Node.state}\n')
                # print(f' NextScene: {execution_return}')
                # print(f' goal_scene: {goal_scene}')

                if next_scene:
                    new_node = SearchNode(action, next_scene, parent_node)
                    # print(f'parent_node.in_path(next_scene): {parent_node.in_path(next_scene)}')
                    if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
                        solution = True
                        # path = new_node.path()
                        plan = new_node.act_sequence()
                        return [plan, solution]
                    elif (
                        next_scene in visited
                    ):  # pruning rule: do not consider any path that visits a state that you have already visited via some other path.
                        pass
                    else:
                        visited[next_scene] = True
                        queue.append(new_node)
        return [plan, solution]

    @staticmethod
    def simple_Astar(current_scene: Scene, goal_scene: Scene, action_list: List[Action]) -> Union[List[Action], bool]:
        """A* algorithm for finding path between current_scene and goal_scene in
        discrete state transition system (nodes: Scenes, transitions: actions)

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible basic maneuver

        Returns:
            List[Action]: plan
        """

        # Create start and end node
        start_node = Node(None, current_scene)
        start_node.g = start_node.h = start_node.f = 0
        end_node = Node(None, goal_scene)
        end_node.g = end_node.h = end_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # Add the start node
        open_list.append(start_node)

        solution = False
        count_loop = 0

        # print_scene(end_node.state,f)

        # Loop until you find the end
        while len(open_list) > 0 and solution == False:
            # Get the current node (Take from the open list the current_node with the lowest f(s))
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # Found the goal if current_node is goal we have found the solution; break
            if end_node.state.scene_relations.items() <= current_node.state.scene_relations.items():
                solution = True
                path = []
                sequence = []
                current = current_node
                while current is not None:
                    path.append(current.state)
                    if isinstance(current.action, Action):
                        sequence.append(current.action)
                    current = current.parent_state
                sequence = sequence[::-1]
                return [sequence, solution]

            # Generate children: apply action and determine effects of actions
            children = []
            # print_scene(current_node.state,f)
            for action in action_list:
                # if action.check_precondition(current_node.state):
                # NextScene=action.execute()
                execution_return = action.execute(current_node.state)
                if isinstance(execution_return, Scene):
                    NextScene = execution_return
                    nextNode = Node(current_node, NextScene, action)
                    children.append(nextNode)

            # Loop through children
            for child in children:
                open_list_counter = 0
                closed_list_counter = 0

                # Create the f, g, and h values heuristic function
                child.h = current_node.h - 2
                child.g = current_node.g + 1
                child.f = child.g + child.h

                for closed_node in closed_list:
                    # if not check_identical_scenes(child.state, closed_node.state):
                    #     closed_list_counter = closed_list_counter + 1

                    # if closed_list_counter != len(closed_list):
                    #     continue
                    if check_identical_scenes(child.state, closed_node.state):
                        continue
                    else:
                        closed_list_counter = closed_list_counter + 1

                for open_node in open_list:
                    # if not check_identical_scenes(child.state, closed_node.state):
                    #     open_list_counter = open_list_counter+1

                    # if open_list_counter == len(closed_list) and child.g > open_node.g:
                    #     continue

                    if check_identical_scenes(child.state, closed_node.state) and child.g > open_node.g:
                        continue
                    else:
                        open_list_counter = open_list_counter + 1

                # Add the child to the open list
                if open_list_counter == len(open_list) and closed_list_counter == len(closed_list):
                    open_list.append(child)

            # break condition
            if count_loop == 150:
                sequence = []
                print("solution takes to long")
                return [sequence, solution]
            count_loop += 1


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
            return self.parent.path() + [(self.action, self.state)]

    def act_sequence(self):
        """returns a sequence of a action"""
        if self.parent is None:
            return [(self.action)]
        else:
            return self.parent.act_sequence() + [(self.action)]

    def in_path(self, state):
        """checks if next state is equal to parent state. for pruning reason: do not consider any path that visits the same state twice."""
        if self.state.scene_relations.items() == state.scene_relations.items():  #
            return True
        elif self.parent is None:
            return False
        else:
            return self.parent.in_path(state)


class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent_state=None, state=None, action=None):

        self.parent_state = parent_state
        self.state = state
        self.action = action

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.state == other.state


def check_identical_scenes(scene1: Scene, scene2: Scene) -> bool:
    """checks if 2 scene descriptions (2 different "Scene" python objects) are identical in terms of their scene relations

    Args:
        scene1 (Scene): scene 1
        scene2 (Scene): scene 2

    Returns:
        bool: True if scenes are identical
    """
    if (
        scene1.scene_relations.items() <= scene2.scene_relations.items()
        and scene2.scene_relations.items() <= scene1.scene_relations.items()
    ):
        return True
    else:
        return False


def check_subset_scenes(goal_scene: Scene, scene2: Scene) -> bool:
    """checks if scene1.relations:type[dict] is a subset or equal to scene2.relations:type[dict] in terms of their scene relations

    Args:
        scene1 (Scene): scene 1
        scene2 (Scene): scene 2

    Returns:
        bool: True if scene1.relations:type[dict] is a subset or equal to scene2.relations:type[dict]
    """
    if goal_scene.scene_relations.items() <= scene2.scene_relations.items():
        return True
    else:
        return False
