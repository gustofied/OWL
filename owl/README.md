GENZZZIS

Diary:
https://chatgpt.com/share/6890ce90-92f8-800b-8dc4-2c2eb1912d62

1. Does Litellm use the chat completions endpoint or nah?
2. OpenAI-compatible JSON schema
3. Function-calling / “tools” support is just passed through as the standard functions parameter on the ChatCompletion API. If you need to use OpenAI’s function-calling, you define your tool signatures in Python, pass them into chat_completion(functions=[…]), and Atropos will forward them directly. [This is kinda like P2Engine]
4. If you wanted to swap out OpenAI for another “OpenAI-compatible” inference server (vLLM’s REST shim, an Azure endpoint, SGLang, etc.), you simply set base_url to point there — Atropos will send the same JSON payloads it would to api.openai.com.
5. This is probably why you should do completions, well it is why.
6. We gather rollout from an environemnt (single-turn, multi-turn, or tool-calling)
7. Scores them with rubric
8. We want worlds for the agents to play in
9. They sit on the same layer of the stack—all four projects assume you already have an LLM that speaks the OpenAI-/Chat-Completions JSON spec and they focus on experience-driven improvement or evaluation.
10. Rollout → reward → update loop – collectors generate trajectories, some scorer/rubric produces rewards, an optimizer updates LoRA or full weights, then new weights get pushed back to the collectors.
11. What is LORA?
12. - Setup:
    - All collectors call a single BatchedLLM client that takes the usual {model, messages, …} payload.
    - Log every node expansion & reward in a Trajectory object.
    - And something like, Use asyncio.Queue → flush to LiteLLM with a batch_size knob.
13. Point your searcher at GEM envs (ARC, Human-Eval, tool-calling tasks) so you don’t spend weeks writing environments. But do also look at how yourself could make them
14. a research-oriented roll-out → reward → update, framework

15. obs = env.reset()
    done = False
    while not done: # ← the classic Gym “driver loop”
    action = policy.act(obs) # ❶ policy (LLM, searcher, etc.)
    obs, reward, done, info = env.step(action)
    buffer.add((obs, action, reward))

    The loop above is what we and many papers call the driver, roll-out worker, runner, or collector. Pick one term and stick to it in your codebase (I usually call the Ray/async actor RolloutDriver).

16. Tool-calling willccbb/verifiers’s ToolEnv shows how to thread a set of Python functions through the env.
17. Look at ways to do batched completions, you could do that through litellm?
18. Start with ENV? Adopt a Standard Interface: Structure your game environment using the OpenAI Gym API style, which is the field standard for RL tasks. This means defining an Env class with methods like reset(), step(action), and a clear way to represent observations, actions, and rewards. By following the Gym interface, you ensure compatibility with a wide range of RL algorithms and frameworks
19. Some existing envs are TextArena, Reasoing Gym
20. Creating Custom Environments: For a completely new game, you can still speed up development using libraries like Verifiers. Verifiers is a toolkit of modular components for defining RL environments and training loops for LLM agents
21. With an environment in place, the next step is training an agent (or agents) to play the game. A variety of RL training frameworks for language models have emerged, and you can choose one based on your needs: In summary, you have a spectrum of choices. If your focus is on multi-agent dialogue games or text contests, TextArena + UnstableBaselines is a quick path (these were literally made for the MindGames challenge). If you are more focused on single-agent reasoning puzzles, you might use Reasoning Gym for data and train with Verifiers or a custom loop. And if you plan to incorporate tools or complex actions, look at frameworks like Search-R1 or RAGEN for guidance on extending the action space and state.
22. Yes – use Weights & Biases (wandb) for metrics. Instrumenting your training runs with a tool like W&B will greatly help in debugging and improving your agent. In fact, the MindGames demo pipeline uses a Tracker class that handles W&B logging automaticall
23. From GEM GYM REPO their observations wrapper was interesting, tool wrapper , maybe there is something here?
