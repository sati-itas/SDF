import timeit
from typing import Any
from typing import List
from typing import Tuple

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
    ) -> Tuple[List[Any], bool]:
        """Deep First Search algorithm for finding path between current_scene and goal_scene
            in discrete state transition system (nodes: Scenes, transitions: actions).
            The execution method for actions is execute_select_dict_single().

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible actions

        Returns:
            plan, solution (Tuple[List[Any], bool]): returns a tupel with list of actions and a bool wich indicates if solution was found
        """
        # TODO setup data logger

        data_simple_dfs = data_logger

        plan = []
        queue = []
        solution = False

        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))

        while queue:
            parent_node = queue.pop()  # stack: last-in, first-out
            for action in action_list:
                next_scene, sd_rel = action.execute_select_dict_single(parent_node.state, debug=False)
                if next_scene:
                    new_node = SearchNode(action, next_scene, parent_node)
                    if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
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
    # TODO
    def dfs_list(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        data_logger: DataStorage = DataStorage('simple_dfs'),
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
        # TODO setup data logger

        data_simple_dfs = data_logger

        plan = []
        queue = []
        solution = False

        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            solution = True
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))

        while queue:
            parent_node = queue.pop()  # stack: last-in, first-out
            for action in action_list:

                new_scene_action_dict = action.execute_select_dict_list(parent_node.state, debug=False)
                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode([action, action_eff], next_scene, parent_node)

                        if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
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
    def simple_bfs(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        data_logger: DataStorage = DataStorage('simple_bfs'),
        debug=False,
    ) -> Tuple[List[Any], bool]:
        """Breadth First Search algorithm for finding path between current_scene and goal_scene in discrete
            state transition system (nodes: Scenes, transitions: actions).
            The execution method for actions is execute_select_dict_single().

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible actions

        Returns:
            plan, solution (Tuple[List[Any], bool]): returns a tupel with list of actions and a bool wich indicates if solution was found
        """
        data_simple_bfs = data_logger

        plan = []
        queue = []
        solution = False
        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            return (plan, solution)

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
                next_scene, sd_rel = action.execute_select_dict_single(
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

                if next_scene:
                    new_node = SearchNode(action, next_scene, parent_node)
                    if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
                        solution = True
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
                        return (plan, solution)
                    # elif parent_node.in_path(next_scene): # pruning rule1: do not consider any path that visits the same state twice
                    #     pass
                    # elif next_scene in new_child_states: # pruning rule2: if multiple actions lead to the same state, consider only one of them
                    #     pass
                    else:
                        queue.append(new_node)
            end_state_time = timeit.default_timer()
            # datalogger: log processing time
            data_simple_bfs.state_processing_time.append(end_state_time - start_state_time)
        return (plan, solution)

    @staticmethod
    def bfs_dp(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        data_logger: DataStorage = DataStorage('bfs_dp'),
        debug=False,
    ) -> Tuple[List[Any], bool]:
        """Breadth First Search algorithm for finding path between current_scene and goal_scene in
            discrete state transition system (nodes: Scenes, transitions: actions).
            The execution method for actions is execute_select_dict_single().

        Args:
            current_scene (Scene): current scene
            goal_scene (Scene): goal scene
            action_list (List[Action]): list of possible actions

        Returns:
            plan, solution (Tuple[List[Any], bool]): returns a tupel with list of actions and a bool wich indicates if solution was found
        """
        data_bfs_dp = data_logger

        plan = []
        queue = []
        visited = {}
        visited_check = False
        solution = False

        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        while queue:  # not goal_scene.scene_relations.items() <= current_scene.scene_relations.items() and
            parent_node = queue.pop(0)  # first-in, first-out

            for action in action_list:
                next_scene, sd_rel = action.execute_select_dict_single(
                    parent_node.state
                )  # pruning of states (Scenes): which action is executable in Scene, if executable generate Scene
                if next_scene:
                    new_node = SearchNode(action, next_scene, parent_node)
                    # print(f'parent_node.in_path(next_scene): {parent_node.in_path(next_scene)}')
                    for scene in visited:
                        if check_identical_scenes(next_scene, scene):
                            visited_check = True
                            break
                    if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
                        solution = True
                        plan = new_node.act_sequence()
                        return (plan, solution)
                    elif (
                        visited_check
                    ):  # pruning rule: do not consider any path that visits a state that you have already visited via some other path.
                        visited_check = False
                        pass
                    else:
                        visited[next_scene] = True
                        queue.append(new_node)
        return (plan, solution)

    @staticmethod
    def bfs_dp_list(
        current_scene: Scene,
        goal_scene: Scene,
        action_list: List[Action],
        data_logger: DataStorage = DataStorage('bfs_dp'),
        debug=False,
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
        data_bfs_dp = data_logger

        plan = []
        queue = []
        visited = {}
        visited_check = False
        solution = False

        if goal_scene.scene_relations.items() <= current_scene.scene_relations.items():
            return (plan, solution)

        queue.append(SearchNode(None, current_scene, None))
        visited = {current_scene: True}

        while queue:
            parent_node = queue.pop(0)  # first-in, first-out

            for action in action_list:
                new_scene_action_dict = action.execute_select_dict_list(
                    parent_node.state
                )  # pruning Scenes: which action is executable in Scene, if executable generate Scene

                if new_scene_action_dict:
                    for next_scene, action_eff in new_scene_action_dict.items():
                        new_node = SearchNode([action, action_eff], next_scene, parent_node)
                        # print(f'parent_node.in_path(next_scene): {parent_node.in_path(next_scene)}')
                        for scene in visited:
                            if check_identical_scenes(next_scene, scene):
                                visited_check = True
                                break
                        if goal_scene.scene_relations.items() <= next_scene.scene_relations.items():
                            solution = True
                            plan = new_node.act_sequence()
                            return (plan, solution)
                        elif (
                            visited_check
                        ):  # pruning rule: do not consider any path that visits a state that you have already visited via some other path.
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
            return self.parent.path() + [(self.action, self.state)]

    def act_sequence(self):
        """returns a sequence of a action"""
        if self.parent is None:
            return [(self.action)]
        else:
            return self.parent.act_sequence() + [(self.action)]

    def in_path(self, state):
        """checks if next state is equal to parent state.
        for pruning reason: do not consider any path that visits the same state twice."""
        if self.state.scene_relations.items() == state.scene_relations.items():  #
            return True
        elif self.parent is None:
            return False
        else:
            return self.parent.in_path(state)


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
