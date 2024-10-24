import pickle
import socket
import threading
import helper
from donotmodify import *

def dma_controller_init():
    dram = { # GPU memory
        "M1" : -1,   "M2" : -1,
        "M3" : -1,   "M4" : -1,
        "M5" : -1,   "M6" : -1,
        "M7" : -1,   "M8" : -1,
        "M9" : -1,   "M10" : -1,
        "M11" : -1,  "M12" : -1,
        "M13" : -1,  "M14" : -1,
        "M15" : -1,  "M16" : -1,
        "M17" : -1,  "M18" : -1,
        "M19" : -1,  "M20" : -1,
    }

    with open('keys/dram.pkl', 'wb') as f:
        pickle.dump(dram,f)

def do_dma(msg): # DMA operations on GPU memory
    command = msg[128:]
    command_split = command.split(b":")
    len_command_split = len(command_split)
    dma_direction = command_split[1]

    if len_command_split < 3:
        err_msg = f"ERROR:DMA command is expecting at least 3 arguments and received {len_command_split}"
        return err_msg.encode()

    match dma_direction:
        case b"IN": # Writes to GPU memory
            with open('keys/dram.pkl', 'rb') as f:
                dram = pickle.load(f)

            target = command_split[2].decode()
            if target not in dram:
                err_msg = f"ERROR:DMA:IN command is modifying value at {target}, but {target} does not exist"
                return err_msg.encode()

            value = b":".join(command_split[3:])
            # Writes a byte string to the memory address "target"
            dram[target] = value

            with open('keys/dram.pkl', 'wb') as f:
                pickle.dump(dram,f)

        case b"OUT": # Reads GPU memory
            with open('keys/dram.pkl', 'rb') as f:
                dram = pickle.load(f)

            target = command_split[2].decode()
            if target not in dram:
                err_msg = f"ERROR:DMA:OUT command is asking for value at {target}, but {target} does not exist"
                return err_msg.encode()

            value = dram[target]

            err_msg = b"DMA-OUT-DONE:"+value
            return err_msg
        case _:
            err_msg = f"ERROR:Unknown DMA direction {dma_direction}"
            return err_msg.encode()
    return b"DMA-DONE"


def handle_dma_requests(connection, client_address):
    try:
        # print("Connected to", client_address)
        while 1:
            msg = connection.recv(1024)
            if msg:
                reply = do_dma(msg)
                connection.sendall(reply)
            else:
                print("ERROR: No msg received")
    finally:
        # print("Connection closed with", client_address)
        connection.close()

def dma_controller():
    dma_controller_init()

    dma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    dma_address = ('localhost', DMASOCKET)
    dma_socket.bind(dma_address)
    dma_socket.listen(1)
    # print("DMA Controller is listening on", dma_address)

    while True:
        connection, client_address = dma_socket.accept()
        client_thread = threading.Thread(target=handle_dma_requests, args=(connection, client_address))
        client_thread.start()

if __name__ == "__main__":
    dma_controller()
