# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated without permission.

"""
Common Cipher Algorithms - COMPLETE IMPLEMENTATION
Shared cipher tools used across multiple agents
"""

from strands import tool
import string


# Basic Substitution Ciphers
@tool
def atbash_cipher(text: str) -> str:
    """Apply Atbash cipher (A↔Z, B↔Y, C↔X, etc.)"""
    result = ""
    for char in text.upper():
        if char.isalpha():
            # A=0, Z=25, so A↔Z is 25-0=25, B↔Y is 25-1=24, etc.
            result += chr(ord('Z') - (ord(char) - ord('A')))
        else:
            result += char
    return result


@tool
def caesar_cipher(text: str, shift: int) -> str:
    """Apply Caesar cipher with given shift"""
    result = ""
    for char in text.upper():
        if char.isalpha():
            result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        else:
            result += char
    return result


@tool
def simple_substitution_cipher(text: str, key: str) -> str:
    """Apply simple substitution cipher with given key"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = key.upper()
    result = ""
    for char in text.upper():
        if char.isalpha():
            idx = alphabet.index(char)
            result += key[idx] if idx < len(key) else char
        else:
            result += char
    return result

@tool
def keyword_substitution_decrypt(ciphertext: str, keyword: str) -> str:
    """Decrypt a keyword substitution cipher. Build the cipher alphabet from the keyword, then reverse the mapping to recover plaintext."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    seen = set()
    cipher_alphabet = ""
    for c in keyword.upper():
        if c.isalpha() and c not in seen:
            cipher_alphabet += c
            seen.add(c)
    for c in alphabet:
        if c not in seen:
            cipher_alphabet += c
            seen.add(c)
    result = ""
    for char in ciphertext.upper():
        if char.isalpha():
            idx = cipher_alphabet.index(char)
            result += alphabet[idx]
        else:
            result += char
    return result


# Pattern-Based Ciphers
@tool
def morse_code_encode(text: str) -> str:
    """Encode text to Morse code (dots and dashes)"""
    morse_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', ' ': '/'
    }
    return ' '.join(morse_dict.get(char.upper(), char) for char in text)


@tool
def morse_code_decode(morse_text: str) -> str:
    """Decode Morse code to text"""
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
        '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
        '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
        '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
        '-.--': 'Y', '--..': 'Z', '/': ' '
    }
    return ''.join(morse_dict.get(code, code) for code in morse_text.split())


@tool
def rail_fence_encode(text: str, rails: int) -> str:
    """Encode text using Rail Fence cipher with specified number of rails"""
    if rails == 1:
        return text
    
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    
    for char in text:
        fence[rail].append(char)
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    
    return ''.join(''.join(rail) for rail in fence)


@tool
def rail_fence_decode(cipher_text: str, rails: int) -> str:
    """Decode Rail Fence cipher with specified number of rails"""
    if rails == 1:
        return cipher_text
    
    n = len(cipher_text)
    
    # Create fence pattern
    fence = [[None for _ in range(n)] for _ in range(rails)]
    rail = 0
    direction = 1
    
    # Mark positions
    for i in range(n):
        fence[rail][i] = True
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    
    # Fill fence with cipher text
    idx = 0
    for r in range(rails):
        for c in range(n):
            if fence[r][c]:
                fence[r][c] = cipher_text[idx]
                idx += 1
    
    # Read fence
    result = []
    rail = 0
    direction = 1
    for i in range(n):
        result.append(fence[rail][i])
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    
    return ''.join(result)


@tool
def polybius_square_encode(text: str) -> str:
    """Encode text using Polybius square (5x5 grid coordinates)"""
    square = {
        'A': '11', 'B': '12', 'C': '13', 'D': '14', 'E': '15',
        'F': '21', 'G': '22', 'H': '23', 'I': '24', 'J': '24',  # I/J share 24
        'K': '25', 'L': '31', 'M': '32', 'N': '33', 'O': '34',
        'P': '35', 'Q': '41', 'R': '42', 'S': '43', 'T': '44',
        'U': '45', 'V': '51', 'W': '52', 'X': '53', 'Y': '54', 'Z': '55'
    }
    return ' '.join(square.get(char.upper(), char) for char in text if char.isalpha())


@tool
def polybius_square_decode(coordinates: str) -> str:
    """Decode Polybius square coordinates to text"""
    square = {
        '11': 'A', '12': 'B', '13': 'C', '14': 'D', '15': 'E',
        '21': 'F', '22': 'G', '23': 'H', '24': 'I', '25': 'K',
        '31': 'L', '32': 'M', '33': 'N', '34': 'O', '35': 'P',
        '41': 'Q', '42': 'R', '43': 'S', '44': 'T', '45': 'U',
        '51': 'V', '52': 'W', '53': 'X', '54': 'Y', '55': 'Z'
    }
    coords = coordinates.replace('/', ' ').split()
    return ''.join(square.get(coord, coord) for coord in coords)


