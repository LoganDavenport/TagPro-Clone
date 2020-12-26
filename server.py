import socket, pickle, packet, time

class Server:

    def __init__(self, ip, port):
        self.address = (ip, port)
        self.sock = socket.create_server(self.address)
        self.sock.setblocking(False)
        self.game_map = [[1,1,1,1,1,1,1], # 0 is floor, 1 is wall, 2 is flag
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,2,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,0,0,0,0,0,1],
                         [1,1,1,1,1,1,1]]
        self.game_state = packet.GameState({}, self.game_map)
        self.last_tick_time = 0
        self.players = []
    
    def add_player(self, conn, addr, name):
        self.players.append((conn, addr, name, -1))
    
    # accepts someone trying to join the server
    def accept_players(self):
        try:
            conn, addr = self.sock.accept()
            self.players.append((conn, addr, "", -1))
        except:
            pass
    
    def check_players(self):
        i = 0
        while i < len(self.players):
            conn, addr, name, inpt = self.players[i]
            try:
                pkt = pickle.loads(conn.recv(500))
                if(pkt.kind == packet.Kind.NAME):
                    self.players[i] = (conn, addr, pkt.message, inpt)
                    self.game_state.players[pkt.message] = ((3,1), 0, False)
                    print("{} connected from {}.".format(pkt.message, addr))
                elif(pkt.kind == packet.Kind.END):
                    self.players.remove((conn, addr, name, inpt))
                    self.game_state.players.pop(name)
                    i -= 1
                    print("{} disconnected.".format(name))
                else:
                    new_input = -1
                    if pkt.message == "d":
                        new_input = 0
                    elif pkt.message == "w":
                        new_input = 1
                    elif pkt.message == "a":
                        new_input = 2
                    elif pkt.message == "s":
                        new_input = 3
                    self.players[i] = (conn, addr, name, new_input)
            except:
                pass
            i += 1
    
    def is_valid(self, y, x):
        return self.game_map[y][x] != 1
    
    def update_game(self):
        for i in range(len(self.players)):
            (conn, addr, name, inpt) = self.players[i]
            (y,x), c, f = self.game_state.players[name]
            dy = -1 if inpt == 1 else 1 if inpt == 3 else 0
            dx = 1 if inpt == 0 else -1 if inpt == 2 else 0
            if(self.is_valid(y+dy, x+dx)):
                self.game_state.players[name] = ((y+dy,x+dx), c, f)
            self.players[i] = (conn, addr, name, -1)
    
    def broadcast_game(self):
        pkt = packet.Packet(packet.Kind.GAME_STATE, "", self.game_state)
        data = pickle.dumps(pkt)
        for (conn, addr, name, inpt) in self.players:
            try:
                conn.send(data)
            except:
                pass
    
    def loop(self):
        cur_time = time.time_ns()/1000000
        self.accept_players()
        self.check_players()
        if(cur_time - self.last_tick_time >= 125): # one tick has passed
            self.last_tick_time = cur_time
            self.update_game()
            self.broadcast_game()
        

def main():
    server = Server("127.0.0.1", 8080)
    while True:
        server.loop()

        
if __name__ == "__main__":
    main()
    
