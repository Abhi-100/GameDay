# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

"""
Pattern Detective Agent - Pattern-Based Ciphers
Handles Morse code, Rail Fence ciphers, and Polybius square ciphers.
"""

from strands import tool
from common_algos import morse_code_decode, rail_fence_decode, polybius_square_decode
import re

@tool
def morse_code_decoder(encrypted_text: str) -> str:
    """Decode Morse code (dots and dashes)"""
    return morse_code_decode(encrypted_text)

@tool
def rail_fence_decoder(encrypted_text: str) -> str:
    """Decode Rail Fence cipher by trying 2-5 rails"""
    results = []
    for rails in range(2, 6):
        result = rail_fence_decode(encrypted_text, rails)
        results.append(f"Rails={rails}: {result}")
    return "\n".join(results)

@tool
def polybius_square_decoder(encrypted_text: str) -> str:
    """Decode Polybius square coordinates"""
    return polybius_square_decode(encrypted_text)
