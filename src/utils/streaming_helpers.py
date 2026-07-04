"""
Streaming helper utilities for character-level streaming and engaging NLP messages.
"""
import time
from typing import Generator, Dict, Any
import random


def stream_text_character_by_character(
    text: str,
    chunk_size: int = 1,
    delay: float = 0.01,
    event_type: str = "stream_char"
) -> Generator[Dict[str, Any], None, None]:
    """
    Stream text character-by-character for smooth typing effect.
    
    Args:
        text: Text to stream
        chunk_size: Number of characters to send at once (1 = character-by-character)
        delay: Delay between chunks in seconds
        event_type: Type of event to yield
        
    Yields:
        Dict with character/chunk data
    """
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        yield {
            "type": event_type,
            "char": chunk,
            "chunk": chunk  # For compatibility
        }
        if delay > 0:
            time.sleep(delay)


def generate_engaging_nlp_message(
    context: str,
    operation: str,
    details: Dict[str, Any] = None
) -> str:
    """
    Generate engaging NLP messages for non-streaming operations.
    Makes waiting for API calls (like temperature) more interesting.
    
    Args:
        context: Context of the operation (e.g., "temperature_analysis")
        operation: What operation is happening (e.g., "analyzing temperature patterns")
        details: Optional details to include in the message
        
    Returns:
        Engaging natural language message
    """
    messages = {
        "temperature_analysis": [
            "🌡️ Temperature patterns reveal fascinating insights about disease risk. Each degree matters in the delicate balance between plant health and pathogen activity.",
            "🌡️ Analyzing temperature data is like reading nature's thermometer. The subtle variations tell a story of potential disease development.",
            "🌡️ Temperature analysis is underway. These readings help us understand how environmental conditions influence disease progression in your crop.",
            "🌡️ Examining temperature patterns reveals critical information about disease risk. Optimal conditions for potato growth differ from those that favor pathogens.",
        ],
        "humidity_analysis": [
            "💧 Humidity levels are crucial for disease development. Moisture in the air creates the perfect environment for fungal spores to thrive and spread.",
            "💧 Analyzing humidity patterns helps us understand moisture dynamics. High humidity can accelerate disease progression, while low humidity may slow it down.",
            "💧 Humidity analysis reveals how atmospheric moisture influences disease risk. These patterns are essential for accurate predictions.",
        ],
        "precipitation_analysis": [
            "🌧️ Rainfall patterns are being analyzed. Water from above can both nourish crops and create conditions that favor disease development.",
            "🌧️ Precipitation data tells a story of moisture availability. Understanding these patterns helps predict disease outbreaks with greater accuracy.",
            "🌧️ Analyzing rainfall patterns reveals critical information about disease risk. Water is essential for life, but it can also spread pathogens.",
        ],
        "weather_collection": [
            "🌤️ Gathering comprehensive weather data from multiple sources. This information forms the foundation of accurate disease predictions.",
            "🌤️ Collecting weather data is like assembling pieces of a puzzle. Each parameter contributes to a complete picture of disease risk.",
            "🌤️ Weather data collection is in progress. These environmental factors are key to understanding disease development patterns.",
        ],
        "ai_analysis": [
            "🤖 The AI is analyzing complex patterns in the data. Machine learning models are identifying subtle correlations that human analysis might miss.",
            "🤖 Advanced AI algorithms are processing the data. These models have been trained on thousands of disease cases to provide accurate predictions.",
            "🤖 AI analysis is uncovering hidden patterns in the data. This sophisticated analysis helps us make more accurate disease risk assessments.",
        ],
        "tavily_search": [
            "🔍 Searching through agricultural research databases. Finding location-specific recommendations based on scientific literature and historical data.",
            "🔍 Researching treatment recommendations from trusted sources. Combining scientific knowledge with practical agricultural experience.",
            "🔍 Gathering location-specific research data. This helps us provide recommendations tailored to your specific growing conditions.",
        ],
    }
    
    # Get messages for this context
    context_messages = messages.get(context, [
        f"Processing {operation}...",
        f"Analyzing {operation}...",
        f"Working on {operation}..."
    ])
    
    # Select a random message
    message = random.choice(context_messages)
    
    # Add details if provided
    if details:
        if "location" in details:
            message = message.replace("your crop", f"your crop in {details['location']}")
        if "disease" in details:
            message = message.replace("disease", details['disease'])
    
    return message


def stream_engaging_message(
    context: str,
    operation: str,
    details: Dict[str, Any] = None,
    delay: float = 0.02
) -> Generator[Dict[str, Any], None, None]:
    """
    Stream an engaging NLP message character-by-character.
    Used during non-streaming API calls to keep users engaged.
    
    Args:
        context: Context of the operation
        operation: What operation is happening
        details: Optional details
        delay: Delay between characters
        
    Yields:
        Character-by-character streaming events
    """
    message = generate_engaging_nlp_message(context, operation, details)
    yield from stream_text_character_by_character(message, delay=delay, event_type="stream_char")

