import socket
import threading
import helper
from donotmodify import *

clients = []
ack_count = 0

input_targets = []
op_targets = []

inputs = []



def handle_client(connection, client_address, dma_socket):
    try:
        # print("Connected to", client_address)
        clients.append(connection)
        while True:
            data = connection.recv(1024)
            if data:
                #print(data[helper.SIGLEN:])
                #store the input targets in dram
                if b'QUEUE:DATA' in data:
                    d = data[helper.SIGLEN + 11:]
                    input_targets.append(d)
                #store the operation targets in dram
                if b'ACK:Node Op' in data:
                    d = data.split(b':')[2]  
                    op_targets.append(d.split(b':')[0])

                #If execution of the node graph is done, 
                # the single steps are still saved in the dram but not encrypted
                # we ask the dma to fetch the data from the dram and send it to us 
                if b'DMA:OUT' in data:
                    # print(input_targets)
                    # print(op_targets)
                    #create 4 new messages for each of the numbers
                    #D1 can be recovered from IN1
                    out_reg = data[helper.SIGLEN + 8:]
                    
                    
                    #first input 
                    new_msg = data
                    new_msg = new_msg.replace(out_reg, op_targets[0])
                    dma_socket.sendall(new_msg)
                    msg = dma_socket.recv(1024)
                    ab1 = float(msg.split(b':')[1])
                    inputs.append(-ab1)

                    #second input
                    new_msg = data 
                    new_msg = new_msg.replace(out_reg, op_targets[2])
                    dma_socket.sendall(new_msg)
                    msg = dma_socket.recv(1024)
                    s1 = float(msg.split(b':')[1])
                    inputs.append(ab1 - s1)

                    #third input
                    new_msg = data
                    new_msg = new_msg.replace(out_reg, op_targets[3])
                    dma_socket.sendall(new_msg)
                    msg = dma_socket.recv(1024)
                    s2 = float(msg.split(b':')[1])
                    inputs.append(s1 - s2)

                    #fourth input
                    new_msg = data
                    new_msg = new_msg.replace(out_reg, op_targets[5])
                    dma_socket.sendall(new_msg)
                    msg = dma_socket.recv(1024)
                    a1 = float(msg.split(b':')[1])
                    inputs.append(a1 - inputs[2])

                    #output
                    ab2 = abs(s2)
                    res = ab2 + a1
                    inputs.append(res)
                    print(inputs)






                    

                # If the incoming request is a DMA command, the hypervisor
                # sends it to the dma controller
                if b'DMA:IN' in data or b'DMA:OUT' in data:
                    # print(data)
                    # #print(confidential)
                    # input_ = data[helper.SIGLEN + 12:]
                    # print(input_)
                    # #convert binary to string
                
                    # input_ = input_.decode()
                    # print(input_)


                    #print(data[helper.SIGLEN:])
                    dma_socket.sendall(data)
                    msg = dma_socket.recv(1024)
                    connection.sendall(b'\x00'*helper.SIGLEN+msg)
                else:
                    relay_message(connection, data)
            else:
                break
    finally:
        # print("Connection closed with", client_address)
        connection.close()

def relay_message(sender, message): # Relays the message to the guest or to the gpu
    for client in clients:
        if client != sender:  
            try:
                client.sendall(message)
            except Exception:
                client.close()
                clients.remove(client)

def start_hypervisor():
    dma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dma_address = ('localhost', DMASOCKET)
    helper.connect(dma_socket,dma_address)

    hypervisor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hypervisor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    hypervisor_address = ('localhost', SOCKET)
    hypervisor_socket.bind(hypervisor_address)
    hypervisor_socket.listen(2)
    # print("Hypervisor is listening on", hypervisor_address)

    while True:
        connection, client_address = hypervisor_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(connection, client_address, dma_socket))
        client_thread.start()

if __name__ == "__main__":
    start_hypervisor()



