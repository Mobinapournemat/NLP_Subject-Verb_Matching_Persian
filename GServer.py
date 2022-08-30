import socket
import threading
import random


host = '127.0.0.1'
port = 8550

g_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
g_server.connect((host, port))

default_board = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
game_board = []


def get_str_of_board(board):
    temp = ''
    for row in board:
        temp += ' '.join(row) + '\n'
    return temp


def put(board, coord, item):
    ij = coord.split()
    i, j = int(ij[0]), int(ij[1])
    board[i][j] = item
    return board


def random_put(game_board):
    while True:
        i = random.randint(0, 2)
        j = random.randint(0, 2)
        if game_board[i][j] == '-':
            game_board = put(game_board, str(i) + ' ' + str(j), 'O')
            return game_board
    


def check_win(board):
    for row in board:
        result = all((element == row[0] and element != '-') for element in row)
        if result:
            return row[0]
    for i in range(3):
        result = (board[0][i] == board[1][i] == board[2][i]) and (board[0][i] != '-')
        if result:
            return board[0][i]
    result = ((board[0][0] == board[1][1] == board[2][2]) or (board[0][2] == board[1][1] == board[2][0])) and (board[1][1] != '-')
    if result:
        return board[1][1]
    draw = True
    for row in board:
        for elem in row:
            if elem == '-':
                draw = False
    result = 'D' if draw else False
    return result


def receive(game_board):
    while True:
        try:
            messages = g_server.recv(1024).decode('ascii').split('\0')
            for message in messages:
                if message == 'Type':
                    g_server.send('Game Server'.encode('ascii'))
                elif message == 'get_board':
                    board = get_str_of_board(game_board)
                    g_server.send(board.encode('ascii'))
                elif message[:3] == 'put':
                    coord = message[3:]
                    game_board = put(game_board, coord, 'X')
                    win = check_win(game_board)
                    if win is False:
                        game_board = random_put(game_board)
                        win = check_win(game_board)
                    g_server.send(str(win).encode('ascii'))
                elif message == 'Reset_board':
                    game_board = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
                elif message[1:5] == '_put':
                    coord = message[5:]
                    game_board = put(game_board, coord, message[0])
                    win = check_win(game_board)
                    g_server.send(str(win).encode('ascii'))
                else:
                    print(message)
        except:
            print('An Error occurred!')
            g_server.close()
            break


def write():
    while True:
        try:
            message = input()
            g_server.send(message.encode('ascii'))
        except:
            print('An Error occurred!')
            g_server.close()
            break


receive_thred = threading.Thread(target=receive, args=(game_board,))
receive_thred.start()

write_thred = threading.Thread(target=write)
write_thred.start()