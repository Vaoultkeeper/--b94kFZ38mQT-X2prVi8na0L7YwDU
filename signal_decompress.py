import sys
import json

def main(vin_path):
    # Load binary
    with open(vin_path, "rb") as f:
        byte_data = f.read()

    # Load SMAP
    with open("signal_output.smap", "r", encoding="utf-8") as f:
        smap = json.load(f)

    behavior_map = smap["behavior_map"]
    huffman = smap["huffman"]

    # Rebuild reverse maps
    reverse_huffman = {v: k for k, v in huffman.items()}
    reverse_behavior_map = {v: k for k, v in behavior_map.items()}

    # Convert binary to bitstring
    bitstring = ''.join(f'{byte:08b}' for byte in byte_data)

    # Decode Huffman sequence
    current = ""
    decoded_sequence = []
    for bit in bitstring:
        current += bit
        if current in reverse_huffman:
            decoded_sequence.append(reverse_huffman[current])
            current = ""

    # Recover original characters
    recovered = ''.join([key for key in decoded_sequence if key in reverse_behavior_map])
    restored = ' '.join([reverse_behavior_map.get(code, 'UNK') for code in decoded_sequence])


    # Save output
    with open("signal_output_restored.txt", "w", encoding="utf-8") as f:
        f.write(restored)

    print("✅ Decompression complete.")
    print(f"📂 Output written to signal_output_restored.txt")

if __name__ == "__main__":
    main(sys.argv[1])
