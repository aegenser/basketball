from bs4 import BeautifulSoup as bsoup
import urllib.request

myUrl = 'https://www.basketball-reference.com/boxscores/201706010GSW.html'

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
print(table.get('id'))
row = table
for i in range(5):
    row = row.find_next( scope = 'row' )
    playersHome.append(row.get('data-append-csv'))

for player in playersAway:
    print(player, end = ' ')
print('')
for player in playersHome:
    print(player, end = ' ')
print('')
