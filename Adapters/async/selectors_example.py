import selectors
from time import sleep

sel = selectors.DefaultSelector()

def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()

def accept():
    print("Start accept")
    sleep(5)
    print("Stop accept")

def accept_2():
    print("Start accept 2")
    sleep(3)
    print("Stop accept 2")


sel.register(None, selectors.EVENT_READ, accept)
sel.register(None, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    print(f"Events : {events}")
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)