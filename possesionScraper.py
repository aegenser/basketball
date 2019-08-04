from bs4 import BeautifulSoup as bsoup
import urllib.request
import copy, time
import pandas as pd
import numpy as np

def findAwayCol(row):
    return row.find_next('td').find_next('td')

def findHomeCol(row):
    return row.find_next('td').find_next('td').find_next('td').find_next('td')\
           .find_next('td').find_next('td')

class Possession():

    def __init__(self, offPlayers, defPlayers):
        self.offPlayers     = offPlayers
        self.defPlayers     = defPlayers
        self.nextPossession = None
        self.end            = 0

    def __str__(self):
        if self != None:
            result = "Offense: "
            for player in self.offPlayers:
                result = result + player + ' '
            result = result + "Defense: "
            for player in self.defPlayers:
                result = result + player + ' '
            result = result + "Result: " + str(self.end)

            return result + ' ;\n ' + str(self.nextPossession)

    def addPoints(self, end):
        self.end += end

class Player():
    def __init__(self, tag, minutes, seconds):
        self.tag = tag
        self.minutes = minutes
        self.seconds = seconds

    def __str__(self):
        return self.tag

    def __repr__(self):
        return self.tag

    def __lt__(self, other):
        if (self.minutes < other.minutes) or ((self.minutes == other.minutes) \
           and (self.seconds < other.seconds)):
            return 1
        else:
            return 0

    def __eq__(self, other):
        return (self.minutes == other.minutes and self.seconds == other.seconds)

def scrapeBoxScore(year, month, day, team):
    myUrl = 'https://www.basketball-reference.com/boxscores/' \
             + year + month + day + '0' + team + '.html' #standardized url
    playersHome = []
    playersAway = []
    startersHome = []
    startersAway = []
    client = urllib.request.urlopen(myUrl).read()
    soup = bsoup(client, 'lxml')
    body = soup.body
    div = body.find('div', {'class' : 'content_grid'}) # this is the table
    # before the table for the away team players
    awayTable = div.next_sibling.next_sibling
    row = awayTable.find_next('tbody').find_next('tr') # first row
    for _ in range(5):
        player = row.find_next( scope = 'row' )
        playertag = player.get('data-append-csv') # extract info
        time = player.find_next('td').string
        seconds = int(time[-2:]) # isolate seconds and minutes
        minutes = int(time[:-3])
        currentPlayer = Player(playertag, minutes, seconds)
        playersAway.append(currentPlayer) # save the player with time
        startersAway.append(playertag) # save the starter
        row = row.next_sibling.next_sibling # next row
    row = row.next_sibling.next_sibling # skip a line that isn't a player
    while(row != None): # do the same for the bench players
        player = row.find_next( scope = 'row' )
        playertag = player.get('data-append-csv')
        time = player.find_next('td').string
        if 'Not' not in time:
            seconds = int(time[-2:])
            minutes = int(time[:-3])
            currentPlayer = Player(playertag, minutes, seconds)
            playersAway.append(currentPlayer)
        row = row.next_sibling.next_sibling
    # do the same for the home team
    homeTable = awayTable.next_sibling.next_sibling.next_sibling.next_sibling
    row = homeTable.find_next('tbody').find_next('tr')
    for _ in range(5):
        player = row.find_next( scope = 'row' )
        playertag = player.get('data-append-csv')
        time = player.find_next('td').string
        seconds = int(time[-2:])
        minutes = int(time[:-3])
        currentPlayer = Player(playertag, minutes, seconds)
        playersHome.append(currentPlayer)
        startersHome.append(playertag)
        row = row.next_sibling.next_sibling
    row = row.next_sibling.next_sibling
    while(row != None):
        player = row.find_next( scope = 'row' )
        playertag = player.get('data-append-csv')
        time = player.find_next('td').string
        if 'Not' not in time:
            seconds = int(time[-2:])
            minutes = int(time[:-3])
            currentPlayer = Player(playertag, minutes, seconds)
            playersHome.append(currentPlayer)
        row = row.next_sibling.next_sibling

    playersAway.sort(reverse = True)
    playersHome.sort(reverse = True)
    return (playersAway, playersHome, startersAway, startersHome)


