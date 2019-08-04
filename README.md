# Basketball Possession Scraper

The goal of this project was to create a new statistic for players using possession by possession data to determine 
how many points were made each possession while a certain player was on the floor, normalized for their teammates. 
In essence, this data would approximate for each player how many points one could expect a team to score per possession 
given that the team was an average team plus the player.

## Complication

In trying to get the possession per possession data, I chose to scrape data from basketball-reference.com because they had play by play data for each game. However, once I wrote the code to keep track of who was in the game at a given time, I discovered that basketball-reference did not
keep track of which players were substituted each quarter. I emailed them and they responded that they do not have this data. This made my task much
more difficult. To know who was in the game after a new quarter I would have to check who got substituted out for the rest of the quarter. This might
work but there are players that do not get subbed out for the entire quarter, and so I would just have to guess at that point based on who played 
the most minutes for the team (might be an interesting idea, not sure how accurate that would be). Either way, for now I have decided to put this
project on hold. Last edit to the code was made December 1st 2018.

## What is working then?

Currently what is working is that given a home team and a date of the game, the program can scrape the starting five for each team. 
I can also keep track of who is subbed in and out, but it is not accurate due to the quarter subbing explained aboved. The next step would be
to be able to accurately scrape the possessions and store them. 
