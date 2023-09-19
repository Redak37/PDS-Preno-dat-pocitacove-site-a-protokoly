import csv
from scapy.all import *
from scapy.layers.inet import *


pkts = PcapNgReader('dataset/mega104-17-12-18.pcapng')
i = 0
with open('out.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    for pkt in pkts:
        #ethernet_header = (len(pkt))  # IP payload size
        #ip_pload = (len(pkt.payload) - 20)  # Ethernet frame length
        #ip_header = (len(pkt.payload))  # Total length IP header
        #print(datetime.datetime.fromtimestamp(float(pkt.time)))

        try:
            check_int = None
            check_len = None
            check_bool = None
            try:
                check = bytes(pkt[Raw]).hex()
                check_int = int(check[2:4], 16)
                check_len = int(len(check) / 2 - 2)
                check_bool = int(check[9], 16) & 1 != 1
                if check[:2] == "68" and check_bool and check_len >= 4:
                    writer.writerow([
                        pkt.time, #pkt.seq, pkt.ack,
                        pkt[IP].src, pkt[IP].dst,
                        check_len
                        #pkt.src, pkt.dst,
                        #pkt.sport, pkt.dport,
                        #check_int, check_len, check_bool,
                        #len(pkt[IP]),
                        #len(pkt)
                    ])
            except Exception:
                pass
        except Exception:
            pass