# Numeric Encoding Schemes
@tool
def a1z26_encode(text: str) -> str:
    """Encode text using A1Z26 (A=1, B=2, ..., Z=26)"""
    return ' '.join(str(ord(char.upper()) - ord('A') + 1) for char in text if char.isalpha())


@tool
def a1z26_decode(numbers: str) -> str:
    """Decode A1Z26 numbers to text"""
    # Split by slashes first to preserve word boundaries
    words = numbers.split('/')
    decoded_words = []
    
    for word in words:
        nums = word.strip().split()
        word_result = ""
        for num in nums:
            try:
                n = int(num)
                if 1 <= n <= 26:
                    word_result += chr(n - 1 + ord('A'))
            except ValueError:
                continue
        if word_result:
            decoded_words.append(word_result)
    
    return ' '.join(decoded_words)


@tool
def phone_keypad_encode(text: str) -> str:
    """Encode text using phone keypad mapping (2=ABC, 3=DEF, etc.)"""
    keypad = {
        'A': '2', 'B': '2', 'C': '2', 'D': '3', 'E': '3', 'F': '3',
        'G': '4', 'H': '4', 'I': '4', 'J': '5', 'K': '5', 'L': '5',
        'M': '6', 'N': '6', 'O': '6', 'P': '7', 'Q': '7', 'R': '7', 'S': '7',
        'T': '8', 'U': '8', 'V': '8', 'W': '9', 'X': '9', 'Y': '9', 'Z': '9'
    }
    return ''.join(keypad.get(char.upper(), char) for char in text)


@tool
def phone_keypad_decode(numbers: str) -> str:
    """Decode phone keypad numbers to text"""
    keypad = {
        '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
        '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ'
    }
    # Simple decode - return first letter for each number
    return ''.join(keypad.get(char, char)[0] if char in keypad else char for char in numbers)


# Steganography Tools
@tool
def extract_acrostic(text: str, method: str = "first_letter") -> str:
    """Extract acrostic message from text (first letter of lines/words)"""
    if method == "first_letter":
        lines = text.strip().split('\n')
        return ''.join(line.strip()[0].upper() if line.strip() else '' for line in lines)
    elif method == "first_word":
        words = text.split()
        return ''.join(word[0].upper() for word in words)
    elif method == "sentences":
        # Extract first letter of words that start with capital letters
        import re
        words = text.split()
        capitals = [word[0] for word in words if word and word[0].isupper()]
        return ''.join(capitals)
    return ""


@tool
def extract_spacing_pattern(text: str) -> str:
    """Extract hidden message from spacing patterns"""
    # Extract based on double spaces or unusual spacing
    words = text.split('  ')  # Split on double spaces
    return ''.join(word[0].upper() if word else '' for word in words)


@tool
def extract_capitalization_pattern(text: str) -> str:
    """Extract hidden message from capitalization patterns"""
    return ''.join(char for char in text if char.isupper())


# Utility Functions
@tool
def detect_caesar_shift(text: str) -> int:
    """Detect the most likely Caesar cipher shift by trying all possibilities"""
    best_shift = 0
    best_score = 0
    
    # Key English words to look for
    key_words = ['THE', 'AND', 'TO', 'OF', 'A', 'IN', 'THAT', 'HAVE', 'FOR', 'NOT', 'WITH', 'HE', 'AS', 'YOU', 'DO', 'AT', 'THIS', 'BUT', 'HIS', 'BY', 'FROM', 'THEY', 'WE', 'SAY', 'HER', 'SHE', 'OR', 'AN', 'WILL', 'MY', 'ONE', 'ALL', 'WOULD', 'THERE', 'THEIR']
    
    for shift in range(-25, 1):
        decoded = caesar_cipher(text, shift)
        
        # Count matches with common English words
        score = 0
        words = decoded.split()
        for word in words:
            if word in key_words:
                score += 1
        
        # Bonus for very common words
        if 'THE' in decoded: score += 5
        if 'AND' in decoded: score += 3
        if 'TO' in decoded: score += 3
        
        if score > best_score:
            best_score = score
            best_shift = shift
    
    return best_shift


@tool
def caesar_decrypt_auto(text: str) -> str:
    """Automatically detect Caesar shift and decrypt"""
    shift = detect_caesar_shift(text)
    return caesar_cipher(text, shift)


@tool
def reverse_text(text: str) -> str:
    """Reverse the order of characters in text"""
    return text[::-1]


@tool
def frequency_analysis(text: str) -> str:
    """Perform frequency analysis on text"""
    freq = {}
    for char in text.upper():
        if char.isalpha():
            freq[char] = freq.get(char, 0) + 1
    
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return ', '.join(f"{char}: {count}" for char, count in sorted_freq[:10])


@tool
def index_of_coincidence(text: str) -> float:
    """Calculate Index of Coincidence for text"""
    text = ''.join(char.upper() for char in text if char.isalpha())
    n = len(text)
    if n <= 1:
        return 0.0
    
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    
    ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
    return ic
