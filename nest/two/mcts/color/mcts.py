import math
import random


class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0

    # ------------------------------------------------------------------ A+B
    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_actions())

    def best_child(self, c_param: float = 1.4):
        """
        UCT selection with safe handling of unvisited children.
        If a child has zero visits it is returned immediately.
        """
        best, best_score = None, float("-inf")
        for child in self.children:
            if child.visits == 0:
                return child  # explore unvisited node immediately
            exploit = child.value / child.visits
            explore = c_param * math.sqrt(math.log(self.visits) / child.visits)
            score = exploit + explore
            if score > best_score:
                best, best_score = child, score
        return best

    def expand(self):
        tried = {child.state.last_action for child in self.children}
        for action in self.state.get_legal_actions():
            if action not in tried:
                next_state, _, _, _ = self.state.step(action)
                new_node = Node(next_state, parent=self)
                self.children.append(new_node)
                return new_node
        return None

    # ------------------------------------------------------------------ A
    # ------------------------------------------------------------------
    def simulate(self):
        """
        Roll out with random moves until the environment signals done,
        accumulating step-rewards.  Handles the corner-case where the
        starting node is already terminal (no legal actions).
        """
        current_state = self.state.copy()

        # 1) If the starting state is terminal, just return its outcome.
        if current_state.is_terminal():
            return current_state.get_result()

        total_reward = 0.0
        while True:
            legal = current_state.get_legal_actions()

            # 2) Defensive guard: no moves even though not done yet
            #    (should only occur if is_terminal mis-matches, but be safe).
            if not legal:
                total_reward += current_state.get_result()
                break

            action = random.choice(legal)
            current_state, reward, done, _ = current_state.step(action)
            total_reward += reward
            if done:
                break

        return total_reward


    def backpropagate(self, result):
        self.visits += 1
        self.value += result
        if self.parent:
            self.parent.backpropagate(-result)


def mcts(root_state, iterations: int = 1000):
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

        # Backpropagation
        node.backpropagate(result)

    return root_node.best_child(c_param=0).state.last_action
