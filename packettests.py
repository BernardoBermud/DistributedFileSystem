from Packet import *

# Create a list of Packet objects
packet_list = []
packet_list.append(Packet())
packet_list.append(Packet())
packet_list.append(Packet())
# Example of building a registration packet for the first packet in the list
packet_list[0].BuildRegPacket("127.0.0.1", 12345)

# Example of building a list packet for the second packet in the list
packet_list[1].BuildListPacket()

# Example of building a get packet for the third packet in the list
packet_list[2].BuildGetPacket("example_file.txt")

registration_packet = Packet()
registration_packet.BuildGetPacket("loli.txt")

# Print the address and port
print(f"Address: {registration_packet.getFileInfo()}")
print(registration_packet.getPort())
# Print the values of each Packet object in the list
for packet in packet_list:
    encoded_packet = packet.getEncodedPacket()
    decoded_packet = Packet()
    decoded_packet.DecodePacket(encoded_packet)

    print(f"Original Packet: {packet.__dict__}")
    print(f"Encoded Packet: {encoded_packet}")
    print(f"Decoded Packet: {decoded_packet.__dict__}")
    print("-" * 30)