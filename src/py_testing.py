import pyautogui as pa
import time
import os
import pickle

PROCESSOR_SPEED = 1
INTERNET_SPEED = 2

os.popen('"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"')
time.sleep(PROCESSOR_SPEED)
pa.write('https://www.on.bet365.ca/#/AS/B17/')
pa.press('enter')

time.sleep(INTERNET_SPEED)

##########################################################################################

# IF NO URL IS BEING RETURNED INSIDE debug_one.py THERE MAY BE A GOOGLE CHROMEDRIVER UPDATE

##########################################################################################

from subprocess import STDOUT, Popen, PIPE

output = Popen(['python', 'src/debug_one.py'], stdout=PIPE, stderr = STDOUT)
new_url = ''

# https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
while True:
  line = output.stdout.readline()
  if 'https://' in str(line):
    new_url = str(line).replace("\\r\\n'", '').replace("b'", '')
    print(new_url)
    break
  if not line: break
  ...

pa.keyDown('ctrl')
pa.press('t')
pa.keyUp('ctrl')

pa.write(new_url)
pa.press('enter')

pa.keyDown('ctrl')
pa.keyDown('shift')
pa.press('tab')
pa.keyUp('shift')
pa.press('w')
pa.keyUp('ctrl')

time.sleep(INTERNET_SPEED)

output = Popen(['python', 'src/debug_two.py'], stdout=PIPE, stderr = STDOUT)
players = []

# https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
while True:
  line = output.stdout.readline()
  if 'EX' in str(line):
    player_string = str(line).replace("b'EX", '').replace("\\r\\n'", '').replace("\\xf6", 'ö')
    players = player_string.split('|')
    players.pop()
    print(players)
    break
  if not line: break
  ...

# Close Chrome window
pa.keyDown('ctrl')
pa.press('w')
pa.keyUp('ctrl')

# Order the list of players and teams so that each object starts with the teams player, following with the players in that game
games = []

for i in range(len(players)):
  if '@' in players[i]:
    new_game = [players[i]]

    i += 1
    for p in range(i, len(players)):
      if '@' not in players[p]:
        new_game.append(players[p])
      else:
        break

    games.append(new_game)
  else:
    continue

with open('./lib/games.pickle', 'wb') as f:
  pickle.dump(games, f)
  print('Pickled Games')

exit(0)


# os.popen('"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"')
# time.sleep(1)
# pa.write(new_url)
# pa.press('enter')

# time.sleep(2)