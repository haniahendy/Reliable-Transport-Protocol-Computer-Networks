import socket
import os
import random
import time

# Constants
MSS = 1024  
N = 4       
TIMEOUT = 5 
LOSS_RATE = 0.1  

def read_and_chunk_file(filepath):
    # Read the file as binary data
    with open(filepath, 'rb') as file:
        data = file.read()

    # Chunk the file into segments
    chunks = [data[i:i+MSS] for i in range(0, len(data), MSS)]
    
    return chunks

def send_packet(packet, receiver_ip, receiver_port):
    # Simulate packet loss
    if random.random() < LOSS_RATE:
        print("Packet lost:", packet)
        return

    # Create UDP socket and send packet
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(packet, (receiver_ip, receiver_port))
        print("Packet sent:", packet[:10])  # Print only the first few bytes for simplicity

def GBN_sender(filepaths, receiver_ip, receiver_port):
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        chunks = read_and_chunk_file(filepath)
        window_base = 0
        next_seq_num = 0

        while window_base < len(chunks):
            while next_seq_num < min(window_base + N, len(chunks)):
                packet = f"{next_seq_num:06d}".encode() + chunks[next_seq_num]
                send_packet(packet, receiver_ip, receiver_port)
                next_seq_num += 1

            # Wait for acknowledgements
            start_time = time.time()
            while True:
                current_time = time.time()
                if current_time - start_time >= TIMEOUT:
                    break

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(TIMEOUT - (current_time - start_time))
                    try:
                        data, _ = sock.recvfrom(1024)
                        ack_packet_id = int(data.decode())
                        if ack_packet_id >= window_base:
                            window_base = ack_packet_id + 1
                            break
                    except socket.timeout:
                        break

if __name__ == "__main__":
    filepaths = [r"C:\Users\Me\Downloads\small file.jpeg", 
                 r"C:\Users\Me\Downloads\medium file.jpeg", 
                 r"C:\Users\Me\Downloads\large file.jpeg"]
    receiver_ip = "192.168.0.100"  
    receiver_port = 5000        
    GBN_sender(filepaths, receiver_ip, receiver_port)
