from tkinter import *
import socket, pickle, packet, time, gc

class Client:

    def __init__(self):
        self.initUI()
        self.state = 0
        self.i = 0
        self.sock = None
        self.root.after(1, self.loop)
        self.root.mainloop()
    
    def initUI(self):
        self.root = Tk()
        self.root.title("TagPro Clone")
        self.root.minsize(800,400)
        self.root.bind("<Escape>", self.close)
        self.root.bind("z", self.send_input)
        self.root.bind("x", self.send_input)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
        self.game = Frame(self.root)
        self.drawing = Canvas(self.game, width=800, height=400)
        self.drawing.bind("w", self.send_input)
        self.drawing.bind("a", self.send_input)
        self.drawing.bind("s", self.send_input)
        self.drawing.bind("d", self.send_input)
        self.drawing.pack()
        self.game.grid(row=0, column=0, sticky="nsew")
        
        self.menu = Frame(self.root)
        Label(self.menu, text="IP").grid(row=0)
        self.ip = Entry(self.menu)
        self.ip.grid(row=0, column=1)
        Label(self.menu, text="Name").grid(row=1)
        self.name = Entry(self.menu)
        self.name.grid(row=1, column=1)
        Button(self.menu, text="Join Server", command=self.connect).grid(row=3)
        self.menu.grid(row=0, column=0, sticky="nsew")
        
    def connect(self):
        ip = port = None
        try:
            ip, port = self.ip.get().strip().split(":")
        except:
            ip = self.ip.get()
            port = "8080"
        if(ip == ""):
            return
        self.sock = socket.socket()
        address = (ip, int(port))
        self.sock.connect(address)
        name = self.name.get().strip()
        self.sock.send(pickle.dumps(packet.Packet(packet.Kind.NAME, name)))
        
        self.sock.setblocking(False)
        self.game_state = None
        self.last_tick_time = 0
        self.last_frame_time = 0
        self.switch_context()
        
    def switch_context(self):
        self.state = (self.state+1)%2
        if self.state == 0:
            self.menu.tkraise()
        else:
            self.game.tkraise()
            self.drawing.focus_set()
        
        
    def close(self, *args):
        if(self.sock is not None):
            self.sock.send(pickle.dumps(packet.Packet(packet.Kind.END)))
            self.sock.close()
        self.root.destroy()
    
    def send_input(self, event):
        if self.sock is not None:
            self.sock.send(pickle.dumps(packet.Packet(packet.Kind.INPUT, event.char)))
    
    def draw_frame(self):
        self.drawing.delete("all")
        if(self.game_state is not None):
            for y in range(len(self.game_state.game_map)):
                row = self.game_state.game_map[y]
                for x in range(len(row)):
                    color = "gray88" if row[x] == 0 else "gray28" if row[x] == 1 else "lawn green"
                    self.drawing.create_rectangle(x*20,y*20,x*20+20,y*20+20, fill=color)
            for name in self.game_state.players:
                (y,x), color, flag = self.game_state.players[name]
                self.drawing.create_rectangle(x*20,y*20,x*20+20,y*20+20, 
                                                fill="blue" if color else "red")
                if flag:
                    self.drawing.create_rectangle(x*20+10, y*20, x*20+20, y*20+10, fill="lawn green")
    
    def loop(self):
        cur_time = time.time_ns()/1000
        if(self.state == 1 and cur_time - self.last_tick_time > 115):
            try:
                self.last_tick_time = cur_time
                self.game_state = pickle.loads(self.sock.recv(5000)).state
                self.draw_frame()
            except BlockingIOError:
                pass
        self.root.after(1, self.loop)
        
        
def main():
    client = Client()
    

if __name__ == "__main__":
    main()
        
        