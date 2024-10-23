import pyshark
import json

def pcap_to_json(pcap_file, output_file):
    # Open the pcap file with pyshark
    capture = pyshark.FileCapture(pcap_file)
    packets = []

    # Iterate through packets and extract relevant information
    for packet in capture:
        packet_info = {
        'number': packet.number,
        'timestamp': packet.sniff_time.isoformat(),
        'layers': [],
        }
    
    # Extract each layer's information
    for layer in packet.layers:
        layer_info = {
        'layer_name': layer.layer_name,
        'fields': {}
        }
    # Extract fields for each layer
    for field_name in layer.field_names:
        layer_info['fields'][field_name] = layer.get_field(field_name)
        packet_info['layers'].append(layer_info)
    
    # Add packet info to the list
    packets.append(packet_info)
    
    # Write the output to a JSON file
    with open(output_file, 'w') as f:
        json.dump(packets, f, indent=4)
    
    print(f'Conversion complete. JSON saved to {output_file}')


# Example usage
pcap_file = 'LabTongHop_4-1-2016.pkt'
output_file = 'netbox_pcap.json'
pcap_to_json(pcap_file, output_file)