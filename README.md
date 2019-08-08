# Basketball Possession Scraper

The goal of this project was to create a new statistic for players using possession by possession data to determine
how many points were made each possession while a certain player was on the floor, normalized for their teammates.
In essence, this data would approximate for each player how many points one could expect a team to score per possession
given that the team was an average team plus the player.

## Process and Results

I scraped https://www.basketball-reference.com, checking to see on every day between the season start and season end if there was a game played at home by each time, scraping the players in the game and the result of each possession. This results in 255 thousand possessions scraped. This is done by possessionScraper.py, and it outputs possessions.csv. Then the relevant advanced statistic is scraped from each player's personal stats page, done by playerScraper.py and outputted to players.csv. I chose Defensive Win Shares to measure defense and Offensive Win Shares to measure offense. Then, regressPlayer.py takes every possession with the player in it, looks up the skill of their teammates and the result, regresses all of this to find an expected per possession outcome on offense and defense, then outputs this as playersRegressed.csv.

According to this, the top five players in general, on offense, and on defense, are:

1. Myles Turner
2. Jakob Poeltl
3. Al-Farouq Aminu
4. Lamarcus Aldridge
5. Brook Lopez

Offense:
1. Hassan Whiteside
2. Joe Harris
3. Kemba Walker
4. Lamarcus Aldridge
5. Klay Thompson

Defense:
1. Al-Farouq Aminu
2. Myles Turner
3. Damian Lillard
4. Kyrie Irving
5. CJ McCollum

Uhh... So these aren't exactly the results I was hoping for. The only one that feels like it belongs is Klay Thompson as a top five offensive player. I tried a couple of different options to try to get it to work, and eventually landed on this one where it looks at the average result for each set of teammates the player played with, and that seemed to work the best. I also tried taking into account the defense they were playing and originally regressing on each individual possession. What was especially concerning was that with decent regularity there seemed to be a negative correlation between playing with good teammates and results. My thought there was that maybe one plays with worse players when one is also playing against worse teams, so I tried to account for that by counting the skill of the defense, but this did not improve the situation.

## Potential Solutions / Ways To Improve:

1. **Clean up code and add more documentation**
   - Specifically, I know there are some variable names that could be changed for comprehension. Additionally, documentation is very sparse. Especially since this is tailored so heavily to an outside source, I need to explain a lot of what I am doing and why.
2. **Better testing**
    - One reason the project may not have worked as planned is perhaps the data I scraped is wrong. I tried to do as much testing as was feasible at the time, but even in one game there are over 200 possessions to compare to the result, which was rather restrictive.
3. **Research if there better, but similar methods**
    - At first glance, something exactly like this has not been attempted, but perhaps there are similar ideas available to consult. Also, I could ask around to people that I know who are more familiar with statistical models.
4. **Retool the project**
    - Perhaps there is something interesting that I can still do with this data, or similar data. Exact possession data for an entire season is not readily available, so I could look at how fast a team plays with certain players on the court, or propensity to shoot threes with certain players on the court (this could be especially interesting does not shoot many threes but creates space, a la LeBron James on the Cavs or potentially Westbrook now on the Rockets).
