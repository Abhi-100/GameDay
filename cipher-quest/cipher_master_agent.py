# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated without permission.

"""
Cipher Master Agent - Multi-Layer Decryption
Handles complex multi-layered encryption, cipher identification, and advanced cryptanalysis.
"""

from strands import tool
from common_algos import atbash_cipher, caesar_cipher, a1z26_decode, morse_code_decode, rail_fence_decode, polybius_square_decode, caesar_decrypt_auto, reverse_text

@tool
def multi_layer_decoder(encrypted_text: str) -> str:
    """Decode multi-layer encryption by trying common cipher combinations"""
    results = []
    # Try single ciphers
    results.append(f"Atbash: {atbash_cipher(encrypted_text)}")
    results.append(f"Caesar auto: {caesar_decrypt_auto(encrypted_text)}")
    # Try reverse then atbash
    rev = reverse_text(encrypted_text)
    results.append(f"Reverse+Atbash: {atbash_cipher(rev)}")
    # Try atbash then caesar
    ab = atbash_cipher(encrypted_text)
    for s in [-3, -5, -7, -13]:
        results.append(f"Atbash+Caesar({s}): {caesar_cipher(ab, s)}")
    return "\n".join(results)

@tool
def a1z26_decoder(text: str) -> str:
    """Decode A1Z26 numeric encoding (A=1, B=2, ..., Z=26)"""
    return a1z26_decode(text)

@tool
def cipher_type_identifier(encrypted_text: str) -> str:
    """Identify cipher type based on patterns"""
    text = encrypted_text.strip()
    if all(c in '.-/ ' for c in text):
        return "MORSE_CODE"
    if all(c in '0123456789 /' for c in text):
        nums = [int(n) for n in text.replace('/', ' ').split() if n.isdigit()]
        if all(1 <= n <= 26 for n in nums):
            return "A1Z26"
        if all(n in range(11, 56) for n in nums):
            return "POLYBIUS_SQUARE"
        return "NUMERIC_ENCODING"
    if text.isupper() and ' ' not in text:
        return "POSSIBLE_RAIL_FENCE_OR_TRANSPOSITION"
    if text.isupper():
        return "SUBSTITUTION_CIPHER (Caesar/Atbash/Keyword)"
    return "UNKNOWN - try multi_layer_decoder"
