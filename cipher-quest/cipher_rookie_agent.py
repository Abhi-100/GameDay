# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

"""
Cipher Rookie Agent - Basic Substitution Ciphers
Handles Caesar ciphers, Atbash ciphers, and keyword substitution ciphers.
"""

from strands import tool
from common_algos import caesar_cipher, atbash_cipher, caesar_decrypt_auto, keyword_substitution_decrypt

@tool
def caesar_cipher_decoder(encrypted_text: str) -> str:
    """Decrypt Caesar cipher by auto-detecting the shift"""
    return caesar_decrypt_auto(encrypted_text)

@tool
def atbash_cipher_decoder(encrypted_text: str) -> str:
    """Decrypt Atbash cipher (A↔Z, B↔Y, etc.)"""
    return atbash_cipher(encrypted_text)

@tool
def simple_substitution_decoder(encrypted_text: str) -> str:
    """Decrypt substitution cipher using keyword. Tries common keywords like UNICORN, LLAMA, etc."""
    common = {'THE', 'AND', 'TO', 'OF', 'IS', 'A', 'IN', 'AT', 'FOR', 'IT', 'NOT', 'ON', 'ALL',
              'MISSION', 'AGENT', 'SECRET', 'UNICORN', 'LLAMA', 'BASE', 'PLAN', 'LOCATED'}
    for kw in ['UNICORN', 'LLAMA', 'RENTAL', 'SECRET', 'CIPHER', 'MAGIC', 'QUEST', 'AGENT']:
        result = keyword_substitution_decrypt(encrypted_text, kw)
        words = result.split()
        if words and sum(1 for w in words if w in common) / len(words) >= 0.3:
            return result
    # Fallback: try atbash then caesar
    result = atbash_cipher(encrypted_text)
    words = result.split()
    if words and sum(1 for w in words if w in common) / len(words) >= 0.3:
        return result
    return caesar_decrypt_auto(encrypted_text)
