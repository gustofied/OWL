<!-- # My idea is that we would need to translate the game to the llm in someways
# in addition this game trnslation could be a set of states
# whcih could if enable different stuff, for example planning, decompostiion etc.
# Tool usage to translate?


# It’s often helpful to provide a concise summary of the game’s rules, goals,
# and any special mechanics at the start of the prompt (for instance, in a system message or the first part of a prompt).
# This gives the LLM a grounding in what kind of environment it is operating in and what the objectives are

# When writing such rule descriptions, use clear, structured language or bullet points.
# You might outline the turn order, how combat or point scoring works,
# and constraints like “you cannot play more than one card per turn” or
# “a pawn moves forward one square”. Keep it as brief as possible while covering essentials –
# overly long rule dumps can exhaust the context window or confuse the model.
# The rule section can be separated or tagged (e.g., begin the prompt with a section titled "Game Rules:" followed by the summary).

# Hidden information: In multi-agent games with hidden information (like card games where each player’s hand is secret),
# be careful to only include information that the agent should know in that agent’s prompt.

# After we describe the game, and game rules, high-level, the prompt should desrcribe the current game state
# in a structured and unambiguous way. This typically includes: the turn number or phase, the positions or statuses of pieces/characters,
# each player’s relevant stats (health, score, resources, etc.), and any other contextual info (like weather effects in Pokémon or the last move made).

# Each turn use a consistent format. Our game/visual layer could auto generate a textual observation, which could include info such as
# 1) the game name and which player the agent is, (2) a visualization or listing of the current board state, and (3) the list of legal moves available

# Example

# Game: Tic-Tac-Toe – You are X (playing against O).
# Turn 3. Current board:
# X | O |
# - + - + -
#   | X |
# - + - + -
#   |   | O

# Available moves: (a) place X in top-right, (b) place X in middle-left, (c) place X in bottom-left, (d) place X in bottom-middle).

# Critically, include all information the model needs to decide on a move.

# Include recent history if relevant: For many games, the last move or a short history of recent turns can be important for strategy.
# However, be mindful of length; don’t dump a full move list every time if it’s long


# In general, prompt the model in a way that it cannot miss the fact that it must choose from the provided actions.
# Phrases like “Choose one of the following options” or “Reply only with the number of your chosen action” are effective.


# Multi-turn decision-making: Ensuring the model maintains a strategy over many turns is challenging.
# Prompting the reasoning each turn helps, as the model can refer back to previous rationale
# (if it’s kept in the conversation context or a persistent memory).
# You could give the model a meomry of past states and plans
# in claude pokemon they gave the model a tool to record facts it learned
# How do we remind the model of the long term goal, to pick a strategy to win?
# How do we give a model long term info, when do we remind it.

# > Comment
# I think that this is why it is promoising to test out starting with a root agent who can set up a plan, or has that is his main goal,
# Just an understanding of the task etc, and then he can use the tools as sub agents and more to his disposable in order to test the env, adust things etc
# He can always test out a system prompt, a user message adjustment on an agent, info from that test gets stored, and he can use tool to look if wanted
# lets say that sub agent looses, well  that info is maybe stored, but is not fed to the root agent, only if he want to peek and see
# so sub agents as tools can help towards long term play, by having the long term plan consistent to the root agent? sub agents is him testing his hypothesis or actions
# rambly here come back to this to really think

# this game transition should be like a general prompting system we build.
# It constructs prompts as described earlier: game state + legal moves + a request for reasoning and answer in JSON

# Some tips

# Use a System/Role prompt for overarching instructions:

# Clearly separate sections in the prompt
# One structure that works: Rules/Context, then Current State, then Your Task/Question. For instance:
# - Rules: (if needed, or put in system message).
# - State: (describe the game state as discussed).
# - Available Actions: (list them).
# - Question: “What do you do? Provide your reasoning and then your action.”

# Keep prompts consistent every turn

# Minimize irrelevant verbosity
# Minimize open-ended questions
# Minimize self-referential or meta language

# Example TextArena Example

# [GAME] You are Player 0. You are playing Mastermind (easy level).
# Your goal is to guess the other player's secret code that is 4 digits long, where each digit ranges from 1 to 6 with no duplicates.
# In your responses, you may discuss strategies, but **when you are ready to make a guess, you must format it as** [X X X X].
# After each guess, you will receive feedback (black pegs for correct digit+position, white pegs for correct digit wrong position).
# You have 10 turns to guess the code. Good luck!


# Action Formatting Constraints: A recurring convention is to require the model’s action in a specific textual format that can be parsed.
# Rather than selecting from a list of moves or outputting an index, the model is asked to write the move (or answer) in context.  -->
