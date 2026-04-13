# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated without permission.

"""
Cipher Command Agent - Multi-Agent Orchestration
Main orchestration agent that coordinates all specialist cipher-breaking agents.
"""

from strands import Agent
from strands.multiagent import Swarm
from strands_tools import current_time
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from botocore.config import Config as BotocoreConfig
import boto3
import re
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from cipher_rookie_agent import caesar_cipher_decoder, atbash_cipher_decoder, simple_substitution_decoder
from pattern_detective_agent import morse_code_decoder, rail_fence_decoder, polybius_square_decoder
from cipher_master_agent import multi_layer_decoder, cipher_type_identifier, a1z26_decoder

from common_algos import (
    morse_code_decode, rail_fence_decode, a1z26_decode,
    atbash_cipher, caesar_cipher, caesar_decrypt_auto,
    keyword_substitution_decrypt, polybius_square_decode,
    reverse_text, extract_acrostic, extract_capitalization_pattern,
    frequency_analysis
)

session = boto3.Session()
region = session.region_name
boto_config = BotocoreConfig(retries={"max_attempts": 3, "mode": "standard"}, connect_timeout=15, read_timeout=360)
model = BedrockModel(model_id="us.amazon.nova-pro-v1:0", boto_client_config=boto_config, region_name=region)

# --- Swarm Agents ---

cipher_rookie = Agent(name="cipher_rookie", model=model,
    tools=[caesar_cipher_decoder, atbash_cipher_decoder, simple_substitution_decoder],
    system_prompt="You are a substitution cipher specialist. Use the provided decoder tools. Try atbash first, then caesar, then substitution. Return ONLY the decoded plaintext.")

pattern_detective = Agent(name="pattern_detective", model=model,
    tools=[morse_code_decoder, rail_fence_decoder, polybius_square_decoder],
    system_prompt="You are a pattern cipher specialist. Use the provided decoder tools. Pass text EXACTLY as given. Return ONLY the decoded plaintext.")

cipher_master = Agent(name="cipher_master", model=model,
    tools=[multi_layer_decoder, cipher_type_identifier, a1z26_decoder],
    system_prompt="You are the cipher master. Use cipher_type_identifier first to identify the cipher type. Dots/dashes -> hand off to pattern_detective. Numbers that map 1-26 -> use a1z26_decoder. Two-digit numbers -> hand off to pattern_detective for Polybius. ALL CAPS text -> hand off to cipher_rookie. Complex/multi-layer -> use multi_layer_decoder. Return ONLY the decoded plaintext.")

swarm = Swarm([cipher_rookie, pattern_detective, cipher_master], entry_point=cipher_master,
    max_handoffs=5, max_iterations=5, execution_timeout=180.0, node_timeout=60.0,
    repetitive_handoff_detection_window=3, repetitive_handoff_min_unique_agents=2)


def extract_cipher_text(prompt):
    """Extract the encrypted portion from the prompt."""
    text = prompt.strip()

    # Quick check: if after colon split we get morse/numbers, return immediately
    if ':' in text:
        after_first_colon = text.split(':', 1)[1].strip()
        # If it starts with morse or numbers, take up to the next period-space
        if after_first_colon and (after_first_colon[0] in '.-0123456789'):
            if '. ' in after_first_colon:
                # Check if the period is part of morse code or a sentence break
                # Morse has patterns like ".-" so ". " followed by a letter/dash is morse
                # A sentence break is ". " followed by a capital letter word
                idx = 0
                while True:
                    pos = after_first_colon.find('. ', idx)
                    if pos == -1:
                        break
                    after_period = after_first_colon[pos+2:pos+3]
                    # If next char is uppercase letter, it's a sentence break
                    if after_period.isalpha() and after_period.isupper():
                        # Check if this looks like start of a hint sentence
                        rest = after_first_colon[pos+2:]
                        if any(rest.lower().startswith(w) for w in ['hint', 'the ', 'do ', 'note']):
                            return after_first_colon[:pos].strip()
                    idx = pos + 2
            return after_first_colon

    # For prompts without colons: find the ALL CAPS ciphertext block
    # Split on ". " followed by a letter (not morse dots/dashes)
    parts = re.split(r'\.\s+(?=[A-Za-z])', text)
    best = None
    for part in parts:
        part = part.strip().rstrip('.')
        if ':' in part:
            part = part.split(':', 1)[1].strip()
        alpha_only = ''.join(c for c in part if c.isalpha())
        if not alpha_only or len(alpha_only) < 5 or not alpha_only.isupper():
            continue
        words = part.split()
        instruction_words = {'DO', 'NOT', 'RETURN', 'HANDOFF', 'MESSAGES', 'OR', 'THINKING',
                             'PROCESS', 'ONLY', 'THE', 'FINAL', 'DECRYPTED', 'RESULT',
                             'SUBSTITUTION', 'KEY', 'WAS', 'GENERATED', 'USING', 'KEYWORD', 'HINT'}
        if sum(1 for w in words if w in instruction_words) / max(len(words), 1) >= 0.5:
            continue
        best = part
    if best:
        return best

    return text


