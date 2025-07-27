import sys, json, heapq
from collections import Counter

def extract_behavior(word):
    # Simple symbolic example – replace with real RUMA extractor
    vowels = "aeiou"
    return (
        "V" if word[0].lower() in vowels else "C"
    ) + (
        "V" if word[-1].lower() in vowels else "C"
    ) + (
        "C" if len(word) % 2 == 0 else "V"
    )

def build_huffman(symbols):
    freq = Counter(symbols)
    if len(freq) == 1:
        return {list(freq.keys())[0]: "0"}
    heap = [[wt, [[sym, ""]]] for sym, wt in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1]:
            pair[1] = '0' + pair[1]
        for pair in hi[1]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0], lo[1] + hi[1]])
    return dict(heap[0][1])

def main(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        words = f.read().split()
    behavior_seq = [extract_behavior(word) for word in words]
    huffman_map = build_huffman(behavior_seq)
    binary = ''.join(huffman_map[b] for b in behavior_seq)
    padding = (8 - len(binary) % 8) % 8
    binary += '0' * padding
    byte_array = bytearray(
        int(binary[i:i+8], 2) for i in range(0, len(binary), 8)
    )
    with open("signal_output.vin", "wb") as f:
        f.write(byte_array)
    behavior_map = {}
    reverse_map = {}
    for word, b in zip(words, behavior_seq):
        behavior_map[word] = b
        reverse_map[b] = word
    smap = {
        "behavior_map": behavior_map,
        "reverse_behavior_map": reverse_map,
        "huffman_map": huffman_map,
        "padding": padding
    }
    with open("signal_output.smap", "w", encoding="utf-8") as f:
        json.dump(smap, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python signal_compress.py <input_file>")
        sys.exit(1)
    main(sys.argv[1])
