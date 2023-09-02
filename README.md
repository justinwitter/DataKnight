# DataKnight

Hi! Welcome to DataKnight.

This project aims to help casual chess players quickly improve their game, while also compiling the concepts I've learned from chess over the past year or so. 

In the interest of speed, it would be counterintuitive to analyze hundreds (if not thousands) of openings, structures, and endgames that an advanced player may be exposed to. Instead, the main focus here is to emphasize fundamental chess principles while using data from real games as support. I believe (along with many GMs) that the best way to improve from these levels is to develop sound habits that apply to multiple positions and lead to tactical play.

While the traditional chess engine recommends the optimal move in certain positions, this analysis will focus on building a framework that consists of general principles of play that can be applied to many kinds of positions for decision-making. The goal is to help beginners play fundamental chess, which might not always be perfect chess.

## Contents

1. chessdotcom-scraper.py : retrieves chess data using the Chess.com API
2. data-preparation.ipynb : cleans data and engineers necessary features
3. habits-analysis.ipynb : explores recommended chess habits using statistical methods

## Background

I started playing chess in August of 2022 and, after about a year of non-concurrent play, I've been able to increase my ELO rating from 479 to 1222 [link](https://www.chess.com/stats/live/rapid/justinwitter/0). While 1200 is still a beginner rating and nothing to be immensely proud of, I've noticed a considerable difference in the learning rate between myself and many fellow peers who have been playing for much longer.

While being stuck around 600 I stumbled upon [chessbrah](https://www.youtube.com/playlist?list=PL8N8j2e7RpPnpqbISqi1SJ9_wrnNU3rEm), a YouTube channel that posted videos of GMs playing lower rated players and displaying fundamental chess rules instead of crushing. In fact, the GMs lost some games (with X5 proability) just to illustrate the emphasis on sound chess rather than perfect chess. At the end of the day I realized that the changes to my decision-making in chess were now being data-driven, with that data coming from GM teachings. Chess is all about optimal decison-making so I wanted to dive into the landscape of beginner chess to truly see how these games were being played. If I could identify common mistakes and determine better alternatives, on average this information would provide myself and others with the best opportunity to move up the ranks quickly.

This project is targeted towards casual players below 1000 (42% of playerbase) to build habits that will improve their fundamentals and allow them to play a solid game barring positional intricacies and time constraints. This opposes the conventional approach of chess engines which simply identify the best possible move in the position with little insight as to why.

Openings - a very crucial concept as it decides very game
While memorizing 15 moves to set an opening trap may be ideal for some, this approach a. wastes time that could be spent on fundamentals and b. doesn't work on experienced players that have either seen the trap before or play conservative lines. Pick openings with straightforward development and open positions. This allows for easy tactics instead of complicated positional theory.

This project is made for the hardstuck 800 elo player that doesn't understand how they keep hanging their queen every game. Most of the time this comes from a lack of fundamentals.

However, watching hours of chess games is also a bit much for some casual players. This project aims to present the core principles of the series using statistical evidence to help beginners improve their skills.

- Identify what the landscape of chess ratings/games look like, how your rating matches up, and what the obvious mistakes are for your level

It is the hope that by implementing these principles alone, beginner players can achieve rapid success in reaching higher ELO ratings.