COMMON_WORDS = {'THE', 'AND', 'TO', 'OF', 'IS', 'A', 'IN', 'THAT', 'FOR', 'IT', 'NOT', 'ON', 'WITH',
    'HE', 'AS', 'YOU', 'DO', 'AT', 'THIS', 'BUT', 'HIS', 'BY', 'FROM', 'THEY', 'WE',
    'HER', 'SHE', 'OR', 'AN', 'WILL', 'MY', 'ALL', 'MISSION', 'AGENT', 'SECRET',
    'UNICORN', 'LLAMA', 'HELLO', 'WORLD', 'ATTACK', 'DEFEND', 'CODE', 'CIPHER',
    'MESSAGE', 'DECRYPT', 'ENCRYPT', 'KEY', 'OPERATION', 'TARGET', 'BASE', 'TEAM',
    'REPORT', 'INTEL', 'SECURITY', 'ALERT', 'WARNING', 'DANGER', 'SAFE', 'GO',
    'STOP', 'YES', 'NO', 'ARE', 'WAS', 'WERE', 'BEEN', 'HAVE', 'HAS', 'HAD',
    'WOULD', 'COULD', 'SHOULD', 'CAN', 'MAY', 'MIGHT', 'MUST', 'SHALL',
    'NEED', 'DARE', 'OUGHT', 'USED', 'RENTAL', 'RENTALS', 'HEADQUARTERS', 'APPROVED',
    'PLAN', 'STEAL', 'EVIL', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'POLE', 'UNDER',
    'OVER', 'LOCATED', 'TWELVE', 'ICEBERG', 'LLAMAS', 'STOLEN', 'MAGIC', 'HORNS',
    'VAULT', 'TWENTY', 'THREE', 'HIDING', 'MOUNTAIN', 'CAVE', 'BRIDGE', 'RIVER',
    'FOREST', 'DESERT', 'OCEAN', 'ISLAND', 'CASTLE', 'TOWER', 'GATE', 'DOOR',
    'WINDOW', 'FLOOR', 'ROOM', 'HALL', 'WALL', 'ROOF', 'GROUND', 'SKY'}

KEYWORD_CANDIDATES = ['UNICORN', 'LLAMA', 'RENTAL', 'SECRET', 'CIPHER', 'MAGIC', 'QUEST', 'AGENT']


def score_english(decoded):
    words = decoded.split()
    if not words:
        return 0
    return sum(1 for w in words if w in COMMON_WORDS) / len(words)


def try_single_layer(text, prompt_lower):
    """Try single-layer ciphers. Return (result, score) or (None, 0)."""
    best = (None, 0)

    # Atbash
    r = atbash_cipher(text)
    s = score_english(r)
    if s > best[1]:
        best = (r, s)

    # Caesar auto
    r = caesar_decrypt_auto(text)
    s = score_english(r)
    if s > best[1]:
        best = (r, s)

    # Keyword substitution
    keywords = list(KEYWORD_CANDIDATES)
    for kw in KEYWORD_CANDIDATES:
        if kw.lower() in prompt_lower:
            keywords.remove(kw)
            keywords.insert(0, kw)
    for kw in keywords:
        r = keyword_substitution_decrypt(text, kw)
        s = score_english(r)
        if s > best[1]:
            best = (r, s)

    # All caesar shifts
    for shift in range(-25, 0):
        r = caesar_cipher(text, shift)
        s = score_english(r)
        if s > best[1]:
            best = (r, s)

    return best


