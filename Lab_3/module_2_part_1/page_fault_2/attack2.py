import sys
file = open(sys.argv[1], 'r')
lines = file.readlines()
num = 1

rec_addr = lines[1]
#remove the lines with the rec_addr
lines = [line for line in lines if rec_addr not in line]
#convert the lines into int
for i in range(len(lines)):
    lines[i] = int(lines[i], 16)

#find the base address of the binary
main = 0x000000000000c000
main = int(main)

inverse = 0x0000000000009000
inverse = int(inverse)


naf_exponentiation = 0x0000000000008000
naf_exponentiation = int(naf_exponentiation)


naf_exponentiation = 0x0000000000008000
naf_exponentiation = int(naf_exponentiation)

point_double = 0x0000000000006000
point_double = int(point_double)

point_addition = 0x0000000000007000
point_addition = int(point_addition)

_start = 0x0000000000002000
_start = int(_start)

#compute the base address offset 
base_address_offset = lines[0] - _start
base_address_offset = int(base_address_offset)

#print(hex(base_address_offset))

#remove the base address offset from the lines
for i in range(len(lines)):
    lines[i] = lines[i] - base_address_offset

counter = 0
sec_key_bits = [1]

length_of_1 = 0
counting = False

for i in range(len(lines)):
    # Implement your solution here
    if lines[i] == naf_exponentiation:
        if lines[i+1] == point_double:
            sec_key_bits.append(0)
        if lines[i+1] == point_addition:
            #remove the last added zero since we have a point addition
            sec_key_bits.pop()
            sec_key_bits.append(1)
        if lines[i+1] == inverse:
            sec_key_bits.pop()
            sec_key_bits.append(-1)

            	
        
 
#print the found secret key in NAF form and its length
#print("Found secret key: " + str(sec_key_bits) + " with length: " + str(len(sec_key_bits)))

#compute the number of the secret key in decimal form and store it in num
num = 0
for i in range(len(sec_key_bits)):
    num = num + sec_key_bits[i] * (2** (len(sec_key_bits) - i - 1))

#convert it back to binary 
num = bin(num)[2:]
#print("Secret key in decimal: " + str(num))
print("Secret key in hex: " + str(hex(int(num, 2))))
    

#the true key is the name fo the file without the .out extension and withou the path
true_key = sys.argv[1].split("/")[-1].split(".")[0]
#print the number of bits of the true key
true_key = bin(int(true_key, 16))[2:]
#print("True key: " + str(true_key))
#print("True key length: " + str(len(true_key)))