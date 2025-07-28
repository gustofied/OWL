import math
import random


# Code from https://medium.com/data-science-collective/beyond-the-game-board-how-monte-carlo-tree-search-is-powering-the-next-generation-of-ai-a796994e2743
# A simple code example of MCTS

class Node: 
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_actions())
    
    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.value / child.visits) + c_param * math.sqrt(math.log(self.visits) / child.visits)
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]
    
    def expand(self):
        tried_actions = [child.state.last_action for child in self.children]
        for action in self.state.get_legal_actions():
            if action not in tried_actions:
                new_state = self.state.perform_action(action)
                new_node = Node(new_state, parent=self)
                self.children.append(new_node)
                return new_node
        return None
    
    def simulate(self):
        current_state = self.state.copy()
        while not current_state.is_terminal():
            action = random.choice(current_state.get_legal_actions())
            current_state = current_state.perform_action(action)
        return current_state.get_result()
    
    def backpropagate(self, result):
        self.visits += 1
        self.value += result
        if self.parent:
            self.parent.backpropagate(result)
    

def mcts(root_state, iterations=1000):
    root_node = Node(root_state)

    for _ in range(iterations):
        node = root_node

        # Selection
        while node.is_fully_expanded() and node.children:
            node = node.best_child()

        # Expansion
        if not node.state.is_terminal():
            node = node.expand()

        # Simulation
        result = node.simulate()

        # backpropagation
        node.backpropage(result)
    
    return root_node.best_child(c_param=0).state.last_action
    


# This implementation assumes the game state class includes:

# get_legal_actions(): returns valid actions.
# perform_action(action): returns a new state after applying an action.
# is_terminal(): checks if the state is terminal.
# get_result(): returns a result value (e.g., 1 for win, 0 for loss).
# last_action: stores the action that led to the current state.
# copy(): returns a deep copy of the state
# You can implement a simple demonstration for a Tic-Tac-Toe game for example.


# OWL CODE