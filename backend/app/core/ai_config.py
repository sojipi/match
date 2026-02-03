"""
AI and AgentScope configuration.
"""
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global flags for AI service availability
AGENTSCOPE_AVAILABLE = False
GEMINI_AVAILABLE = False

def initialize_agentscope() -> bool:
    """Initialize AgentScope framework."""
    global AGENTSCOPE_AVAILABLE
    
    try:
        import agentscope
        from agentscope.agent import AgentBase
        
        # Simple initialization without complex model configurations for now
        # AgentScope 1.0+ has a different initialization approach
        AGENTSCOPE_AVAILABLE = True
        logger.info("AgentScope initialized successfully")
        return True
            
    except ImportError:
        logger.warning("AgentScope not available - install with: pip install agentscope")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize AgentScope: {e}")
        return False


def initialize_gemini() -> bool:
    """Initialize Gemini API."""
    global GEMINI_AVAILABLE
    
    try:
        import google.genai as genai
        
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Test the API connection
            model = genai.GenerativeModel('gemini-pro')
            test_response = model.generate_content("Hello")
            
            if test_response and test_response.text:
                GEMINI_AVAILABLE = True
                logger.info("Gemini API initialized and tested successfully")
                return True
            else:
                logger.warning("Gemini API test failed - no response received")
                return False
        else:
            logger.warning("Gemini API key not configured")
            return False
            
    except ImportError:
        logger.warning("Google Generative AI not available - install with: pip install google-genai")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {e}")
        return False


def initialize_ai_services() -> Dict[str, bool]:
    """Initialize all AI services."""
    logger.info("Initializing AI services...")
    
    results = {
        "agentscope": initialize_agentscope(),
        "gemini": initialize_gemini()
    }
    
    # Log overall status
    available_services = [service for service, available in results.items() if available]
    if available_services:
        logger.info(f"AI services initialized: {', '.join(available_services)}")
    else:
        logger.warning("No AI services available - running in mock mode")
    
    return results


def get_ai_service_status() -> Dict[str, Any]:
    """Get current AI service status."""
    return {
        "agentscope_available": AGENTSCOPE_AVAILABLE,
        "gemini_available": GEMINI_AVAILABLE,
        "mock_mode": not (AGENTSCOPE_AVAILABLE or GEMINI_AVAILABLE),
        "services": {
            "agentscope": {
                "available": AGENTSCOPE_AVAILABLE,
                "description": "Multi-agent conversation framework"
            },
            "gemini": {
                "available": GEMINI_AVAILABLE,
                "description": "Google Gemini API for AI responses"
            }
        }
    }


# Mock model wrapper for testing
class MockModelWrapper:
    """Mock model wrapper for testing when real AI services are unavailable."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.responses = config.get("responses", ["I understand.", "That's interesting.", "Tell me more."])
        self.response_index = 0
    
    def __call__(self, messages, **kwargs):
        """Generate mock response."""
        # Cycle through predefined responses
        response = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1
        
        # Return response in expected format
        class MockResponse:
            def __init__(self, text):
                self.content = text
                self.text = text
        
        return MockResponse(response)


# Configuration for different AI models
AI_MODEL_CONFIGS = {
    "gemini_pro": {
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
        "top_k": 40
    },
    "mock_model": {
        "responses": [
            "That's really interesting! I'd love to hear more about that.",
            "I can definitely relate to that experience.",
            "What do you think is the most important aspect of that?",
            "That sounds like it was quite meaningful to you.",
            "How did that situation make you feel?",
            "I appreciate you sharing that with me.",
            "That's a great perspective on things.",
            "What would you do differently if you faced that again?"
        ]
    }
}


def get_model_config(model_name: str) -> Dict[str, Any]:
    """Get configuration for a specific AI model."""
    return AI_MODEL_CONFIGS.get(model_name, AI_MODEL_CONFIGS["mock_model"])


def is_ai_service_available(service_name: str) -> bool:
    """Check if a specific AI service is available."""
    if service_name == "agentscope":
        return AGENTSCOPE_AVAILABLE
    elif service_name == "gemini":
        return GEMINI_AVAILABLE
    else:
        return False


def get_available_models() -> list[str]:
    """Get list of available AI models."""
    models = ["mock_model"]  # Always available
    
    if GEMINI_AVAILABLE:
        models.extend(["gemini-pro", "gemini-pro-vision"])
    
    return models