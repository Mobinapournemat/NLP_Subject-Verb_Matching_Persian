# bazi tak nafare + message dar halate tak nafare + bazi 2 nafare + message dar halate 2 nafare
# vaqti yek bazikon nobatesh bashe mitone /message ro vared kone va bad payam hash ro benevise va dar akhar ham /end_message ro bezane


import socket
import threading



host = '127.0.0.1'
port = 8550

web_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
web_serv.bind((host, port))
web_serv.listen()
print("Web Server is listening...") 

clients = []
usernames = []
idle_game_servers = []
client_server = []
dual_game_waiters = []
dual_game_pairs = []
temp = []

def get_opponent(client, dual_game_waiters):
    for c in dual_game_waiters:
        if c != client:
            return c

def handle_dual_end_game(client, opponent, dual_game_pairs, idle_game_servers):
    for pair in dual_game_pairs:
        if pair[0] == client and pair[1] == opponent:
            idle_game_servers.append(pair[2])
            dual_game_pairs.remove((client, opponent, pair[2]))
    return dual_game_pairs, idle_game_servers

def dual_mode_game(client, client_server, dual_game_pairs, temp, idle_game_servers):  
    dual_game_waiters.append(client)
    if len(dual_game_waiters) < 2:
        g_server = client_has_serevr(client, client_server) 
        if g_server is False:
            client.send('Waiting for an idle Game Server...'.encode('ascii')) 
        while True:
            if g_server != False:
                g_server.send('Reset_board'.encode('ascii'))
                break
            if  len(idle_game_servers) > 0: 
                g_server = idle_game_servers.pop()
                client_server.append((client, g_server))
                g_server.send('Reset_board'.encode('ascii'))
                message = 'Successfully connected to a Game Server! \nYou are player X and your input should be like: "0 1" (first row, second column) \0'
                client.send(message.encode('ascii'))
                break
        client.send("Looking for an online player...".encode('ascii'))  
        # msg = client.recv(1024).decode('ascii')
        # if msg == '/change':
        #     dual_game_waiters.remove(client)
        #     handle_client(client, client_server)
        while True:
            # if client.recv(1024).decode('ascii') == '/change': 
            #     dual_game_waiters.remove(client)
            #     handle_client(client, client_server)
            if len(dual_game_waiters) > 1:
                opponent = dual_game_waiters[-1]
                client.send('Your Opponent is ready!'.encode('ascii')) 
                opponent.send('You are player O and your input should be like: "0 1" (first row, second column)'.encode('ascii'))
                dual_game_pairs.append((client, opponent, g_server)) 
                break
        dual_game_waiters.remove(client)
        dual_game_waiters.remove(opponent) 
        while True: 
            try:
                g_server.send('get_board'.encode('ascii'))
                game_board = g_server.recv(1024).decode('ascii')
                game_board = 'board' + game_board
                client.send(game_board.encode('ascii'))
                coord = client.recv(1024).decode('ascii')
                coord = check_message(client, opponent, coord)
                if coord == '/exit':
                    opponent.send('\0 Your Opponent Disconnected!'.encode('ascii'))
                    client_server.remove((client, g_server))
                    dual_game_pairs, idle_game_servers = handle_dual_end_game(client, opponent, dual_game_pairs, idle_game_servers)
                    temp.append(0)
                    raise
                coord = 'X_put' + coord
                g_server.send(coord.encode('ascii'))
                win = g_server.recv(1024).decode('ascii')
                if win in ['X', 'D']:
                    g_server.send('get_board'.encode('ascii')) 
                    game_board = g_server.recv(1024).decode('ascii')
                    if win == 'X':
                        message = 'board' + game_board + '\0' + 'Player ' + win + ' Won!\n'
                    else:
                        message = 'board' + game_board + '\0' + 'Draw! No winner...\n'
                    client.send(message.encode('ascii'))
                    opponent.send(message.encode('ascii'))
                    temp.append(0)
                    dual_game_pairs, idle_game_servers = handle_dual_end_game(client, opponent, dual_game_pairs, idle_game_servers)
                    client_server.remove((client, g_server))
                    handle_client(client, client_server)
                    return
                g_server.send('get_board'.encode('ascii'))
                game_board = g_server.recv(1024).decode('ascii')
                game_board = 'board' + game_board
                opponent.send(game_board.encode('ascii'))
                coord = opponent.recv(1024).decode('ascii')
                coord = check_message(client, opponent, coord)  
                if coord == '/exit':
                    client.send('\0 Your Opponent Disconnected!'.encode('ascii'))
                    i = clients.index(opponent)
                    name = usernames[i] 
                    print(f'Client {name} Disconnected!')
                    clients.pop(i)
                    usernames.pop(i)
                    client_server.remove((client, g_server)) 
                    t = []
                    for pair in dual_game_pairs:
                        if pair[1] == opponent:
                            idle_game_servers.append(pair[2])
                        else:
                            t.append(pair)
                    dual_game_pairs = t
                    handle_client(client, client_server)
                elif coord == '/message':
                    client.send(coord.encode('ascii')) 
                coord = 'O_put' + coord
                g_server.send(coord.encode('ascii'))
                win = g_server.recv(1024).decode('ascii')
                if win in ['O', 'D']:
                    g_server.send('get_board'.encode('ascii')) 
                    game_board = g_server.recv(1024).decode('ascii')
                    if win == 'O':
                        message = 'board' + game_board + '\0' + 'Player ' + win + ' Won!\n'
                    else:
                        message = 'board' + game_board + '\0' + 'Draw! No winner...\n'
                    client.send(message.encode('ascii'))
                    opponent.send(message.encode('ascii'))
                    temp.append(0)
                    dual_game_pairs, idle_game_servers = handle_dual_end_game(client, opponent, dual_game_pairs, idle_game_servers) 
                    client_server.remove((client, g_server)) 
                    handle_client(client, client_server)
                    return
            except:
                i = clients.index(client)
                name = usernames[i] 
                print(f'Client {name} Disconnected!')
                clients.pop(i)
                usernames.pop(i)
                t = []
                for pair in dual_game_pairs:
                    if pair[0] == client:
                        idle_game_servers.append(pair[2])
                    else:
                        t.append(pair)
                dual_game_pairs = t
                client.close()
                exit()
    else:
        while True:
            if len(temp) > 0: 
                print(len(temp))
                for item in temp:
                    temp.remove(item)
                handle_client(client, client_server) 
                break
            



