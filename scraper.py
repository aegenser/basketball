from bs4 import BeautifulSoup as bsoup
import urllib.request

def findAwayCol(row):
    return row.find_next('td').find_next('td')

def findHomeCol(row):
    return row.find_next('td').find_next('td').find_next('td').find_next('td')\
           .find_next('td').find_next('td')

def findOffenseCol(row, homeOnOff):
    if homeOnOff:
        return findHomeCol(row)
    else:
        return findAwayCol(row)

def findDefenseCol(row, homeOnOff):
    if homeOnOff:
        return findAwayCol(row)
    else:
        return findHomeCol(row)

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

            return result + ' ; ' + str(self.nextPossession)

    def addPoints(self, end):
        self.end += end

def scrapePossession(year, month, day, team):

    myUrl = 'https://www.basketball-reference.com/boxscores/pbp/' \
             + year + month + day + '0' + team + '.html'

    client = urllib.request.urlopen(myUrl).read()
    soup   = bsoup(client, 'lxml')
    body   = soup.body
    table  = body.find(id = 'div_pbp')
    row    = table.find_next('tr').find_next('tr').find_next('tr')\
             .find_next('tr')

    (awayStarters, homeStarters) = scrapeStarters(year, month, day, team)
    #homeOnOff -- true if Home team is on offense, false if Home team is on defense
    #jumpballResult -- true if home team got it, false if away team got it
    duringFreeThrows = False

    basePossession = Possession([],[])
    currentPossession = basePossession

    jumpballPlayer = findAwayCol(row).find_next('a').find_next('a') \
                     .find_next('a').get('href')
    jumpballPlayer = jumpballPlayer[11:-5]

    currentPoints      = 0
    currentPlayersAway = awayStarters
    nextPlayersAway    = awayStarters
    currentPlayersHome = homeStarters
    nextPlayersHome    = homeStarters

    if jumpballPlayer in homeStarters:
        jumpballResult = True
        homeOnOff = True
    else:
        jumpballResult = False
        homeOnOff = False

    row = row.find_next('tr')
    while((findAwayCol(row).string == None) or \
          ("End of 4th" not in findAwayCol(row).string)):
        if((findAwayCol(row).string != None) \
           and ("End of" in findAwayCol(row).string)):

            if homeOnOff:
                newPossession = Possession(currentPlayersHome, currentPlayersAway)
            else:
                newPossession = Possession(currentPlayersAway, currentPlayersHome)
            newPossession.addPoints(currentPoints)
            currentPossession.nextPossession = newPossession
            currentPossession = newPossession
            currentPlayersAway = nextPlayersAway
            currentPlayersHome = nextPlayersHome
            row = row.find_next('tr')
            if("End of 2nd" in findAwayCol(row).string):
                homeOnOff = jumpballResult
            else:
                homeOnOff = not jumpballResult
        elif((findAwayCol(row).text != None) \
             and ("enters" in findAwayCol(row).text)):
            playerIn = findAwayCol(row).find_next('a')
            playerOut = playerIn.find_next('a')
            playerIn = playerIn.get('href')[11:-5]
            playerOut = playerOut.get('href')[11:-5]
            print("sub " + playerIn + " for " + playerOut)
            if playerIn in currentPlayersAway:
                print("error, double player")
                break
            if not duringFreeThrows:
                for i in range(5):
                    if(currentPlayersAway[i] == playerOut):
                        currentPlayersAway[i] = playerIn
                        break
                nextPlayersAway = currentPlayersAway
            print(currentPlayersAway)
        elif((findHomeCol(row).text != None) \
             and ("enters" in findHomeCol(row).text)):
            playerIn = findHomeCol(row).find_next('a')
            playerOut = playerIn.find_next('a')
            playerIn = playerIn.get('href')[11:-5]
            playerOut = playerOut.get('href')[11:-5]
            print("sub " + playerIn + " for " + playerOut)
            if playerIn in currentPlayersAway:
                print("error, double player")
                break
            if not duringFreeThrows:
                for i in range(5):
                    if(currentPlayersHome[i] == playerOut):
                        currentPlayersHome[i] = playerIn
                        break
                nextPlayersHome = currentPlayersHome
            print(currentPlayersHome)
        row = row.find_next('tr')

    print(basePossession)




def scrapeStarters(year, month, day, team):

    myUrl = 'https://www.basketball-reference.com/boxscores/' \
             + year + month + day + '0' + team + '.html'

    playersHome = []
    playersAway = []

    client = urllib.request.urlopen(myUrl).read()
    soup = bsoup(client, 'lxml')
    body = soup.body
    div = body.find(id='all_four_factors')

    table = div.next_sibling.next_sibling.next_sibling.next_sibling
    row = table
    for i in range(5):
        row = row.find_next( scope = 'row' )
        playersAway.append(row.get('data-append-csv'))

    table = table.next_sibling.next_sibling.next_sibling.next_sibling
    row = table
    for i in range(5):
        row = row.find_next( scope = 'row' )
        playersHome.append(row.get('data-append-csv'))

    return (playersAway, playersHome)

def main():
    scrapePossession('2016', '11', '04', 'DAL')

if __name__ == '__main__':
    main()
