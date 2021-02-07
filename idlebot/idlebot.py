from rlbot.agents.base_agent import BaseAgent, SimpleControllerState

class IdleBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)