import socket
from PIL import Image
import os

def receive_packet(receiver_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('0.0.0.0', receiver_port))
        data, addr = sock.recvfrom(1024)
    return data, addr

def GBN_receiver(receiver_port):
    received_data = b""
    expected_packet_id = 0

    while True:
        packet_data, addr = receive_packet(receiver_port)
        if packet_data:
            packet_id = int(packet_data[:6].decode('utf-8'))
            chunk = packet_data[6:]

            if packet_id == expected_packet_id:
                received_data += chunk
                expected_packet_id += 1

            # Send acknowledgment
            ack_packet_id = packet_id
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(str(ack_packet_id).encode(), addr)

            if len(chunk) < 1024:
                # Write received data to a file
                try:
                    with open("received_image.jpg", 'wb') as file:
                        file.write(received_data)
                except Exception as e:
                    print("Error writing received data to file:", e)
                    break
                
                # Open and display the image
                image_path = "received_image.jpg"
                try:
                    if os.path.exists(image_path):
                        image = Image.open(image_path)
                        image.show()
                        print("Image received successfully.")
                    else:
                        print("Received file not found.")
                except Exception as e:
                    print("Error opening the received image:", e)
                    break

                break

# Example usage
receiver_port = 5000
GBN_receiver(receiver_port)
