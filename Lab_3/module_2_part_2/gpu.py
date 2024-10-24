import socket
import helper
from donotmodify import *
import pickle

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

class Node:
    def __init__(self, op_type, parents, addr):
        self.op_type = op_type
        self.addr = addr
        self.parents = parents

op_names = []
compute_graph = {}
queue_started = 0
confidential = 0

def find_free_addr():
    with open('keys/dram.pkl', 'rb') as f:
        dram = pickle.load(f)
     
    for d in dram:
        # -1 means that the address is not being used
        # DMA requests cannot set the address to unused (-1) since they only allow to write bytes strings.
        if dram[d] == -1: 
            dram[d] = 0
            with open('keys/dram.pkl', 'wb') as f:
                pickle.dump(dram,f)
            return d

    print("ERROR: Memory space exhausted")
    exit(-1)

def read_mem(addr):
    with open('keys/dram.pkl', 'rb') as f:
        dram = pickle.load(f)

    if not addr in dram:
        print(f"Invalid read: address {addr} does not exist")
        exit(-1)

    value = dram[addr]

    return value

def write_mem(addr, value):
    with open('keys/dram.pkl', 'rb') as f:
        dram = pickle.load(f)

    if not addr in dram:
        print(f"Invalid write: address {addr} does not exist")
        exit(-1)
    
    if not isinstance(value,bytes):
        # Writes a byte string to the memory address
        value = str(value).encode() 
    dram[addr] = value

    with open('keys/dram.pkl', 'wb') as f:
        pickle.dump(dram,f)

def reset_mem():
    with open('keys/dram.pkl', 'rb') as f:
        dram = pickle.load(f)

    for d in dram:
        dram[d] = -1

    with open('keys/dram.pkl', 'wb') as f:
        pickle.dump(dram,f)



def send_mmio(socket, msg):
    sign = helper.sign_mmio(msg,"gpu")
    socket.sendall(sign.encode()+msg)

def check_sign_gpu(msg, hypervisor_socket):
    sig_hex = msg[:helper.SIGLEN].decode()

    public_key = ECC.import_key(open("keys/public_guest.pem").read())

    sig = bytes.fromhex(sig_hex)
    verifier = eddsa.new(public_key, 'rfc8032')

    try:
        verifier.verify(msg[helper.SIGLEN:], sig)
        return 1
    except (ValueError, TypeError):
        print("The signature is not valid.")
        reset()
        message = b"ERROR:Signature is not matching the message"
        send_mmio(hypervisor_socket, message)
        return 0

def print_node(node: Node):
    print(f"type: {node.op_type}, parents: {node.parents}, address: {node.addr}")

def reset_keys(): # Generates new keys
    helper.gen_aes_key()
    helper.gen_ecc_key("gpu")

def reset(): # Clears all states
    global queue_started
    global confidential
    op_names.clear()
    compute_graph.clear()
    reset_mem()
    queue_started = 0
    confidential = 0

def queue_start():
    global queue_started
    op_names.clear()
    compute_graph.clear()
    queue_started = 1

def queue_stop():
    global queue_started
    queue_started = 0
    message = "QUEUE-DONE"

    for cg in compute_graph:
        for p in compute_graph[cg].parents:
            if p not in op_names:
                message = f"ERROR:Operator {p} indicated as an input node of {cg} does not exist"
                reset()
                return message.encode()
    
    return message.encode()

def op_2_node(op_inputs, op_name, op_type): # Operator with 2 inputs
    num_inputs = len(op_inputs)
    message = ""
    addr = find_free_addr()

    node = Node(op_type, op_inputs, addr)

    if num_inputs == 2:
        compute_graph[op_name] = node
        message = f"ACK:Node Op:{addr}"
    else:
        message = f"ERROR:Operator expects 2 inputs and received {num_inputs}"

    return message

def op_1_node(op_inputs, op_name, op_type): # Operator with 1 input
    num_inputs = len(op_inputs)
    message = ""
    addr = find_free_addr()

    node = Node(op_type, op_inputs, addr)

    if num_inputs == 1:
        compute_graph[op_name] = node
        message = f"ACK:Node Op:{addr}"
    else:
        message = f"ERROR:Operator expects 1 inputs and received {num_inputs}"

    return message

def op_data_node(op_name): # Data node
    addr = find_free_addr()

    node = Node("DATA",[], addr)

    compute_graph[op_name] = node

    return f"ACK:Node Data:{addr}"

def op_end_node(op_name):
    addr = find_free_addr()
    keys = list(compute_graph.keys())

    node = Node("END", keys[-1:], addr) # Last node added will be the end node

    compute_graph[op_name] = node

    return f"ACK:Node End:{addr}"

