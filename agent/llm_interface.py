"""
LLM Interface untuk Autonomous Agent
"""
import os
import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class LLMInterface(ABC):
    """Abstract base class untuk LLM interface"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response dari LLM"""
        pass
    
    @abstractmethod
    async def plan_next_action(self, goal: str, current_state: str, history: List[str]) -> Dict[str, Any]:
        """Plan next action berdasarkan goal dan current state"""
        pass

class OpenAIInterface(LLMInterface):
    """Interface untuk OpenAI GPT models"""
    
    def __init__(self, model: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available")
        
        self.model = model
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
    
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response dari OpenAI"""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            if context:
                system_message = f"Context: {json.dumps(context, indent=2)}"
                messages.insert(0, {"role": "system", "content": system_message})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def plan_next_action(self, goal: str, current_state: str, history: List[str]) -> Dict[str, Any]:
        """Plan next action menggunakan OpenAI"""
        prompt = f"""
Anda adalah autonomous agent yang dapat melakukan browser automation.

GOAL: {goal}

CURRENT STATE:
{current_state}

HISTORY:
{chr(10).join(history[-5:]) if history else "No previous actions"}

AVAILABLE TOOLS:
1. navigate(url) - Navigate to a URL
2. click(selector) - Click element by CSS selector or XPath
3. type(selector, text) - Type text into input field
4. read_dom() - Read current page DOM
5. wait(seconds) - Wait for specified seconds

Berdasarkan goal dan current state, tentukan action selanjutnya.
Respond dalam format JSON:
{{
    "reasoning": "Penjelasan mengapa memilih action ini",
    "tool_name": "nama_tool",
    "parameters": {{"param1": "value1"}},
    "expected_outcome": "Apa yang diharapkan terjadi"
}}
"""
        
        response = await self.generate_response(prompt)
        
        try:
            # Try to parse JSON response directly
            action_plan = json.loads(response)
            return action_plan
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown code block
            try:
                import re
                json_match = re.search(r'```json\n(.*?)```', response, re.DOTALL)
                if json_match:
                    action_plan = json.loads(json_match.group(1))
                    return action_plan
                else:
                    raise ValueError("No JSON found in LLM response")
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback jika response bukan JSON valid atau tidak ada JSON di markdown
                print(f"Failed to parse LLM response: {e}. Raw response: {response[:200]}...")
                return {
                    "reasoning": "Failed to parse LLM response",
                    "tool_name": "wait",
                    "parameters": {"seconds": 1},
                    "expected_outcome": "Wait and retry"
                }

class AnthropicInterface(LLMInterface):
    """Interface untuk Anthropic Claude models"""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available")
        
        self.model = model
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response dari Anthropic Claude"""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {json.dumps(context, indent=2)}\n\n{prompt}"
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    async def plan_next_action(self, goal: str, current_state: str, history: List[str]) -> Dict[str, Any]:
        """Plan next action menggunakan Claude"""
        prompt = f"""
Anda adalah autonomous agent yang dapat melakukan browser automation.

GOAL: {goal}

CURRENT STATE:
{current_state}

HISTORY:
{chr(10).join(history[-5:]) if history else "No previous actions"}

AVAILABLE TOOLS:
1. navigate(url) - Navigate to a URL
2. click(selector) - Click element by CSS selector or XPath  
3. type(selector, text) - Type text into input field
4. read_dom() - Read current page DOM
5. wait(seconds) - Wait for specified seconds

Berdasarkan goal dan current state, tentukan action selanjutnya.
Respond dalam format JSON:
{{
    "reasoning": "Penjelasan mengapa memilih action ini",
    "tool_name": "nama_tool", 
    "parameters": {{"param1": "value1"}},
    "expected_outcome": "Apa yang diharapkan terjadi"
}}
"""
        
        response = await self.generate_response(prompt)
        
        try:
            # Try to parse JSON response directly
            action_plan = json.loads(response)
            return action_plan
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown code block
            try:
                import re
                json_match = re.search(r'```json\n(.*?)```', response, re.DOTALL)
                if json_match:
                    action_plan = json.loads(json_match.group(1))
                    return action_plan
                else:
                    raise ValueError("No JSON found in LLM response")
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback jika response bukan JSON valid atau tidak ada JSON di markdown
                print(f"Failed to parse LLM response: {e}. Raw response: {response[:200]}...")
                return {
                    "reasoning": "Failed to parse LLM response",
                    "tool_name": "wait",
                    "parameters": {"seconds": 1},
                    "expected_outcome": "Wait and retry"
                }

def create_llm_interface(provider: str = "openai", **kwargs) -> LLMInterface:
    """Factory function untuk membuat LLM interface"""
    if provider.lower() == "openai":
        return OpenAIInterface(**kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicInterface(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