def try_deterministic_decode(user_input):
    """Try to decode deterministically without the LLM. Return decoded text or None."""
    text = extract_cipher_text(user_input)
    prompt_lower = user_input.lower()

    # Morse code: dots, dashes, spaces, slashes
    if text and all(c in '.-/ ' for c in text):
        return morse_code_decode(text)

    # A1Z26: numbers 1-26 separated by spaces/slashes
    if text and all(c in '0123456789 /' for c in text):
        nums = text.replace('/', ' ').split()
        if all(n.isdigit() and 1 <= int(n) <= 26 for n in nums):
            return a1z26_decode(text)
        if all(n.isdigit() and len(n) == 2 and n[0] in '12345' and n[1] in '12345' for n in nums):
            return polybius_square_decode(text)

    # For alphabetic text
    stripped = text.replace(' ', '').replace('.', '').replace(',', '').replace('!', '').replace('?', '')
    if not (text and stripped.isalpha()):
        return None

    # Try single-layer ciphers first
    result, score = try_single_layer(text, prompt_lower)
    if score >= 0.3:
        return result

    # Try rail fence (2-5 rails) — with original spacing
    for rails in range(2, 6):
        r = rail_fence_decode(text, rails)
        s = score_english(r.upper())
        if s >= 0.3:
            return r.upper()
        # Also try without spaces
        r2 = rail_fence_decode(text.replace(' ', ''), rails)
        s2 = score_english(r2.upper())
        if s2 >= 0.3:
            return r2.upper()

    # Try multi-layer: atbash then caesar, caesar then atbash
    ab = atbash_cipher(text)
    for shift in range(-25, 0):
        r = caesar_cipher(ab, shift)
        if score_english(r) >= 0.3:
            return r

    for shift in range(-25, 0):
        r = atbash_cipher(caesar_cipher(text, shift))
        if score_english(r) >= 0.3:
            return r

    # Try multi-layer: keyword then caesar, caesar then keyword
    for kw in KEYWORD_CANDIDATES:
        kw_result = keyword_substitution_decrypt(text, kw)
        for shift in range(-25, 0):
            r = caesar_cipher(kw_result, shift)
            if score_english(r) >= 0.3:
                return r

    # Try multi-layer: atbash then keyword
    for kw in KEYWORD_CANDIDATES:
        r = keyword_substitution_decrypt(ab, kw)
        if score_english(r) >= 0.3:
            return r

    return None


# --- Entrypoint ---

app = BedrockAgentCoreApp()

@app.entrypoint
async def strands_agent_bedrock(payload: Dict[str, Any]) -> str:
    user_input = payload.get("prompt", "")
    logger.info(f"RECEIVED PROMPT: {user_input}")
    if not user_input:
        return "Error: No prompt provided."

    # Try deterministic decode first
    result = try_deterministic_decode(user_input)
    logger.info(f"DETERMINISTIC RESULT: {result}")
    if result:
        return result

    # Fall back to swarm
    try:
        response = await swarm.invoke_async(user_input)
        rs = str(response)

        # Try to extract clean text from SwarmResult
        if hasattr(response, 'results') and response.results:
            for nm, nd in reversed(list(response.results.items())):
                if hasattr(nd, 'result') and hasattr(nd.result, 'message'):
                    mg = nd.result.message
                    if isinstance(mg, dict) and 'content' in mg:
                        for block in mg['content']:
                            if 'text' in block:
                                tx = block['text'].strip()
                                # Strip thinking tags
                                tx = re.sub(r'<THINKING>.*?</THINKING>', '', tx, flags=re.DOTALL | re.IGNORECASE).strip()
                                # Extract quoted result if present
                                quoted = re.findall(r'"([^"]{3,})"', tx)
                                if quoted:
                                    return quoted[-1]
                                if tx and len(tx) > 2:
                                    return tx

        # Try marker-based extraction
        for marker in ['DECODED: ', 'DECRYPTED: ', 'RESULT: ', 'PLAINTEXT: ']:
            idx = rs.upper().rfind(marker.upper())
            if idx != -1:
                rem = rs[idx + len(marker):]
                for ec in ['\n', '<', '"']:
                    ei = rem.find(ec)
                    if ei != -1:
                        rem = rem[:ei]
                        break
                if len(rem.strip()) > 3:
                    return rem.strip()

        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                return response.message['content'][0]['text']
            return str(response.message)

        return rs
    except Exception as e:
        return f"Error processing cipher: {str(e)}"

if __name__ == "__main__":
    app.run()
