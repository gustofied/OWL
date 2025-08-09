# import textarena as ta

# # Initialize agents
# agents = {
#     0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
#     1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
# }

# # Initialize the environment
# env = ta.make(env_id="TicTacToe-v0")
# env.reset(num_players=len(agents))

# done = False
# while not done:
#     player_id, observation = env.get_observation()
#     action = agents[player_id](observation)
#     done, step_info = env.step(action=action)

# rewards, game_info = env.close()