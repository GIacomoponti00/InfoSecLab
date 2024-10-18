import sys
file = open(sys.argv[1], 'r')
lines = file.readlines()
num = 1

# initialize the gap variable to count the number of pages between the two recurring address
gap = 0 
#recurrent address that recurs trhoughout the trace file
rec_addr = lines[1].strip()
#rec_addr = int(rec_addr, 16)

#counter to count the number of gaps of size 3 
counter = 0

#aan example of gap of size 3 is: 
""" 
0x5b49ba5d7000
0x5b49ba5d9000
0x5b49ba5df000
0x5b49ba5de000
0x5b49ba5d7000
 """

#we need to detect pair of gap of size 2
#the first pair of gap of size 2 is of the form: 
""" 
0x638927d4a000
0x638927d51000
0x638927d50000
0x638927d4a000
0x638927d50000
0x638927d4a000
0x638927d50000
0x638927d4a000
0x638927d50000
0x638927d4a000
0x638927d50000
0x638927d4a000
0x638927d50000
0x638927d4a000
0x638927d50000
0x638927d4e000
0x638927d4a000 """

#for the rest of the program the pair is of the form:
""" 
0x638927d4a000
0x638927d4e000
0x638927d50000
0x638927d4a000
0x638927d50000
0x638927d4f000
0x638927d4a000 
""" 
#flag to check if the first pair of gap of size 2 is detected
first_flag = False
#iteration flag to signal whether we found a 3 gap
iteration_f = False


#store the bits from LSB to MSB of the secret key
secret_key_bits = []

#clean the trace file to remove the incipit and the end
#remove the incipit which are the first 90 lines
lines = lines[89:] 
#remove the end which are the last 9 lines
lines = lines[:-9]


for i in range(len(lines)):
    # Implement your solution here
    # get the address of the current line
    addr = lines[i].strip()
    #addr = int(addr, 16)

    # check if the address is equal to the recurrent address
    if addr == rec_addr:
        # if the gap is equal to 2, increment the counter
        if gap == 2:
            counter += 1

            if first_flag == False:
                first_flag = True
                if iteration_f == True: 
                    secret_key_bits.append('0')

            else: 
                first_flag = False
                iteration_f = True
        #if we also have a gap in the iteration it means the bit of the secret key is 1
        if gap == 3:
            secret_key_bits.append('1')
            iteration_f = False

        # reset the gap
        gap = 0
    else:
        # increment the gap
        gap += 1

# compose the binary of the secret key without the last bit (to fix) 
#print(secret_key_bits)
found_sk = ''.join(secret_key_bits)
#append a 1 to the beginning of the secret key
found_sk = '1' + found_sk

if iteration_f == True:
    found_sk += '0'
#remove the last 1 since the 3 gap don't represent the last bit of the secret key
#found_sk = found_sk[:-1]
#remove the first digit of the secret key
#found_sk = found_sk[1:]
#remove the 2nd digit of the secret key but keeping the first digit
#found_sk = found_sk[0] + found_sk[2:]

#print(found_sk)
#print the hex of the secret key
print(hex(int(found_sk, 2)))
            
#get the number of bits of the secret key, which is the name of file of the trace file without the extension 
# and all the folder names before the file name 
#the secret key starts after the last '/' in the path of the file
#sec_key = sys.argv[1].split('/')[-1].split('.')[0]
#print (sec_key)
   
#transform the secret key into binary format
#sec_key = bin(int(sec_key, 16))
#remove the '0b' prefix
#sec_key = sec_key[2:]
#count the number of bits of the secret key
#num = len(sec_key)

#count the number of bits equal 1 and store it in a new variable n_pos 
""" n_pos = 0
for i in range(num):
    if sec_key[i] == '1':
        n_pos += 1 """

# print the number of bits equal to 1
#print(n_pos)



# print the number of gaps of size 2
#print(counter)
# print the number of bits of the secret key
#print(num)
    

#print(hex(num))
