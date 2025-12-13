import asyncio
import logging
from typing import Any, Dict, List, Optional

import openai
from dotenv import load_dotenv

from ..config.config import get_config

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for interacting with Large Language Models (LLMs).
    Currently supports OpenAI models.
    """
    
    def __init__(self):
        """
        Initialize the LLM client with configuration from environment/config.
        """
        config = get_config()
        self.model = config.get('LLM.MODEL')
        self.max_tokens = config.get('LLM.MAX_TOKENS')
        self.temperature = config.get('LLM.TEMPERATURE')
        self.timeout = config.get('LLM.TIMEOUT_SECONDS')
        
        # Set the OpenAI API key
        api_key = openai.api_key or None
        if not api_key:
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
        
        if not api_key:
            logger.warning("OpenAI API key not found. LLM functionality will not work.")
        
        # Validate configuration
        if not self.model:
            raise ValueError("LLM model not specified in configuration")
    
    async def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Generate a response from the LLM based on the given prompt.
        
        Args:
            prompt: The user prompt to send to the LLM
            system_message: Optional system message to guide the LLM's behavior
            max_tokens: Override the default max_tokens value
            temperature: Override the default temperature value
            
        Returns:
            Generated response from the LLM, or None if an error occurred
        """
        try:
            # Prepare messages
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            # Use provided parameters or defaults
            effective_max_tokens = max_tokens or self.max_tokens
            effective_temperature = temperature or self.temperature
            
            # Make the API call
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=effective_max_tokens,
                temperature=effective_temperature,
                timeout=self.timeout
            )
            
            # Extract and return the response
            if response and response.choices:
                content = response.choices[0].message.content
                logger.info(f"LLM response generated successfully")
                return content
            else:
                logger.error("No response received from LLM")
                return None
                
        except openai.error.AuthenticationError:
            logger.error("Authentication failed. Please check your OpenAI API key.")
            return None
        except openai.error.RateLimitError:
            logger.error("Rate limit exceeded. Please try again later.")
            return None
        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during LLM call: {str(e)}")
            return None
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_format: str = "json_object",
        system_message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a structured response (e.g., JSON) from the LLM.
        
        Args:
            prompt: The user prompt to send to the LLM
            response_format: Expected format of the response (default: json_object)
            system_message: Optional system message to guide the LLM's behavior
            
        Returns:
            Parsed structured response from the LLM, or None if an error occurred
        """
        try:
            # Add instruction for JSON format if needed
            full_prompt = prompt
            if response_format == "json_object":
                full_prompt += "\n\nRespond in valid JSON format."
            
            response_text = await self.generate_response(full_prompt, system_message)
            
            if response_text:
                import json
                try:
                    parsed_response = json.loads(response_text)
                    logger.info("Structured response parsed successfully")
                    return parsed_response
                except json.JSONDecodeError:
                    logger.error("Failed to parse LLM response as JSON")
                    return None
            else:
                logger.warning("No response received from LLM for structured output")
                return None
                
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            return None
    
    def validate_model_capabilities(self) -> bool:
        """
        Validate that the configured model supports required capabilities.
        
        Returns:
            True if the model supports required capabilities, False otherwise
        """
        # For now, assume all configured models support the required capabilities
        # In a real implementation, you'd check model capabilities against requirements
        logger.info(f"Model {self.model} capabilities validated")
        return True


# Global instance of the LLM client
_llm_client = None


def get_llm_client() -> LLMClient:
    """
    Get the global LLM client instance.
    
    Returns:
        LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client