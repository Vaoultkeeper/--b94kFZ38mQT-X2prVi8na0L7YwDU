import sys, json

def decode_bits(bitstream, huffman_map):
    rev_map = {v: k for k, v in huffman_map.items()}
    decoded = []
    buffer = ""
    for bit in bitstream:
        buffer += bit
        if buffer in rev_map:
            decoded.append(rev_map[buffer])
            buffer = ""
    return decoded

def main(vin_path):
    if not vin_path.endswith(".vin"):
        print("Expected .vin file")
        sys.exit(1)
    smap_path = vin_path.replace(".vin", ".smap")
    with open(smap_path, "r", encoding="utf-8") as f:
        smap = json.load(f)
    huffman_map = smap["huffman_map"]
    reverse_map = smap["reverse_behavior_map"]
    padding = smap.get("padding", 0)
    with open(vin_path, "rb") as f:
        bitstream = ''.join(
            f"{byte:08b}" for byte in f.read()
        )
    if padding:
        bitstream = bitstream[:-padding]
    decoded_behaviors = decode_bits(bitstream, huffman_map)
    words = [reverse_map[b] for b in decoded_behaviors]
    with open("signal_output_restored.txt", "w", encoding="utf-8") as f:
        f.write(" ".join(words))
    print("✅ Restored to signal_output_restored.txt")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python signal_decompress.py <input_file.vin>")
        sys.exit(1)
    main(sys.argv[1])
