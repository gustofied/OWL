<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/1f/Edvard_Munch_-_At_the_Roulette_Table_in_Monte_Carlo_-_Google_Art_Project.jpg" alt="At the Roulette Table in Monte Carlo, Edvard Munch, 1892" width="440" />
</p>
<p align="center"><u>At the Roulette Table in Monte Carlo, Edvard Munch, 1892</u></p>

<h1 align="center">Monte Carlo Tree Search (MCTS)</h1>

<p align="center">
  Backpropagation, Simulations, Rollouts, Tree Search, To Seek
</p>

<hr />

<h5 align="left">What?</h5>
<p align="left">
  Well I started on this project but quick 20% through, I do I think I want to come back here, finish it up by 2025, the project here is to learn about MCTS, and then AlphaZero esque systems. To do a project that employs both of them, and then at finalement develop a system that on top of that includes some llm stuff, where and in what way I got pleny of ideas of, and plenty research on. I was thinking on applying it on and make a system for system prompt optimizing, search a tree of different approaches/(system prompts). The color game I'm making making is perhpas not that, it's more of a game akin to conenct four and is optimized or intertwine with LLMs in another way. Either way I have to come back and finish the job, so far I have researched MCTS, found some good resources and am looking to start on the AlphaZero work. Then at end LLM.

- [x] Color Game
- [x] MCTS
- [x] Rerun
- [ ] Observability layer with W&B rerun, fix what yo got
- [ ] Prime the project before working on AlphaZero
- [ ] AlphaZero begin here, [Watch on YouTube](https://www.youtube.com/watch?v=_Y26BFaVclg)
- [ ] Perhaps make a connect 4 game, as your color game is very explorative
- [ ] Decide the LLM MCTS project, if it's added on to color game, or something else
- [ ] Make that LLM MCTS, now you have three "demos"
- [ ] Research more abour colors, color theory and emerging integrations into what you made
- [ ] Organazie the whole repo, present the demos, and decide on further research

The project should be renamed and rotated into a new repo. and completed:)

</p>

<h5 align="left">MCTS</h5>

