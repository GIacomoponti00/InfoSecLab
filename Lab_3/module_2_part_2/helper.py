from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import os
import time
import socket

SIGLEN = 128

def remove_file(name):
    if os.path.exists(name):
        os.remove(name)

def enc_aes(msg):
    with open("keys/aes_key.bin", "rb") as f:
        aes_key = f.read()

    cipher = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(msg)
    assert len(cipher.nonce) == 16

    return str(len(ciphertext)).encode()+b":"+ciphertext+tag+cipher.nonce

def dec_aes(length, full_cipher):
    with open("keys/aes_key.bin", "rb") as f:
        aes_key = f.read()

    length = int(length)
    ciphertext = full_cipher[0:length]
    tag = full_cipher[length:length+16]
    nonce = full_cipher[length+16:]
    assert len(nonce) == 16

    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    try:
        msg = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        print("ERROR: The message was modified!")
        exit(-1)

    return msg

def gen_ecc_key(name):
    key = ECC.generate(curve='ed25519')
    private_key = key.export_key(format='PEM')
    public_key = key.public_key().export_key(format='PEM')

    with open("keys/private_"+name+".pem", "wt") as priv_file:
        priv_file.write(private_key)
    with open("keys/public_"+name+".pem", "wt") as pub_file:
        pub_file.write(public_key)

def gen_aes_key():
    aes_key = get_random_bytes(16)

    with open("keys/aes_key.bin", "wb") as f:
        f.write(aes_key)

def sign_mmio(msg, name):
    private_key = ECC.import_key(open("keys/private_"+name+".pem").read())

    signer = eddsa.new(private_key, 'rfc8032')
    signature = signer.sign(msg)

    return signature.hex()

def connect(csocket,address):
    while True:
        try:
            csocket.connect(address)
            break
        except socket.error:
            time.sleep(1)
