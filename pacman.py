import time


with open("ascii-art.txt") as file:
    pacmans = [part.strip("\n") for part in file.read().split("\n\n")]

x = 0
y = 0
while True:
    for pacman in pacmans[:-1] + pacmans[::-1][:-1]:
        print('\n' * 20)
        print(('\n' + pacman).replace('\n', '\n' + ' '*x))
        print('\n' * y, end='')
        time.sleep(1)
        x += 2
#        y += 1
