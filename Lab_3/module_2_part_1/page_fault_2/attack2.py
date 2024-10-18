import sys
file = open(sys.argv[1], 'r')
lines = file.readlines()
num = 1

rec_addr = lines[1].strip()
#print("Recurrent address: " + rec_addr)

gap = 0
iteration_f = False

#clean the trace file
lines = lines[89:] 
#remove the end which are the last 9 lines
lines = lines[:-9]

secret_key_bits = []

counter = 0

for i in range(len(lines)):
    # Implement your solution here

    curr_addr = lines[i].strip()
    if curr_addr == rec_addr:
        if gap == 3: 
            counter += 1
            if iteration_f == True:
                secret_key_bits.append('0')
        
            iteration_f = True

        if gap == 4: 
            secret_key_bits.append('1')
            #if we have 2 consecutive ones, the we remove them and append -1 
            if secret_key_bits[-2:] == ['1', '1']:
                secret_key_bits = secret_key_bits[:-2]
                secret_key_bits.append('-1') 

            iteration_f = False
        gap = 0

    else:
        gap += 1


#print("Number of 3 gaps: " + str(counter))
#print("Secret key bits: " + str(secret_key_bits))
print("Secret key binary: " + ''.join(secret_key_bits))
#remove the last bit of the secret key
#secret_key_bits = secret_key_bits[:-1]
#remove the last bit of the secret key
#compute the length of the secret key which is the name of the trace file
#clan the trace name 
sec_key = sys.argv[1].split('/')[-1].split('.')[0]
#print ("Secret key: " + sec_key)
print("Secret key in binary: " + bin(int(sec_key, 16))[2:])
#print("Length of the secret key: " + str(len(bin(int(sec_key, 16))[2:]))) 

#convert the NAF binary <ai, ai-1, ...> to standard binary
#We start with the smallest i∈N0 such that ai<0 and set ai:=ai+2 and ai+1:=ai+1−1. 
# This does not change the value of our sequence, but removes the lowest negative digit in it. 
# By repeating, the value of i will grow and finally we end up with a normal binary number that has either the same number of digits as the NAF we started with 
# or one digit less
naf = secret_key_bits
#iterate over the NAf starting from the end, 
#if we find a -1, we add 2 to it and subtract 1 from the next bit
for i in range(len(naf)-1, -1, -1):
    if naf[i] == '-1':
        naf[i] = str(int(naf[i]) + 2)
        naf[i-1] = str(int(naf[i-1]) - 1)

print("Converted naf: " + ''.join(naf))


#print(hex(num))