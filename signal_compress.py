import argparse, os, zipfile
from collections import Counter, defaultdict

# === Behavior map for codon extraction ===
LETTER_BEHAVIOR = {
    'a':'VCE','b':'CCE','c':'CCF','d':'VCD','e':'EVD','f':'PCD','g':'CCD','h':'EDC',
    'i':'VCF','j':'FCE','k':'PCE','l':'EVC','m':'EVF','n':'CCO','o':'VCO','p':'DVC',
    'q':'ECC','r':'CVF','s':'DCF','t':'VCC','u':'PVC','v':'FCD','w':'VFD','x':'DCF',
    'y':'ECV','z':'FCC',' ':'SPC','.':'END'
}

# === Step 1: Extract codons ===
def extract_codons(text):
    return [LETTER_BEHAVIOR.get(c.lower()) for c in text if c.lower() in LETTER_BEHAVIOR]

# === Step 2: Build index of most common sequences ===
def build_phrase_index(seq, max_window=8, max_phrases=256):
    freq = Counter()
    for w in range(2, max_window + 1):
        for i in range(len(seq) - w):
            chunk = tuple(seq[i:i+w])
            freq[chunk] += 1
    top = [k for k, _ in freq.most_common(max_phrases)]
    return {k: f"I{i}" for i, k in enumerate(top)}

# === Step 3: Replace phrases in sequence with indexes ===
def apply_indexing(seq, index_map):
    result = []
    i = 0
    keys_by_len = defaultdict(list)
    for k in index_map:
        keys_by_len[len(k)].append(k)

    max_len = max(len(k) for k in index_map)
    while i < len(seq):
        matched = False
        for l in range(max_len, 1, -1):
            if i + l <= len(seq):
                window = tuple(seq[i:i+l])
                if window in index_map:
                    result.append(index_map[window])
                    i += l
                    matched = True
                    break
        if not matched:
            result.append(seq[i])
            i += 1
    return result

# === Step 4: Token-level folding ===
def fold_tokens(seq):
    result = []
    i = 0
    while i < len(seq):
        token = seq[i]
        count = 1
        while i + 1 < len(seq) and seq[i + 1] == token:
            count += 1
            i += 1
        result.append(f"{token}*{count}" if count > 1 else token)
        i += 1
    return result

# === Step 5: Static Huffman encoding ===
def build_static_huffman_map(token_prefix="I", max_tokens=256):
    static_map = {}
    # Base tokens
    for i in range(max_tokens):
        base = f"{token_prefix}{i}"
        static_map[base] = format(i, "08b")
        # Add folded forms I3*2 through I3*9
        for rep in range(2, 10):
            token = f"{base}*{rep}"
            index = i * 10 + rep  # Avoid collision
            static_map[token] = format(index % 256, "08b")
    static_map["U"] = "11111111"
    return static_map

def encode_tokens(tokens, huff_map):
    return ''.join(huff_map.get(tok, huff_map["U"]) for tok in tokens)

def bits_to_bytes(bits):
    pad = (8 - len(bits) % 8) % 8
    bits += '0' * pad
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8)), pad

# === MAIN COMPRESSION PIPELINE ===
def compress_vaultzip_hybrid(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    base = os.path.splitext(input_file)[0]
    codons = extract_codons(text)
    print("[DEBUG] Raw codons:", len(codons))

    phrase_index = build_phrase_index(codons)
    print("[DEBUG] Phrases indexed:", len(phrase_index))

    indexed_stream = apply_indexing(codons, phrase_index)
    print("[DEBUG] Indexed stream length:", len(indexed_stream))

    folded_stream = fold_tokens(indexed_stream)
    print("[DEBUG] Folded tokens:", len(folded_stream))
    print("[DEBUG] Unique folded tokens:", len(set(folded_stream)))

    huff_map = build_static_huffman_map()
    bitstream = encode_tokens(folded_stream, huff_map)
    bdata, pad = bits_to_bytes(bitstream)
    print("[DEBUG] Bitstream length (bits):", len(bitstream))
    print("[DEBUG] Final .bin size (bytes):", len(bdata))

    bin_path = base + "_vault.bin"
    with open(bin_path, "wb") as f:
        f.write(bdata)

    rsz_path = base + ".rsz"
    with zipfile.ZipFile(rsz_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(bin_path, "vinrr_final.bin")
    os.remove(bin_path)

    print(f"✅ VaultZip-Hybrid complete: {rsz_path}")
    print(f"   Total stream size: {len(bdata)} bytes")

# === CLI ===
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Input .txt file")
    args = parser.parse_args()
    compress_vaultzip_hybrid(args.input_file)

if __name__ == "__main__":
    main()
