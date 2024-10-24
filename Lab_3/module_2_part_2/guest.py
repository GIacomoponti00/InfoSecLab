import socket
import helper
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from donotmodify import *
import sys
import pickle

confidential = 0

node_name_map = {}

def check_sign_guest(msg):
    if msg[helper.SIGLEN:helper.SIGLEN+len(b'DMA')] == b'DMA': # DMA replies are not signed.
        return 1

    sig_hex = msg[:helper.SIGLEN].decode()

    public_key = ECC.import_key(open("keys/public_gpu.pem").read())

    sig = bytes.fromhex(sig_hex)
    verifier = eddsa.new(public_key, 'rfc8032')

    try:
        verifier.verify(msg[helper.SIGLEN:], sig)
        return 1
    except (ValueError, TypeError):
        print("The signature is not valid.")
        return 0

def dma_enc(seq): # Encrypts DMA commands
    s_splitted = seq.split(b":")
    s_data = helper.enc_aes(s_splitted[3])
    return b":".join(s_splitted[:3])+b":"+s_data

def sequence_exec(seq_num, client_socket):
    with open('keys/sequence_'+seq_num+'.pkl', 'rb') as f:
        sequence = pickle.load(f)
    with open('keys/expected_reply_'+seq_num+'.pkl', 'rb') as f:
        expected_reply = pickle.load(f)

    global confidential
    node_name = -1
    sequence_num = 1

    for i,s in enumerate(sequence):
        s = s.encode()
        if confidential and s[0:6] == b"DMA:IN":
        
            s = dma_enc(s)

        if s[0:3] != b'DMA':
            sign = helper.sign_mmio(s, "guest").encode()
        else: # DMA commands are not signed
            dma_cmd_split = s.split(b':')
            dma_cmd_split[2] = node_name_map[dma_cmd_split[2]]
            s = b":".join(dma_cmd_split)
            sign = b'\x00'*helper.SIGLEN 

        if s[:6] == b'QUEUE:':
            node_name = s.split(b':')[2]
            node_name_map[node_name] = ""

        client_socket.sendall(sign+s)
        data = client_socket.recv(1024)
        reply = data[helper.SIGLEN:]
        reply_cmd = reply.split(b':')[0].decode()

        if reply_cmd != expected_reply[i]:
            print(f'GPU replied with {reply_cmd} instead of {expected_reply[i]}, stopping the execution')
            break

        if reply_cmd == 'CONFIDENTIAL-SET':
            confidential = 1

        if not check_sign_guest(data):
            print("Signature verification failed, stopping the execution")
            break

        if reply[:len(b'ACK:Node')] == b'ACK:Node':
            node_addr = reply.split(b':')[2]
            assert(node_name != -1)
            # Populates node map
            node_name_map[node_name] = node_addr

        if confidential and reply[:len(b"DMA-OUT-DONE")] == b"DMA-OUT-DONE":
            data_split = reply.split(b":")
            cipher_fixed = b":".join(data_split[2:]) # join the command in case the ciphertext, tag or nonce contains the symbol ":"

            value = helper.dec_aes(data_split[1].decode(),cipher_fixed).decode()

            value_split = value.split(':')
            if value_split[0] == 'RES':
                if int(sys.argv[1]) == 2:
                    print(f"Result {sequence_num} is {value_split[1]}", end=";")
                if sequence_num == 2:
                    print("\n", end="")
                sequence_num = sequence_num + 1
            else:
                print(f'ERROR: Keyword RES is not prepended to the result reply')
                exit(-1)

    confidential = 0


def start_guest():
    if len(sys.argv) != 2:
        print("Usage : python guest.py {Sequence to be executed, 1 or 2}")
        exit(1)

    # Clean previous keys
    helper.remove_file("keys/aes_key.bin")
    helper.remove_file("keys/private_guest.pem")
    helper.remove_file("keys/public_guest.pem")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hypervisor_address = ('localhost', SOCKET)
    helper.connect(client_socket,hypervisor_address)
    # print("Connected to", hypervisor_address)

    # No key exchange, we are letting the gpu and the guest read the key files
    helper.gen_ecc_key("guest")
    
    try:
        seq_num = sys.argv[1]
        sequence_exec(seq_num, client_socket)
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_guest()

