from base_goal_manager import BaseGoalManager
from sdf_core import Scene


class SDL_GoalManager(BaseGoalManager):
    def __init__(self):
        self.goal_scene=None

    def set_goal_scene(self, goal_scene:Scene):
        self.goal_scene=goal_scene