def scrapeQuarterStarters(year, month, day, team):
    (playersAway, playersHome, starters1QAway, starters1QHome) = scrapeBoxScore(year, month, day, team)

    myUrl = 'https://www.basketball-reference.com/boxscores/pbp/' \
             + year + month + day + '0' + team + '.html'
    startersHome = [starters1QHome, [], [], []]
    startersAway = [starters1QAway, [], [], []]
    havegoneinHome = [[], [], []]
    havegoneinAway = [[], [], []]
    client = urllib.request.urlopen(myUrl).read()
    soup = bsoup(client, 'lxml')
    body = soup.body
    table  = body.find(id = 'div_pbp')
    row    = table.find_next('tr').find_next('tr').find_next('tr')\
             .find_next('tr')

    whichQuarter = 1
    while(row != None and ((findAwayCol(row).string == None) or \
          ("End of 4th" not in findAwayCol(row).string))):
        #print(findAwayCol(row).text)
        if((findAwayCol(row).string != None) \
           and ("End of" in findAwayCol(row).string)):
           if("2nd" in findAwayCol(row).string):
               whichQuarter = 3;
           elif("3rd" in findAwayCol(row).string):
               whichQuarter = 4;
           else:
               whichQuarter = 2;
        elif((findAwayCol(row).text != None) \
             and ("enters" in findAwayCol(row).text)):
            playerIn = findAwayCol(row).find_next('a')
            playerOut = playerIn.find_next('a')
            playerIn = playerIn.get('href')[11:-5]
            playerOut = playerOut.get('href')[11:-5]
            if whichQuarter != 1:
                if playerOut not in havegoneinAway[whichQuarter-2]:
                    (startersAway[whichQuarter-1]).append(playerOut)
                if playerIn not in havegoneinAway[whichQuarter-2]:
                    (havegoneinAway[whichQuarter-2]).append(playerIn)
        elif('Jump ball' not in findAwayCol(row).text and \
             (findHomeCol(row).text != None) \
             and ("enters" in findHomeCol(row).text)):
            playerIn = findHomeCol(row).find_next('a')
            playerOut = playerIn.find_next('a')
            playerIn = playerIn.get('href')[11:-5]
            playerOut = playerOut.get('href')[11:-5]
            if whichQuarter != 1:
                if playerOut not in havegoneinHome[whichQuarter-2]:
                    (startersHome[whichQuarter-1]).append(playerOut)
                if playerIn not in havegoneinHome[whichQuarter-2]:
                    (havegoneinHome[whichQuarter-2]).append(playerIn)
        row = row.find_next('tr')

    #print(startersHome)
    #print(havegoneinHome)
    for num, starters in enumerate(startersHome):
        i = 0
        while(len(starters) < 5):
            #print(num)
            #print(starters)
            #print(havegoneinHome[num-1])
            if (playersHome[i].tag not in starters) and \
               (playersHome[i].tag not in havegoneinHome[num-1]):
                starters.append(playersHome[i].tag)
            i = i + 1

    for num, starters in enumerate(startersAway):
        i = 0
        while(len(starters) < 5):
            if (playersAway[i].tag not in starters) and \
               (playersAway[i].tag not in havegoneinAway[num-1]):
                starters.append(playersAway[i].tag)
            i = i + 1

    return (startersHome, startersAway)

