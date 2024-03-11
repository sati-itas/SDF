from abc import abstractmethod

class BaseGoalManager:
    def __init__(self):
        pass

    @abstractmethod
    def setGoalScene():
        pass

    @abstractmethod
    def setHorizon():
        pass

    @abstractmethod
    def setHeuristic():
        pass