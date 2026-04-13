#!/usr/bin/env python3
"""
Comprehensive tool verification for cipher quest
"""

def test_all_ciphers():
    """Test all cipher implementations"""
    
    # Atbash cipher
    def atbash_cipher(text):
        result = ''
        for char in text.upper():
            if char.isalpha():
                result += chr(ord('Z') - (ord(char) - ord('A')))
            else:
                result += char
        return result
    
    # Caesar cipher  
    def caesar_cipher(text, shift):
        result = ''
        for char in text.upper():
            if char.isalpha():
                result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                result += char
        return result
    
    # Morse code decode
    def morse_code_decode(morse_text):
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
            '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
            '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
            '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
            '-.--': 'Y', '--..': 'Z', '/': ' '
        }
        return ''.join(morse_dict.get(code, code) for code in morse_text.split())
    
    # A1Z26 decode
    def a1z26_decode(numbers):
        nums = numbers.split()
        result = ''
        for num in nums:
            try:
                n = int(num)
                if 1 <= n <= 26:
                    result += chr(n - 1 + ord('A'))
            except ValueError:
                continue
        return result
    
    # Polybius square decode
    def polybius_square_decode(coordinates):
        square = {
            '11': 'A', '12': 'B', '13': 'C', '14': 'D', '15': 'E',
            '21': 'F', '22': 'G', '23': 'H', '24': 'I', '25': 'K',
            '31': 'L', '32': 'M', '33': 'N', '34': 'O', '35': 'P',
            '41': 'Q', '42': 'R', '43': 'S', '44': 'T', '45': 'U',
            '51': 'V', '52': 'W', '53': 'X', '54': 'Y', '55': 'Z'
        }
        coords = coordinates.replace('/', ' ').split()
        return ''.join(square.get(coord, coord) for coord in coords)
    
    # Rail fence decode
    def rail_fence_decode(cipher_text, rails):
        if rails == 1:
            return cipher_text
        
        # Create fence pattern
        fence = [[None for _ in range(len(cipher_text))] for _ in range(rails)]
        rail = 0
        direction = 1
        
        # Mark positions
        for i in range(len(cipher_text)):
            fence[rail][i] = True
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        # Fill fence with cipher text
        idx = 0
        for r in range(rails):
            for c in range(len(cipher_text)):
                if fence[r][c]:
                    fence[r][c] = cipher_text[idx]
                    idx += 1
        
        # Read fence
        result = []
        rail = 0
        direction = 1
        for i in range(len(cipher_text)):
            result.append(fence[rail][i])
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        return ''.join(result)
    
    # Test cases
    tests = [
        # Basic ciphers
        ('Atbash', 'SVOOL', 'HELLO', lambda x: atbash_cipher(x)),
        ('Atbash Mission', 'HVXIVG ZTVMG NRHHRLM ZKKILEVW YB FMRXLIM IVMGZOH SVZWJFZIGVIH', 
         'SECRET AGENT MISSION APPROVED BY UNICORN RENTALS HEADQUARTERS', lambda x: atbash_cipher(x)),
        ('Caesar', 'KHOOR', 'HELLO', lambda x: caesar_cipher(x, -3)),
        ('Caesar', 'FDHVDU FLSKHU', 'CAESAR CIPHER', lambda x: caesar_cipher(x, -3)),
        
        # Pattern ciphers
        ('Morse', '.... . .-.. .-.. ---', 'HELLO', morse_code_decode),
        ('Morse', '-- --- .-. ... . / -.-. --- -.. .', 'MORSE CODE', morse_code_decode),
        ('A1Z26', '8 5 12 12 15', 'HELLO', a1z26_decode),
        ('A1Z26', '20 5 19 20', 'TEST', a1z26_decode),
        ('Polybius', '23 15 31 31 34', 'HELLO', polybius_square_decode),
        ('Polybius', '44 15 43 44', 'TEST', polybius_square_decode),
        
        # Rail fence
        ('Rail Fence 2', 'HLOEL', 'HELLO', lambda x: rail_fence_decode(x, 2)),
        ('Rail Fence 3', 'HOELL', 'HELLO', lambda x: rail_fence_decode(x, 3)),
    ]
    
    print("🔐 Cipher Tool Verification")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for name, input_text, expected, func in tests:
        try:
            result = func(input_text)
            status = '✅' if result == expected else '❌'
            print(f'{status} {name}: "{input_text}" → "{result}"')
            if result == expected:
                passed += 1
            else:
                print(f'   Expected: "{expected}"')
        except Exception as e:
            print(f'❌ {name}: ERROR - {e}')
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    success = test_all_ciphers()
    print(f"\n{'🎉 ALL TESTS PASSED' if success else '⚠️  SOME TESTS FAILED'}")
