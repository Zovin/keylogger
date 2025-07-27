import os

file_path = "log.txt"
# key for ChaCha20
key = [
    0x03020100,
    0x07060504,
    0x0b0a0908,
    0x0f0e0d0c,
    0x13121110,
    0x17161514,
    0x1b1a1918,
    0x1f1e1d1c
]
block = 0

# ChaCha20 implementation in python
# Based on this implementation of ChaCha20 in javascript: 
# https://github.com/skeeto/chacha-js/blob/master/chacha.js

def rotate_left(value, shift):
    return ((value << shift) & 0xFFFFFFFF) | (value >> (32 - shift))

def quarter_round(matrix, a, b, c, d):
    # column round
    matrix[a] = (matrix[a] + matrix[b]) & 0xFFFFFFFF
    matrix[d] ^= matrix[a]
    matrix[d] = rotate_left(matrix[d], 16)

    matrix[a] = (matrix[c] + matrix[d]) & 0xFFFFFFFF
    matrix[b] ^= matrix[c]
    matrix[b] = rotate_left(matrix[b], 12)

    # diagonal round
    matrix[a] += (matrix[a] + matrix[b]) & 0xFFFFFFFF
    matrix[d] ^= matrix[a]
    matrix[d] = rotate_left(matrix[d], 8)

    matrix[c] += (matrix[c] + matrix[d]) & 0xFFFFFFFF
    matrix[b] ^= matrix[c]
    matrix[b] = rotate_left(matrix[b], 7)

def ChaCha20(nonce):
    matrix = [0] * 16
    matrix[0] = 0x61707865
    matrix[1] = 0x3320646e
    matrix[2] = 0x79622d32
    matrix[3] = 0x6b206574

    # populate the matrix with keys
    for i, word in enumerate(key):
        matrix[4+i] = word

    matrix[12] = block
    matrix[13] = nonce[0]
    matrix[14] = nonce[1]
    matrix[15] = nonce[2]

    original_matrix = matrix.copy()

    # only 10 times because every loop is doing 
    # 1 column round and 1 diagonal round
    for i in range(10):
        quarter_round(matrix,  0,  4,  8, 12)
        quarter_round(matrix,  1,  5,  9, 13)
        quarter_round(matrix,  2,  6, 10, 14)
        quarter_round(matrix,  3,  7, 11, 15)
        quarter_round(matrix,  0,  5, 10, 15)
        quarter_round(matrix,  1,  6, 11, 12)
        quarter_round(matrix,  2,  7,  8, 13)
        quarter_round(matrix,  3,  4,  9, 14)
    
    for i in range(16):
        matrix[i] = (matrix[i] + original_matrix[i]) & 0xFFFFFFFF

    keystream = []
    for word in matrix:
        keystream.append((word) & 0xFF)
        keystream.append((word >> 8) & 0xFF)
        keystream.append((word >> 16) & 0xFF)
        keystream.append((word >> 24) & 0xFF)
    
    return keystream



def read_nonce_and_data(file_path):
    with open(file_path, "rb") as f:
        nonce_bytes = f.read(12)  # first 12 bytes = nonce
        encrypted_data = f.read()  # rest of file

    # Convert nonce bytes to list of three 32-bit ints (big endian)
    nonce = [
        int.from_bytes(nonce_bytes[0:4], 'big'),
        int.from_bytes(nonce_bytes[4:8], 'big'),
        int.from_bytes(nonce_bytes[8:12], 'big'),
    ]

    return nonce, encrypted_data

def decrypt_chacha20(encrypted, nonce):
    # You need your ChaCha20 function here that accepts nonce, key, block and returns keystream bytes
    # This example assumes your ChaCha20 returns keystream for the current block
    global key, block
    
    # Generate keystream for length of encrypted data
    keystream = []
    total_len = len(encrypted)
    while len(keystream) < total_len:
        ks = ChaCha20(nonce)  # your ChaCha20 function should accept key and block
        keystream.extend(ks)
        block += 1
    keystream = keystream[:total_len]

    # XOR to decrypt
    decrypted = bytes([c ^ k for c, k in zip(encrypted, keystream)])

    return decrypted


nonce, encrypted_data = read_nonce_and_data(file_path)

plaintext = decrypt_chacha20(encrypted_data, nonce)

with open("log.decrypted.txt", "w", encoding="ascii", errors="ignore") as f:
    f.write(plaintext.decode("ascii", errors="ignore"))