# signal_compress.py
import argparse
import json
import heapq
import os
from collections import Counter, defaultdict
from typing import Dict, List

def extract_behavior(word: str) -> str:
    """Return a symbolic codon for a word based on RUMA-style heuristic."""
    vowels = "aeiouAEIOU"
    if not word:
        return "UNK"
    first = "V" if word[0] in vowels else "C"
    last = "V" if word[-1] in vowels else "C"
    parity = "E" if len(word) % 2 == 0 else "O"
    return first + last + parity

def build_huffman(symbols: List[str]) -> Dict[str, str]:
    freq = Counter(symbols)
    if len(freq) == 1:
        sym = next(iter(freq))
        return {sym: "0"}
    heap = [[wt, [[sym, ""]]] for sym, wt in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1]:
            pair[1] = "0" + pair[1]
        for pair in hi[1]:
            pair[1] = "1" + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0], lo[1] + hi[1]])
    return dict(heap[0][1])

def encode_bits(seq: List[str], huffman_map: Dict[str, str]) -> str:
    return "".join(huffman_map[s] for s in seq)

def bits_to_bytes(bits: str) -> tuple[bytes, int]:
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding
    return (bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)), padding)

def benchmark(input_path: str, vin_path: str, smap_path: str) -> Dict[str, float]:
    orig = os.path.getsize(input_path)
    vin = os.path.getsize(vin_path)
    smap = os.path.getsize(smap_path)
    return {
        "original_kb": orig / 1024,
        "vin_kb": vin / 1024,
        "smap_kb": smap / 1024,
        "total_kb": (vin + smap) / 1024,
        "compression_ratio": (vin + smap) / orig if orig else 0,
    }

def compress_file(input_file: str) -> None:
    with open(input_file, "r", encoding="utf-8") as f:
        words = f.read().split()

    codon_counts = defaultdict(int)
    reverse_map = {}
    codon_seq = []

    for word in words:
        base = extract_behavior(word)
        idx = codon_counts[base]
        codon = f"{base}{idx}"
        codon_counts[base] += 1
        codon_seq.append(codon)
        reverse_map[codon] = word

    huffmap = build_huffman(codon_seq)
    bits = encode_bits(codon_seq, huffmap)
    binary_data, pad = bits_to_bytes(bits)

    base = os.path.splitext(input_file)[0]
    vin_path = base + ".vin"
    smap_path = base + ".smap"

    with open(vin_path, "wb") as f:
        f.write(binary_data)

    with open(smap_path, "w", encoding="utf-8") as f:
        json.dump({
            "reverse_behavior_map": reverse_map,
            "huffman_map": huffmap,
            "padding": pad
        }, f, indent=2)

    stats = benchmark(input_file, vin_path, smap_path)
    print("✅ Compressed to:", vin_path)
    print(json.dumps(stats, indent=2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Plain text file to compress")
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print("❌ File not found:", args.input_file)
        return

    compress_file(args.input_file)

if __name__ == "__main__":
    main()