def client_has_serevr(client, client_server):
    for pair in client_server:
        if pair[0] == client:
            return pair[1]
    return False

def check_message(client, g_server, input): 
    if input != '/message':
        return input
    input = client.recv(1024).decode('ascii')
    while input != '/end_message':
        g_server.send(input.encode('ascii'))
        input = client.recv(1024).decode('ascii')
    input = client.recv(1024).decode('ascii')
    input = check_message(client, g_server, input)
    return input


def single_mode_game(client, client_server, idle_game_servers):
    g_server = client_has_serevr(client, client_server) 
    if g_server is False:
        client.send('Waiting for an idle Game Server...'.encode('ascii')) 
    while True:
        if g_server != False:
            g_server.send('Reset_board'.encode('ascii'))
            break
        if  len(idle_game_servers) > 0: 
            g_server = idle_game_servers.pop()
            g_server.send('Reset_board'.encode('ascii')) 
            client_server.append((client, g_server))
            message = 'Successfully connected to a Game Server! \nYou are player X and your input should be like: "0 1" (first row, second column) \0'
            client.send(message.encode('ascii'))
            break
    while True:
        try:
            g_server.send('get_board'.encode('ascii'))
            game_board = g_server.recv(1024).decode('ascii')
            game_board = 'board' + game_board
            client.send(game_board.encode('ascii'))
            coord = client.recv(1024).decode('ascii')
            coord = check_message(client, g_server, coord)
            if coord == '/exit':
                raise
            coord = 'put' + coord
            g_server.send(coord.encode('ascii'))
            win = g_server.recv(1024).decode('ascii')
            if win in ['X', 'O']:
                g_server.send('get_board'.encode('ascii'))
                game_board = g_server.recv(1024).decode('ascii')
                game_board = 'board' + game_board + '\0' + 'Player ' + win + ' Won!\n'
                client.send(game_board.encode('ascii'))
                handle_client(client, client_server)
            elif win == 'D':
                g_server.send('get_board'.encode('ascii'))
                game_board = g_server.recv(1024).decode('ascii')
                game_board = 'board' + game_board + '\0' + 'Draw! No winner...\n'
                client.send(game_board.encode('ascii'))
                handle_client(client, client_server)
        except:
            i = clients.index(client)
            name = usernames[i] 
            print(f'Client {name} Disconnected!')
            clients.pop(i)
            usernames.pop(i)
            temp = []
            for pair in client_server:
                if pair[0] == client:
                    idle_game_servers.append(pair[1])
                else:
                    temp.append(pair)
            client_server = temp
            client.close()
            exit()



def check_client_exit(client, command, client_server):
    if command != '/exit':
        return False
    try:
        i = clients.index(client)
        name = usernames[i]
        print(f'Client {name} Disconnected!')
        clients.pop(i)
        usernames.pop(i)
        temp = []
        for pair in client_server:
            if pair[0] == client:
                idle_game_servers.append(pair[1])
            else:
                temp.append(pair)
        client_server = temp
        client.close()
        return True
    except:
        pass




def handle_client(client, client_server):
    try:
        message = ' 1. Play with Computer \n 2. Play with an online player'
        client.send(message.encode('ascii'))
        game_mode = client.recv(1024).decode('ascii')
        if game_mode == '/exit':                                          
            i = clients.index(client)
            name = usernames[i]
            print(f'Client {name} Disconnected!')
            clients.pop(i)
            usernames.pop(i)
            client.close()
            exit()
        if str(game_mode) == '2':
            dual_mode_game(client, client_server, dual_game_pairs, temp, idle_game_servers) 
        else:
            single_mode_game(client, client_server, idle_game_servers)
    except:
        pass



def receive():
    while True:
        client, address = web_serv.accept()
        client.send('Type'.encode('ascii'))
        type = client.recv(1024).decode('ascii')
        check_client_exit(client, type, client_server)
        if type == 'Client':
            message = 'Username'
            client.send(message.encode('ascii'))
            username = client.recv(1024).decode('ascii')
            check_client_exit(client, username, client_server)
            usernames.append(username)
            clients.append(client)
            c_thread = threading.Thread(target=handle_client, args=(client,client_server))
            c_thread.start()
        else: 
            idle_game_servers.append(client)
        
        print(f"New {type} with address{address} connected!")
        

def write():
    while True:
        command = input()
        if command == '/users':
            print(f'{len(clients)} Online Player!')



receive_thred = threading.Thread(target=receive)
receive_thred.start()

write_thred = threading.Thread(target=write)
write_thred.start()