def scrapePossession(year, month, day, team):

    myUrl = 'https://www.basketball-reference.com/boxscores/pbp/' \
             + year + month + day + '0' + team + '.html'

    try:
        client = urllib.request.urlopen(myUrl).read()
    except:
        return (None, 0)
    soup   = bsoup(client, 'lxml')
    body   = soup.body
    table  = body.find(id = 'div_pbp')
    row    = table.find_next('tr').find_next('tr').find_next('tr')\
             .find_next('tr')

    amountOfErrors  = 0

    (startersHome, startersAway) = scrapeQuarterStarters(year, month, day, team)
    #print(startersHome)
    #print(startersAway)
    whichQuarter = 1;
    #homeOnOff -- true if Home team is on offense, false if Home team is on defense
    #jumpballResult -- true if home team got it, false if away team got it
    duringFreeThrows = False

    basePossession = Possession([],[])
    currentPossession = basePossession

    jumpballPlayer = findAwayCol(row).find_next('a').find_next('a') \
                     .find_next('a').get('href')
    jumpballPlayer = jumpballPlayer[11:-5]

    currentPoints      = 0
    currentPlayersAway = copy.copy(startersAway[0])
    nextPlayersAway    = copy.copy(startersAway[0])
    currentPlayersHome = copy.copy(startersHome[0])
    nextPlayersHome    = copy.copy(startersHome[0])

    if jumpballPlayer in startersHome[0]:
        jumpballResult = True
        homeOnOff = True
    else:
        jumpballResult = False
        homeOnOff = False

    row = row.find_next('tr')
    while(row != None and ((findAwayCol(row).string == None) or \
          ("End of 4th" not in findAwayCol(row).string))):
        if((findAwayCol(row).string != None) \
           and ("End of" in findAwayCol(row).string)):
            #print(currentPlayersAway)
            #print(currentPlayersHome)
            if homeOnOff:
                newPossession = Possession(copy.copy(currentPlayersHome), \
                                           copy.copy(currentPlayersAway))
            else:
                newPossession = Possession(copy.copy(currentPlayersAway), \
                                           copy.copy(currentPlayersHome))
            newPossession.addPoints(currentPoints)
            currentPoints = 0
            currentPossession.nextPossession = newPossession
            currentPossession = newPossession
            #print(findAwayCol(row).string)
            row = row.find_next('tr')
            #print(findAwayCol(row).string)
            if("2nd" in findAwayCol(row).string):
                homeOnOff = not jumpballResult
                whichQuarter = 2;
                #print('End of First')
            elif("3rd" in findAwayCol(row).string):
                homeOnOff = not jumpballResult
                whichQuarter = 3;
                #print('End of Second')
            else:
                homeOnOff = jumpballResult
                whichQuarter = 4;
                #print('End of Third')
            currentPlayersAway = copy.copy(startersAway[whichQuarter - 1])
            nextPlayersAway = copy.copy(startersAway[whichQuarter - 1])
            currentPlayersHome = copy.copy(startersHome[whichQuarter - 1])
            nextPlayersHome = copy.copy(startersHome[whichQuarter - 1])
        elif((findAwayCol(row).text != None) \
             and ("enters" in findAwayCol(row).text)):
            playerIn = findAwayCol(row).find_next('a')
            playerOut = playerIn.find_next('a')
            playerIn = playerIn.get('href')[11:-5]
            playerOut = playerOut.get('href')[11:-5]
            #print("sub " + playerIn + " for " + playerOut)
            if playerIn in currentPlayersAway:
                amountOfErrors += 1
            if playerOut not in currentPlayersAway:
                amountOfErrors += 1
            for i in range(5):
                if(nextPlayersAway[i] == playerOut):
                    nextPlayersAway[i] = copy.copy(playerIn)
                    break
            if not duringFreeThrows:
                currentPlayersAway = copy.copy(nextPlayersAway)
            #print(currentPlayersAway)
        elif 'Jump ball' in findAwayCol(row).text:
            jumpballPlayer = findAwayCol(row).find_next('a').find_next('a') \
                             .find_next('a').get('href')
            jumpballPlayer = jumpballPlayer[11:-5]
            if ((jumpballPlayer in currentPlayersAway) and \
               (homeOnOff)) or ((jumpballPlayer in currentPlayersHome) and \
               (not homeOnOff)):
               if homeOnOff:
                   newPossession = Possession(copy.copy(currentPlayersHome), \
                                              copy.copy(currentPlayersAway))
               else:
                   newPossession = Possession(copy.copy(currentPlayersAway), \
                                              copy.copy(currentPlayersHome))
               newPossession.addPoints(currentPoints)
               currentPoints = 0
               currentPossession.nextPossession = newPossession
               currentPossession = newPossession
               homeOnOff = not homeOnOff
        elif((findHomeCol(row).text != None) \
             and ("enters" in findHomeCol(row).text)):
            playerIn = findHomeCol(row).find_next('a')
            playerOut = playerIn.find_next('a')
            playerIn = playerIn.get('href')[11:-5]
            playerOut = playerOut.get('href')[11:-5]
            #print("sub " + playerIn + " for " + playerOut)
            if playerIn in currentPlayersHome:
                amountOfErrors += 1
            if playerOut not in currentPlayersHome:
                amountOfErrors += 1
            for i in range(5):
                if(nextPlayersHome[i] == playerOut):
                    nextPlayersHome[i] = copy.copy(playerIn)
                    break
            if not duringFreeThrows:
                currentPlayersHome = copy.copy(nextPlayersHome)
            #print(currentPlayersHome)
        elif('Turnover' in findHomeCol(row).text or \
             'Turnover' in findAwayCol(row).text):
             if homeOnOff:
                 newPossession = Possession(copy.copy(currentPlayersHome), \
                                            copy.copy(currentPlayersAway))
             else:
                 newPossession = Possession(copy.copy(currentPlayersAway), \
                                            copy.copy(currentPlayersHome))
             newPossession.addPoints(currentPoints)
             currentPoints = 0
             currentPossession.nextPossession = newPossession
             currentPossession = newPossession
             homeOnOff = not homeOnOff
        elif('Defensive rebound' in findHomeCol(row).text or \
             'Defensive rebound' in findAwayCol(row).text):
             if homeOnOff:
                 newPossession = Possession(copy.copy(currentPlayersHome), \
                                            copy.copy(currentPlayersAway))
             else:
                 newPossession = Possession(copy.copy(currentPlayersAway), \
                                            copy.copy(currentPlayersHome))
             newPossession.addPoints(currentPoints)
             currentPoints = 0
             currentPossession.nextPossession = newPossession
             currentPossession = newPossession
             homeOnOff = not homeOnOff
        elif('free throw' in findHomeCol(row).text):
            if not duringFreeThrows:
                duringFreeThrows = not duringFreeThrows
            if 'makes' in findHomeCol(row).text:
                currentPoints += 1
            if '1 of 1' in findHomeCol(row).text or \
               '2 of 2' in findHomeCol(row).text or \
               '3 of 3' in findHomeCol(row).text or \
               'technical' in findHomeCol(row).text:
               if homeOnOff:
                   newPossession = Possession(copy.copy(currentPlayersHome), \
                                              copy.copy(currentPlayersAway))
               else:
                   newPossession = Possession(copy.copy(currentPlayersAway), \
                                              copy.copy(currentPlayersHome))
               newPossession.addPoints(currentPoints)
               currentPoints = 0
               currentPossession.nextPossession = newPossession
               currentPossession = newPossession
               currentPlayersHome = copy.copy(nextPlayersHome)
               currentPlayersAway = copy.copy(nextPlayersAway)
               duringFreeThrows = 0
               if 'makes' in findHomeCol(row).text:
                   homeOnOff = not homeOnOff
        elif('free throw' in findAwayCol(row).text):
            if not duringFreeThrows:
                duringFreeThrows = not duringFreeThrows
            if 'makes' in findAwayCol(row).text:
                currentPoints += 1
            if '1 of 1' in findAwayCol(row).text or \
               '2 of 2' in findAwayCol(row).text or \
               '3 of 3' in findAwayCol(row).text or \
               'technical' in findAwayCol(row).text:
               if homeOnOff:
                   newPossession = Possession(copy.copy(currentPlayersHome), \
                                              copy.copy(currentPlayersAway))
               else:
                   newPossession = Possession(copy.copy(currentPlayersAway), \
                                              copy.copy(currentPlayersHome))
               newPossession.addPoints(currentPoints)
               currentPoints = 0
               currentPossession.nextPossession = newPossession
               currentPossession = newPossession
               currentPlayersAway = copy.copy(nextPlayersAway)
               currentPlayersHome = copy.copy(nextPlayersHome)
               duringFreeThrows = 0
               if 'makes' in findAwayCol(row).text:
                   homeOnOff = not homeOnOff
        elif('makes' in findHomeCol(row).text or 'makes' in findAwayCol(row).text):
            if '2-pt' in findHomeCol(row).text or '2-pt' in findAwayCol(row).text:
                currentPoints = 2
            else:
                currentPoints = 3
            if homeOnOff:
                newPossession = Possession(copy.copy(currentPlayersHome), \
                                           copy.copy(currentPlayersAway))
            else:
                newPossession = Possession(copy.copy(currentPlayersAway), \
                                           copy.copy(currentPlayersHome))

            nextRow = row.find_next('tr')
            if nextRow == None or 'End of' in findAwayCol(nextRow).text\
               or (('makes' in findHomeCol(row).text and \
               'Shooting foul' not in findHomeCol(nextRow).text) or \
               ('makes' in findAwayCol(row).text and \
               'Shooting foul' not in findAwayCol(nextRow).text)):
                newPossession.addPoints(copy.copy(currentPoints))
                #print(newPossession)
                currentPoints = 0
                currentPossession.nextPossession = newPossession
                currentPossession = newPossession
                homeOnOff = not homeOnOff
        # elif 'Jump ball' in findAwayCol(row).text:
        #     jumpballPlayer = findAwayCol(row).find_next('a').find_next('a') \
        #                      .find_next('a').get('href')
        #     jumpballPlayer = jumpballPlayer[11:-5]
        #     if ((jumpballPlayer in currentPlayersAway) and \
        #        (homeOnOff)) or ((jumpballPlayer in currentPlayersHome) and \
        #        (not homeOnOff)):
        #        if homeOnOff:
        #            newPossession = Possession(copy.copy(currentPlayersHome), \
        #                                       copy.copy(currentPlayersAway))
        #        else:
        #            newPossession = Possession(copy.copy(currentPlayersAway), \
        #                                       copy.copy(currentPlayersHome))
        #        newPossession.addPoints(currentPoints)
        #        currentPoints = 0
        #        currentPossession.nextPossession = newPossession
        #        currentPossession = newPossession
        #        homeOnOff = not homeOnOff
        # else:
        #     print(findAwayCol(row).text + ' | ' + findHomeCol(row).text)

        row = row.find_next('tr')

    if homeOnOff:
        newPossession = Possession(copy.copy(currentPlayersHome), \
                                   copy.copy(currentPlayersAway))
    else:
        newPossession = Possession(copy.copy(currentPlayersAway), \
                                   copy.copy(currentPlayersHome))
    newPossession.addPoints(currentPoints)
    currentPoints = 0
    currentPossession.nextPossession = newPossession

    return (basePossession.nextPossession, amountOfErrors)
    #print(basePossession)
    # f = open('output.txt', 'w')
    # currentPossession = basePossession.nextPossession
    # while(currentPossession):
    #     result = "Offense: "
    #     for player in currentPossession.offPlayers:
    #         result = result + player + ' '
    #     result = result + "Defense: "
    #     for player in currentPossession.defPlayers:
    #         result = result + player + ' '
    #     result = result + "Result: " + str(currentPossession.end) + '\n'
    #     f.write(result)
    #     currentPossession = currentPossession.nextPossession
    # f.close()