def queue_op(command):
    command_split = command.split(":")

    length_cmd = len(command_split)
    if length_cmd < 3:
        err_msg = f"ERROR:QUEUE command is expecting at least 4 parameters and received {length_cmd} instead"
        return err_msg.encode()

    queue_type = command_split[1]
    op_name = command_split[2]

    if op_name in op_names:
        return b"ERROR:Operator name is not unique"
    op_names.append(op_name)

    match queue_type:
        case "ADD" | "SUB":
            message = op_2_node(command_split[3:], op_name, queue_type)
        case "ABS" | "INV":
            message = op_1_node(command_split[3:], op_name, queue_type)
        case "DATA":
            message = op_data_node(op_name)
        case "END":
            message = op_end_node(op_name)
        case _:
            message = "UNKNOWN-OP"

    return message.encode()

def decrypt_data(ops, values):
    for i,o in enumerate(ops):
        if 'D' in o and confidential:
            length = values[i].split(b':')[0]
            ciphertext = b':'.join(values[i].split(b':')[1:])

            values[i] = helper.dec_aes(length, ciphertext)

        values[i] = float(values[i])

    return values

def encrypt_result(value):
    value = b'RES:'+str(value).encode()
    if confidential:
        value = helper.enc_aes(value)

    return value


def do_add(ops):
    left_op = read_mem(compute_graph[ops[0]].addr)
    right_op = read_mem(compute_graph[ops[1]].addr)

    left_op,right_op = decrypt_data(ops,[left_op,right_op])

    return left_op + right_op

def do_sub(ops):
    left_op = read_mem(compute_graph[ops[0]].addr)
    right_op = read_mem(compute_graph[ops[1]].addr)

    left_op,right_op = decrypt_data(ops,[left_op,right_op])

    return left_op - right_op

def do_abs(ops):
    op = read_mem(compute_graph[ops[0]].addr)

    op = decrypt_data(ops,[op])[0]

    return abs(op)

def do_inv(ops):
    op = read_mem(compute_graph[ops[0]].addr)

    op = decrypt_data(ops,[op])[0]

    return -op

def do_end(op):
    last_op = read_mem(compute_graph[op[0]].addr)

    last_op = decrypt_data(op,[last_op])[0]

    result = encrypt_result(last_op)
    return result


def exec_compute():
    op_done = []

    for op in op_names:
        for p in compute_graph[op].parents:
            if p not in op_done:
                reset()
                return b"ERROR:One parent has not been executed yet, queue the operator in order for them to get executed before their results are needed"

        if compute_graph[op].op_type != "DATA":
            match compute_graph[op].op_type:
                case "ADD":
                    result = do_add(compute_graph[op].parents)
                    write_mem(compute_graph[op].addr,result)
                case "SUB":
                    result = do_sub(compute_graph[op].parents)
                    write_mem(compute_graph[op].addr,result)
                case "ABS":
                    result = do_abs(compute_graph[op].parents)
                    write_mem(compute_graph[op].addr,result)
                case "INV":
                    result = do_inv(compute_graph[op].parents)
                    write_mem(compute_graph[op].addr,result)
                case "END":
                    result = do_end(compute_graph[op].parents)
                    write_mem(compute_graph[op].addr,result)
                case _:
                    print("Implementation error")
                    exit(-1)

        op_done.append(op)

    return b"DONE-COMPUTE"

def set_confidential():
    global confidential
    confidential = 1

def gpu_mmio(mmio, hypervisor_socket):
    message = b""

    command = mmio[helper.SIGLEN:]
    command_parsed = command.split(b":")[0].decode()

    # Signature checked only if the command is not RESET-KEYS.
    if command_parsed != 'RESET-KEYS' and not check_sign_gpu(mmio, hypervisor_socket):
        return

    match command_parsed:
        case "RESET":
            reset()
            message = b"GPU-RESET"
        case "RESET-KEYS":
            reset_keys()
            message = b"KEYS-RESET"
        case "QUEUE-START":
            queue_start()
            message = b"QUEUE-WAIT"
        case "CONFIDENTIAL-ON":
            set_confidential()
            message = b"CONFIDENTIAL-SET"
        case "QUEUE-STOP":
            message = queue_stop()
        case "EXEC-COMPUTE":
            message = exec_compute()
        case "QUEUE":
            if queue_started:
                message = queue_op(command.decode())
            else:
                message = b"ERROR:Compute queue is not ready to accept new tasks"
        case _:
            message = b"UNKNOWN"

    send_mmio(hypervisor_socket, message)

def start_gpu():
    helper.remove_file("keys/private_gpu.pem")
    helper.remove_file("keys/public_gpu.pem")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hypervisor_address = ('localhost', SOCKET)
    helper.connect(client_socket,hypervisor_address)
    # print("Connected to", hypervisor_address)
    
    try:
        while 1:
            mmio = client_socket.recv(1024)
            gpu_mmio(mmio, client_socket)
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_gpu()
