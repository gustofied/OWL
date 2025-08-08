# This is a possible event loop that drives the state machine
# Session = execution environment
# From Erik, https://www.arnovich.com/writings/state_machines_for_multi_agent_part_1/

def agent_step(agent):
    if agent.state == Finished: # check if the agent is finished
        return True # Agent is finished
    current_state = agent.interaction_stack.top()
    next_state = current_state.transition_step() # (adam) is this the action? what we call action
    agent.interaction_stack.push(next_state)
    if next_state.type == "finished":
        return True # Agent is finished 
    return False # Agent is not finished


def session_step(session): 
    finished = True # Assume all agents are finished
    for agent in session.agents: # For each agent in the session
        finished = finished and agent_step(agent) # Check if any agent is not finished
    return finished

while not session_finished(session): # Is this the env, 
    session_step(session)
    sleep(1)

# and this one too, https://www.arnovich.com/writings/state_machines_for_multi_agent_part_2/

# what is the or how is event loop defined in verifers gem, openai, art, mcts etc 
# the session drives the agent which acts and drives inside the game/states
# session = env?
# We need to translate games etc to llm speak
# session step -> agent step -> translate and game step? what about branches, 
# bare start adam

