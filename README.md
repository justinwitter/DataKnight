# DataKnight

Hi! Welcome to DataKnight.

This project aims to help casual chess players quickly improve their game.

In the interest of speed, it would be counterintuitive to analyze hundreds (if not thousands) of openings, structures, and endgames that an advanced player may be exposed to. Instead, the goal is to implement fundamental chess principles and optimize common positions while using data from real games as support.

## Contents

1. **chessdotcom-scraper.py** : retrieves data using the Chess.com API, outputs *raw_data.csv*
2. **data-preparation.ipynb** : cleans data and engineers features, outputs *clean_data.csv*
3. **habits-analysis.ipynb** : explores recommended chess habits using statistical methods
4. **player-analysis.py** : creates a web app for individual player analysis

## Background

I started playing chess in August of 2022 and, after about a year of non-concurrent play, I've been able to increase my ELO rating from 479 to 1200+ [(my profile)](https://www.chess.com/stats/live/rapid/justinwitter/0). While 1200 is still a beginner rating and nothing to be immensely proud of, I've noticed a considerable difference in the learning rate between myself and many fellow peers who have been playing for much longer.

While being stuck around 600 I stumbled upon [chessbrah](https://www.youtube.com/playlist?list=PL8N8j2e7RpPnpqbISqi1SJ9_wrnNU3rEm), a YouTube channel that posted videos of GMs playing lower rated players and playing basic moves instead of crushing with theory. In fact, the GMs lost some games just to illustrate the emphasis on sound chess rather than perfect chess. I improved rapidly after watching this series, and I realized speculated the reason was because my decision-making was no being more data-driven, with that data coming from GM teachings. 

Chess is all about optimal decison-making so I wanted to dive into the landscape of beginner chess to truly see how these games were being played. If I could identify common mistakes and determine better alternatives, on average this information would provide myself and others with the best opportunity to move up the ranks quickly.

This project is targeted towards casual players below 1000 (42% of playerbase) to build habits that will improve their fundamentals and allow them to play a solid game barring positional intricacies and time constraints. This opposes the conventional approach of chess engines which simply identify the best possible move in the position with little insight as to why.

It is the hope that with these resources alone, beginner players can achieve rapid success in reaching higher ELO ratings.

## [Chess.com Scraper](https://github.com/justinwitter/DataKnight/blob/main/chessdotcom-scraper.py)

This file provides data used for further analysis throughout this project and also provides a framework that is built upon in the Positional Analysis web app. Feel free to utilize for data scraping and exploratory data analysis.

## Data Preparation
## Habits Analysis
## Position Analysis

This app aims to provide a deeper level of analysis than habits-analysis.ipynb by allowing players to target specific openings and positions that they struggle in. 
