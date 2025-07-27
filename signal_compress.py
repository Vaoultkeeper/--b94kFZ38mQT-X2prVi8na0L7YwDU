import sys
import json
import heapq
from collections import defaultdict, Counter

# Basic behavior extraction stub (replace with full RUMA extractor as needed)
def extract_behavior(word):
    vowels = 'aeiou'
    if any(c in vowels for c in word.lower()):
        return 'VEF'
    return 'DDF'

def build_huffman(symbols):
    freq = Counter(symbols)
    heap = [[weight, [[sym, ""]]] for sym, weight in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1]:
            pair[1] = '0' + pair[1]
        for pair in hi[1]:
            pair[1] = '1' + pair[1]
        merged = lo[1] + hi[1]
        heapq.heappush(heap, [lo[0] + hi[0], merged])
    return dict(heap[0][1])

def encode_to_binary(bitstring):
    # Convert bitstring into byte array
    padding = (8 - len(bitstring) % 8) % 8
    bitstring += '0' * padding
    byte_data = bytearray()
    for i in range(0, len(bitstring), 8):
        byte = bitstring[i:i+8]
        byte_data.append(int(byte, 2))
    return bytes(byte_data), padding

def main(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    words = text.split()
    behavior_map = {}
    behavior_seq = []
    reverse_behavior_map = {}

    for i, word in enumerate(words):
        if word not in behavior_map:
            behavior = extract_behavior(word)
            alias = f"A{i}"
            behavior_map[word] = alias
            reverse_behavior_map[alias] = word
        behavior_seq.append(behavior_map[word])

    # Use Huffman to encode behavior sequence
    huffman_map = build_huffman(behavior_seq)
    huff_bitstring = ''.join(huffman_map[sym] for sym in behavior_seq)
    binary, padding = encode_to_binary(huff_bitstring)

    # Write compressed binary
    with open("signal_output.vin", "wb") as f:
        f.write(binary)

    # Write map
    with open("signal_output.smap", "w", encoding='utf-8') as f:
        json.dump({
            "behavior_map": behavior_map,
            "reverse_behavior_map": reverse_behavior_map,
            "huffman_map": huffman_map,
            "padding": padding
        }, f)

    print("✅ Compression complete.")
    print(f"Words processed: {len(words)}")
    print(f"Unique codes: {len(behavior_map)}")
    print(f"Output saved to: signal_output.vin, signal_output.smap")

if __name__ == "__main__":
    main(sys.argv[1])
