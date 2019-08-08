from bs4 import BeautifulSoup as bsoup
import urllib.request
import pandas as pd
import numpy as np
import time

def scrapePlayer(player):
    myUrl = 'https://www.basketball-reference.com/players/' + \
            player[0] + '/' + player + '.html'

    client = urllib.request.urlopen(myUrl).read()
    soup = bsoup(client, 'lxml')
    body = soup.body

    div = body.find(id = 'all_advanced')
    div = div.find_next('div').next_sibling.next_sibling.next_sibling.next_sibling
    strTable = str(div)
    newSoup = bsoup(strTable, 'lxml')
    newBody = newSoup.body
    tableBody = newBody.find('tbody')
    tableRow = tableBody.find_next(id = 'advanced.2019')
    obpm = float(tableRow.find_next('td', {'data-stat' : 'dws'}).text)
    dbpm = float(tableRow.find_next('td', {'data-stat' : 'ows'}).text)
    return (obpm, dbpm)


def main():
    players = {}
    dfpossessions = pd.read_csv('output.csv')
    columnNames = ['offense1', 'offense2', 'offense3', 'offense4', 'offense5',\
                   'defense1', 'defense2', 'defense3', 'defense4', 'defense5']
    highestPlayer = '01'
    for col in columnNames:
        posplayers = (dfpossessions[col].tolist())
        for player in posplayers:
            if int(player[-2:]) > int(highestPlayer[-2:]):
                highestPlayer = player
            if player not in players:
                print('new player ' + player)
                time.sleep(2)
                (obpm, dbpm) = scrapePlayer(player)
                players[player] = (obpm, dbpm, 1)
            else:
                (obpm, dbpm, numOfPos) = players[player]
                players[player] = (obpm, dbpm, numOfPos + 1)
                print(player + ' ' + str(numOfPos + 1))

    # (obpm, dbpm) = scrapePlayer('butleji01')
    # players['butleji01'] = (obpm, dbpm, 1)
    # players['butleji01'] = scrapePlayer('butleji01')
    columnNames = ['playerid', 'offense', 'defense', 'numOfPos']
    i = 0
    dfplayers = pd.DataFrame(columns = columnNames)
    for player in players:
        (obpm, dbpm, numOfPos) = players[player]
        dfplayers.loc[i] = [player, obpm, dbpm, numOfPos]
        i += 1

    dfplayers.to_csv('players.csv', index=False)
    print('player with highest number: ' + highestPlayer)


if __name__ == '__main__':
    main()
