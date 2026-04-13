import os
import json
import requests
import logging
from typing import Dict, List, Optional
from uuid import uuid4
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCoreA2AClient:
    def __init__(self, region: str = None):
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.discovered_agents = {}
        self.bearer_token = os.environ.get('BEARER_TOKEN')
        
    def fetch_agent_card(self, agent_arn: str) -> Optional[Dict]:
        """Fetch agent card using AgentCore runtime URL"""
        if not self.bearer_token:
            logger.error("BEARER_TOKEN environment variable not set")
            return None
            
        escaped_agent_arn = quote(agent_arn, safe='')
        url = f"{TODO}"
        
        headers = {
            'Accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}',
            'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': str(uuid4())
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=300)
            response.raise_for_status()
            
            agent_card = response.json()
            runtime_url = f"{TODO}"
            
            self.discovered_agents[agent_arn] = {
                'card': agent_card,
                'runtime_url': runtime_url
            }
            
            logger.info(f"Discovered: {agent_card.get('name', 'Unknown')}")
            return agent_card
            
        except Exception as e:
            logger.error(f"Failed to fetch agent card: {e}")
            return None
    
    def find_best_agent(self, query: str, exclude: List[str] = None) -> Optional[str]:
        """Find best agent dynamically based on query and agent capabilities"""
        exclude = exclude or []
        query_words = set(query.lower().split())
        
        best_match = None
        best_score = 0
        
        for arn, agent_info in self.discovered_agents.items():
            if arn in exclude:
                continue
                
            card = agent_info['card']
            
            # Build agent vocabulary from all metadata
            agent_parts = [
                card.get('name', ''),
                card.get('description', '')
            ]
            
            for skill in card.get('skills', []):
                agent_parts.extend([
                    skill.get('name', ''),
                    skill.get('description', '')
                ])
            
            agent_text = ' '.join(agent_parts).lower()
            agent_words = set(agent_text.split())
            
            # Exact word matches (highest priority)
            exact_matches = len(query_words.intersection(agent_words))
            
            # Partial matches (medium priority)
            partial_matches = sum(1 for q_word in query_words 
                                if any(q_word in a_word or a_word in q_word 
                                      for a_word in agent_words if len(q_word) > 2))
            
            # Context matches (lowest priority) - check if query context matches agent purpose
            context_score = 0
            # Generic semantic matching - no hardcoded agent types
            query_lower = query.lower()
            if len(query_words.intersection(agent_words)) > 0:
                context_score = 1
            
            total_score = exact_matches * 3 + partial_matches * 2 + context_score
            
            if total_score > best_score:
                best_score = total_score
                best_match = arn
                
        return best_match if best_score > 0 else None
    
    def send_message(self, agent_arn: str, message: str) -> Dict:
        """Send JSON-RPC message to agent"""
        if agent_arn not in self.discovered_agents:
            return {"error": "Agent not discovered"}
            
        runtime_url = self.discovered_agents[agent_arn]['runtime_url']
        
        payload = {
            "jsonrpc": "2.0",
            "id": "req-001",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message}],
                    "messageId": str(uuid4())
                }
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}',
            'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': str(uuid4())
        }
        
        try:
            response = requests.post(runtime_url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def needs_collaboration(self, response_text: str) -> bool:
        """Dynamically detect if response indicates need for collaboration"""
        collaboration_indicators = [
            "don't have", "need", "require", "would need", "please provide",
            "can't access", "not available", "unable to", "missing", "lack"
        ]
        
        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in collaboration_indicators)
    
    def auto_route_query(self, query: str, agent_arns: List[str], max_rounds: int = 3) -> Dict:
        """Dynamic multi-round orchestration"""
        
        # Discover all agents
        for arn in agent_arns:
            if arn not in self.discovered_agents:
                self.fetch_agent_card(arn)
        
        conversation_history = []
        used_agents = []
        
        current_query = query
        
        for round_num in range(max_rounds):
            # Find best agent for current query (excluding recently used)
            exclude_recent = used_agents[-1:] if len(used_agents) > 0 else []
            best_agent = self.find_best_agent(current_query, exclude=exclude_recent)
            
            if not best_agent:
                break
                
            # Send query to agent
            response = self.send_message(best_agent, current_query)
            response_text = self._extract_text(response)
            
            conversation_history.append({
                'round': round_num + 1,
                'agent': best_agent,
                'agent_name': self.discovered_agents[best_agent]['card'].get('name', 'Unknown'),
                'query': current_query,
                'response': response,
                'response_text': response_text
            })
            
            used_agents.append(best_agent)
            
            # Check if collaboration needed
            if self.needs_collaboration(response_text):
                # Prepare next query with context
                current_query = f"Help with: {query}. Previous context: {response_text}"
            else:
                # Task complete
                break
        
        # Format response for backward compatibility
        if not conversation_history:
            return {"error": "No suitable agent found through discovery"}
        elif len(conversation_history) == 1:
            return {
                'primary_agent': conversation_history[0]['agent'],
                'response': conversation_history[0]['response'],
                'result': conversation_history[0]['response_text']
            }
        else:
            return {
                'primary_agent': conversation_history[0]['agent'],
                'collaborating_agent': conversation_history[1]['agent'] if len(conversation_history) > 1 else None,
                'conversation': conversation_history,
                'result': conversation_history[-1]['response_text'],
                'agents_used': [h['agent_name'] for h in conversation_history]
            }
    
    def _extract_text(self, response: Dict) -> str:
        """Extract text from JSON-RPC response"""
        try:
            return response['result']['artifacts'][0]['parts'][0]['text']
        except:
            try:
                return response['result']['message']['parts'][0]['text']
            except:
                return str(response)
