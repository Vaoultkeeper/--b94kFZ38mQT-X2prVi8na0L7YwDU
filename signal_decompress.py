import argparse
import json
import os
from typing import Dict

def decode_bits(bitstream: str, huffman_map: Dict[str, str]) -> list:
    """Decode a bitstream using a Huffman map."""
    rev_map = {v: k for k, v in huffman_map.items()}
    decoded = []
    buffer = ""
    for bit in bitstream:
        buffer += bit
        if buffer in rev_map:
            decoded.append(rev_map[buffer])
            buffer = ""
    return decoded

def decompress_file(vin_path: str) -> str:
    """Decompress a .vin file using its associated .smap metadata."""
    if not vin_path.endswith(".vin"):
        raise ValueError("Expected .vin file")

    base = os.path.splitext(vin_path)[0]
    smap_path = base + ".smap"

    if not os.path.exists(smap_path):
        raise FileNotFoundError(f"Missing SMAP file: {smap_path}")

    with open(smap_path, "r", encoding="utf-8") as f:
        smap = json.load(f)

    huffman_map = smap["huffman_map"]
    reverse_map = smap["reverse_behavior_map"]
    padding = smap.get("padding", 0)

    with open(vin_path, "rb") as f:
        bitstream = ''.join(f"{byte:08b}" for byte in f.read())

    if padding:
        bitstream = bitstream[:-padding]

    behaviors = decode_bits(bitstream, huffman_map)
    words = [reverse_map.get(b, "UNK") for b in behaviors]

    out_path = base + "_restored.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(" ".join(words))

    return out_path

def main():
    parser = argparse.ArgumentParser(description="SignalZip Pro decompressor")
    parser.add_argument("vin_file", help=".vin file produced by signal_compress")
    args = parser.parse_args()

    if not os.path.isfile(args.vin_file):
        print(f"Error: {args.vin_file} does not exist")
        return

    try:
        out = decompress_file(args.vin_file)
        print(f"✅ Restored to {out}")
    except Exception as e:
        print("Error during decompression:", e)

if __name__ == "__main__":
    main()
