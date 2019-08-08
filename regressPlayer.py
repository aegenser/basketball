import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def main():
    # currentPlayer = 'linje01'
    playersOff = {}
    playersDef = {}
    playersPos = {}
    dfplayers = pd.read_csv('players.csv')
    dfpossessions = pd.read_csv('output.csv')
    columnNames = ['skill', 'result']
    columnNames2 = ['name', 'offense', 'defense']
    # dfplayerOff = pd.DataFrame(columns = columnNames)
    # dfplayerDef = pd.DataFrame(columns = columnNames)
    dfplayersNew = pd.DataFrame(columns = columnNames2)

    i = 0
    while(True):
        try:
            player = dfplayers.loc[i].tolist()
        except:
            break

        playersOff[player[0]] = player[1]
        playersDef[player[0]] = player[2]
        playersPos[player[0]] = player[3]
        i += 1

    #print(dfpossessions.loc[0].tolist()[:-1])
    # defSkillResult = {}
    # offSkillResult = {}
    players2 = {}
    for currentPlayer in playersPos:
        if playersPos[currentPlayer] > 12000 or \
        ((playersOff[currentPlayer] + playersDef[currentPlayer]) > 5 and playersPos[currentPlayer] > 1000):
            i = 0
            skillDef = {}
            skillOff = {}
            while(True):
                try:
                    playersInPossession = dfpossessions.loc[i].tolist()
                except:
                    break

                playersOnOffense = playersInPossession[:5]
                playersOnDefense = playersInPossession[5:-1]
                result = playersInPossession[-1]
                skill = 0
                if currentPlayer in playersOnOffense:
                    for player in playersOnOffense:
                        if player != currentPlayer:
                            skill += playersOff[player]
                    # for player in playersOnDefense:
                    #     skill -= playersDef[player]

                    skill = round(skill,1)
                    #print(skill)
                    if skill not in skillOff:
                        skillOff[skill] = (result, 1)
                    else:
                        (currentTotal, n) = skillOff[skill]
                        skillOff[skill] = (currentTotal + result, n + 1)

                if currentPlayer in playersOnDefense:
                    for player in playersOnDefense:
                        if player != currentPlayer:
                            skill += playersDef[player]
                    # for player in playersOnOffense:
                    #     skill -= playersOff[player]

                    #skill = round(skill,1)
                    #print(skill)
                    if skill not in skillDef:
                        skillDef[skill] = (result, 1)
                    else:
                        (currentTotal, n) = skillDef[skill]
                        skillDef[skill] = (currentTotal + result, n + 1)
                i += 1

            dfplayerDef = pd.DataFrame(columns = columnNames)
            i = 0
            for skill in skillDef:
                (totalResult, n) = skillDef[skill]
                if n > 10:
                    dfplayerDef.loc[i] = [round(skill,1), totalResult / n]
                    i += 1

            dfplayerOff = pd.DataFrame(columns = columnNames)
            i = 0
            for skill in skillOff:
                (totalResult, n) = skillOff[skill]
                if n > 10:
                    dfplayerOff.loc[i] = [round(skill,1), totalResult / n]
                    i += 1

            x1 = dfplayerDef['skill']
            y1 = dfplayerDef['result']

            x1 = x1.reshape(-1, 1)
            y1 = y1.reshape(-1, 1)

            regrDef = LinearRegression()
            regrDef.fit(x1, y1)

            x2 = dfplayerOff['skill']
            y2 = dfplayerOff['result']

            x2 = x2.reshape(-1, 1)
            y2 = y2.reshape(-1, 1)

            regrOff = LinearRegression()
            regrOff.fit(x2, y2)

            print(currentPlayer)
            players2[currentPlayer] = (regrOff.predict(0)[0][0], regrDef.predict(0)[0][0])

    i = 0
    for player in players2:
        (offense, defense) = players2[player]
        dfplayersNew.loc[i] = [player, offense, defense]
        i += 1

    dfplayersNew.to_csv('playersRegressed.csv', index=False)

if __name__ == '__main__':
    main()
