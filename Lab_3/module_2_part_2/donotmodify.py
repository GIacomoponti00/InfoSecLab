# ------------- DO NOT MODIFY THIS FILE -----------------

SOCKET = 44444
DMASOCKET = 33333

# First sequence of commands, for part 1
# sequence_1 = \
# ["RESET-KEYS",\
#  "RESET",\
#  "CONFIDENTIAL-ON", \
#  "QUEUE-START",\
#  "QUEUE:DATA:D1",\
#  "QUEUE:DATA:D2",\
#  "QUEUE:DATA:D3",\
#  "QUEUE:DATA:D4",\
#  "QUEUE:INV:IN1:D1",\
#  "QUEUE:ABS:AB1:IN1",\
#  "QUEUE:SUB:S1:AB1:D2",\
#  "QUEUE:SUB:S2:S1:D3",\
#  "QUEUE:ABS:AB2:S2",\
#  "QUEUE:ADD:A1:D3:D4",\
#  "QUEUE:ABS:AB3:A1",\
#  "QUEUE:ADD:A2:AB2:A1",\
#  "QUEUE:END:E",\
#  "QUEUE-STOP",\
#  "DMA:IN:D1:-14578",\
#  "DMA:IN:D2:-7105",\
#  "DMA:IN:D3:-2",\
#  "DMA:IN:D4:2",\
#  "EXEC-COMPUTE",\
#  "DMA:OUT:E",\
#  "RESET"]

# Second sequence of commands, for part 2
# sequence_2 = \
# ["RESET-KEYS",\
#  "RESET",\
#  "CONFIDENTIAL-ON",\
#  "QUEUE-START",\
#  "QUEUE:DATA:D1",\
#  "QUEUE:DATA:D2",\
#  "QUEUE:DATA:D3",\
#  "QUEUE:DATA:D4",\
#  "QUEUE:INV:IN1:D1",\
#  "QUEUE:ABS:AB1:IN1",\
#  "QUEUE:SUB:S1:AB1:D2",\
#  "QUEUE:SUB:S2:S1:D3",\
#  "QUEUE:ABS:AB2:S2",\
#  "QUEUE:ADD:A1:D3:D4",\
#  "QUEUE:ABS:AB3:A1",\
#  "QUEUE:ADD:A2:AB2:A1",\
#  "QUEUE:END:E",\
#  "QUEUE-STOP",\
#  "DMA:IN:D1:-14578",\
#  "DMA:IN:D2:-7105",\
#  "DMA:IN:D3:-2",\
#  "DMA:IN:D4:2",\
#  "EXEC-COMPUTE",\
#  "DMA:OUT:E",\
#  "RESET",\
#  "RESET-KEYS",\
#  "CONFIDENTIAL-ON",\
#  "QUEUE-START",\
#  "QUEUE:DATA:D1",\
#  "QUEUE:DATA:D2",\
#  "QUEUE:DATA:D3",\
#  "QUEUE:INV:IN1:D1",\
#  "QUEUE:ABS:AB1:IN1",\
#  "QUEUE:ADD:A1:AB1:D2",\
#  "QUEUE:SUB:S1:A1:D3",\
#  "QUEUE:END:E",\
#  "QUEUE-STOP",\
#  "DMA:IN:D1:-5",\
#  "DMA:IN:D3:7",\
#  "DMA:IN:D2:10",\
#  "EXEC-COMPUTE",\
#  "DMA:OUT:E"]


# Sequence expected of replies expected by the guest
# expected_reply_1 = \
# ["KEYS-RESET",\
#  "GPU-RESET",\
#  "CONFIDENTIAL-SET",\
#  "QUEUE-WAIT",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "QUEUE-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DONE-COMPUTE",\
#  "DMA-OUT-DONE",\
#  "GPU-RESET"]

# expected_reply_2 = \
# ["KEYS-RESET",\
#  "GPU-RESET",\
#  "CONFIDENTIAL-SET",\
#  "QUEUE-WAIT",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "QUEUE-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DONE-COMPUTE",\
#  "DMA-OUT-DONE",\
#  "GPU-RESET",\
#  "KEYS-RESET",\
#  "CONFIDENTIAL-SET",\
#  "QUEUE-WAIT",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "ACK",\
#  "QUEUE-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DMA-DONE",\
#  "DONE-COMPUTE",\
#  "DMA-OUT-DONE"]