- [Fundementals](#fundementals)
- [Walkthroughs](#walkthroughs)
- [MCTS Deeper Dives](#mcts-deeper-dives)
- [AlphaZero Concepts](#alphazero-concepts)
- [MCTS and LLM](#mcts-and-llm)
- [Additional Resources](#additional-resources)

<h5 align="left">Fundementals?</h5>

**Fundamental resources for understanding the mechanics and motivations behind Monte Carlo Tree Search.**

- **Monte Carlo Tree Search Video by Michael Wollowski** — [Watch](https://www.youtube.com/watch?v=99gPnlfr7Jo)  
  _Overall great little video going into MCTS and some of its concepts._

- **Monte Carlo Tree Search (MCTS) Tutorial Video by Fullstack Academy** — [Watch](https://www.youtube.com/watch?v=99gPnlfr7Jo)  
  _Dabbles into not just MCTS but more—gives a bigger grasp around MCTS, concise about MCTS, a bit unclear, but still a nice watch._

- **Beyond Playing Games: How Monte Carlo Tree Search Is Powering the Next Generation of AI** — [Read](https://medium.com/data-science-collective/beyond-the-game-board-how-monte-carlo-tree-search-is-powering-the-next-generation-of-ai-a796994e2743)  
  _Short explanation of MCTS and exploration of combining MCTS with other methods to create better agents._

- **What is MCTS by Swarthmore** — [Read](https://www.cs.swarthmore.edu/~mitchell/classes/cs63/f20/reading/mcts.html)  
  _Nice and concise article—easy to read, just a quick overview._

- **Monte Carlo Tree Search by Arushi Somani** — [Read](https://www.amks.me/notes/mcts/)  
  _Very nice read, good info on UCB, plus she has many other solid articles._

---

<h5 align="left">Walkthroughs</h5>

**Michelangelo’s Four-Part Tutorial Series on MCTS, AlphaZero & MuZero**

1. **Monte Carlo Tree Search, AlphaZero & (Hopefully) MuZero for Dummies! (Part 1)** — [Read](https://medium.com/@_michelangelo_/monte-carlo-tree-search-mcts-and-hopefully-muzero-for-dummies-11ad5d95d9d8)  
   _High-level survey of MCTS’s role in modern AI._

2. **Monte Carlo Tree Search (MCTS) Algorithm for Dummies (Part 2)** — [Read](https://medium.com/@_michelangelo_/monte-carlo-tree-search-mcts-algorithm-for-dummies-74b2bae53bfa)  
   _Detailed breakdown of MCTS mechanics with pseudocode._

3. **AlphaZero for Dummies (Part 3)** — [Read](https://medium.com/@_michelangelo_/alphazero-for-dummies-5bcc713fc9c6)  
   _Explains how neural networks enhance traditional MCTS._

4. **MuZero for Dummies (Part 4)** — [Read](https://medium.com/@_michelangelo_/muzero-for-dummies-28fa076e781e)  
   _Introduces MuZero’s learned dynamics model building on AlphaZero._

---

<h5 align="left">MCTS Deeper Dives</h5>

- **Pitfalls and Solutions When Using Monte Carlo Tree Search for Strategy and Tactical Games** — [Download PDF](https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter28_Pitfalls_and_Solutions_When_Using_Monte_Carlo_Tree_Search_for_Strategy_and_Tactical_Games.pdf)  
  _Examines real-world challenges when applying MCTS to complex games and proposes practical mitigation strategies._

- **Monte Carlo Tree Search: a review of recent modifcations
  and applications** — [Download PDF](https://link.springer.com/article/10.1007/s10462-022-10228-y?utm_source=chatgpt.com)  
   _A major survey._

---

<h5 align="left">AlphaZero Concepts</h5>

- **AlphaZero Nature Article** — [Download PDF](https://www.nature.com/articles/nature24270.epdf?author_access_token=VJXbVjaSHxFoctQQ4p2k4tRgN0jAjWel9jnR3ZoTv0PVW4gB86EEpGqTRDtpIz-2rmo8-KG06gqVobU5NSCFeHILHcVFUeMsbvwS-lxjqQGg98faovwjxeTUgZAUMnRQ)  
  _Silver \_et al._, “Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm,” _Nature_, 2018. Explores AlphaZero’s core architecture—deep neural networks for policy/value estimation—and its integration with MCTS.\_

- **AlphaZero Overview (Josh Varty)** — [Read](https://joshvarty.github.io/AlphaZero/)  
  _A concise blog post that distills AlphaZero concepts and MCTS fundamentals, with examples and an optional video overview._

- **AlphaZero Connect Four (Monte Carlo Tree Search) (Super Nice)** — [Watch on YouTube](https://www.youtube.com/watch?v=_Y26BFaVclg) · [GitHub Repo](https://github.com/advait/c4a0)  
  _AlphaZero Connect Four (Monte Carlo Tree Search)_

---

<h5 align="left">MCTS and LLM</h5>

- **Improving LLM Accuracy with Monte Carlo Tree Search (Trellis Research)** — [Watch](https://www.youtube.com/watch?v=mfAV_bigdRA&t) simple introduction

- **AB-MCTS: Inference-Time Scaling and Collective Intelligence for Frontier AI** — [Tweet](https://x.com/TrelisResearch/status/1939998805438734657), [Read](https://sakana.ai/ab-mcts/) Sakana ofc

- **A paper, a repo, a write-down on an example use** — [Read Write-up and Paper](https://arunpatro.github.io/blog/mcts/#:~:text=MCTS%20achieves%20better%20benchmark%20performance,4%20unique%20samples%20per), [Repo](https://github.com/rmshin/llm-mcts) this is more doable and quick mvp project I think would be cool to try

- **Mastering Board Games by External and Internal Planning with Language Models** — [Paper](https://arxiv.org/pdf/2412.12119), [Tweet Leaed](https://x.com/ADarmouni/status/1874643013315518712) Harder read imo

---

<h5 align="left">Additional Resources</h5>

- **Monte Carlo Simulation Tutorial (Towards AI)** — [Read](https://towardsai.net/p/editorial/monte-carlo-simulation-an-in-depth-tutorial-with-python-bcf6eb7856c8)  
  _An in-depth walkthrough of Monte Carlo simulation techniques with Python, covering random sampling, statistical estimation, and practical examples It's Cool seeing the examples._
