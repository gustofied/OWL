#### OWL Diary

is owl just about the interaction space for now?

#### Resoources

- Nice one, https://pretty-radio-b75.notion.site/rLLM-A-Framework-for-Post-Training-Language-Agents-21b81902c146819db63cd98a54ba5f31
- A peek into this could yield many learnings, https://github.com/axon-rl/gem
- This too, https://x.com/dileeplearning/status/1701478267755384935

- This means testing out leons stuff, learning from other akin stuff, and building up OWL in september to learn for this. That is kinda the main
  focus whilst you have so many other things you want we focus here, and other stuff gets rotated out for later come back to, never know what happens.

#### Observations

So observations is what the agents sees at one particular step, and is a subset of the total action space + metrics, moves etc?

Either way let's not drown ourselves in terms and concepts, just let's be clear that for a LLM agent
observatoins is the full systems + message prompt sent into the LLM model, and deciding observation space is
deciding what falls into here

This abouve one very interesting on how they translate into llm message?

Goes back into perhaps also in addition to building that observation space for the llm agent observation space could be increased by the agent itself looking into using a tool, where he could pick a number or sometthing from the stack in order to look back at history.. this is a bigger idea, the translation function it self in the lead above will be helpfful

the influence map, the observation space, the translation is the key, and what of the action space should/can be translated

how do we build the observation, we got actions global niveau, local niveau, a root agent see and can peek into local niveau via looking at their interaction stacks

#### History builder

a mechanism then to look at stack , observations at local niveau
this is more of a mechanism than learning problem? but again it cal learn to use this tool.
Translate games to LLM Speak

#### Drivers Runners

Agent runner?
Session step, agent step, translation step, game step

- https://www.arnovich.com/writings/more_on_agents/
- https://www.arnovich.com/writings/state_machines_for_multi_agent_part_1/
- https://www.arnovich.com/writings/state_machines_for_multi_agent_part_2/
- https://www.arnovich.com/writings/state_machines_for_multi_agent_part_3/
- https://www.arnovich.com/writings/state_machines_for_multi_agent_part_4/

#### Functions and Tools

Maybe some type of decorator of some sort to translate functions in openai ready function calling ready, validated cached or whatever? # For tools and decorating around functions, see docs on openai completaions?

#### Rewards

A rewards machine -> splits up 0 -> Goal
diverse range of goals

https://www.cyrusneary.com/publications/RM_for_cooperative_MARL