def main():
    teams = ['MIL', 'GSW', 'TOR', 'UTA', 'HOU', 'POR', 'DEN', 'BOS', 'OKC', \
             'IND', 'PHI', 'SAS', 'LAC', 'ORL', 'MIA', 'BRK', 'DET', 'SAC', \
             'DAL', 'MIN', 'NOP', 'LAL', 'CHO', 'MEM', 'WAS', 'ATL', 'CHI', \
             'PHO', 'NYK', 'CLE']

    #(possessions, amountOfErrors) = scrapePossession('2019', '04', '05', 'CHO')
    columnNames = ['offense1', 'offense2', 'offense3', 'offense4', 'offense5',\
                   'defense1', 'defense2', 'defense3', 'defense4', 'defense5',\
                   'result']
    df = pd.DataFrame(columns = columnNames)

    i = 0
    year = 2018
    month = 10
    day = 16
    while(True):
        strYear = str(year)
        if month < 10:
            strMonth = "0" + str(month)
        else:
            strMonth = str(month)
        if day < 10:
            strDay = "0" + str(day)
        else:
            strDay = str(day)
        for team in teams:
            (possessions, amountOfErrors) = \
                          scrapePossession(strYear, strMonth, strDay, team)
            time.sleep(2)
            if amountOfErrors == 0:
                if possessions != None:
                    print('no error: ' + strYear + strMonth + strDay + team)
                else:
                    print('no game: ' + strYear + strMonth + strDay + team)
                while(possessions):
                    df.loc[i] = possessions.offPlayers + possessions.defPlayers + [possessions.end]
                    possessions = possessions.nextPossession
                    i += 1
            else:
                print('error occurred: ' + strYear + strMonth + strDay + team)
        if day == 31:
            day = 1
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
        else:
            day += 1

        if month == 4 and day == 12 and year == 2019:
            break

    df.to_csv('output.csv', index=False)
if __name__ == '__main__':
    main()
