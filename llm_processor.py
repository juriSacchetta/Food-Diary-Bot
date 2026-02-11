"""
LLM-based meal analyzer using Google Gemini for quick unstructured meal registration
"""
import os
import json
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Run: pip install google-generativeai")


class LLMProcessor:
    """Process unstructured meal input using Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini processor
        
        Args:
            api_key: Google Gemini API key (optional, reads from env if not provided)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Get free key at: "
                "https://aistudio.google.com/app/apikey"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 1.5 Flash (fast, free tier available)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Gemini LLM processor initialized")
    
    async def analyze_meal(
        self, 
        text: str, 
        photo_path: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Analyze meal from text and/or photo using Gemini
        
        Args:
            text: User's text description (can be empty)
            photo_path: Path to meal photo (optional)
        
        Returns:
            {
                'meal_type': 'main' or 'snack',
                'meal_type_label': 'Pasto Principale' or 'Snack',
                'ingredients': 'pasta, pomodoro, formaggio',
                'calories': 650,
                'weight': '400g' (optional),
                'description': 'Full meal description'
            }
            or None if analysis fails
        """
        
        # Build the prompt
        system_instruction = """You are a food diary assistant for an Italian user. 
Analyze the meal description and/or photo and extract structured information.

IMPORTANT: Return ONLY valid JSON with this exact structure:
{
  "meal_type": "main" or "snack",
  "ingredients": "comma-separated list in Italian",
  "calories": estimated_calories_as_integer,
  "weight": "estimated weight if visible or mentioned (e.g., '350g')",
  "description": "brief description in Italian"
}

Rules:
1. meal_type: Use "main" for breakfast/lunch/dinner, "snack" for small portions/snacks/desserts
2. ingredients: List main ingredients in Italian, comma-separated
3. calories: Estimate based on typical Italian portions (be realistic)
4. weight: Extract if mentioned in text (e.g., "350g", "2 fette") or estimate from photo
5. description: Brief summary in Italian for user confirmation
6. If photo is unclear or text is vague, make reasonable assumptions
7. Always return valid JSON - no markdown, no explanations, just JSON

Examples:
Input: "Pizza margherita 🍕"
Output: {"meal_type": "main", "ingredients": "pizza, mozzarella, pomodoro, basilico", "calories": 800, "weight": "300g", "description": "Pizza margherita"}

Input: "Snack: mela e yogurt"
Output: {"meal_type": "snack", "ingredients": "mela, yogurt", "calories": 150, "weight": "150g", "description": "Mela e yogurt"}

Input: [photo of pasta plate]
Output: {"meal_type": "main", "ingredients": "pasta, sugo, parmigiano", "calories": 650, "weight": "350g", "description": "Piatto di pasta"}"""

        # Prepare content parts
        content_parts = []
        
        # Add text if provided
        if text and text.strip():
            content_parts.append(f"User input: {text}")
        else:
            content_parts.append("Analyze this meal photo:")
        
        # Add photo if provided
        if photo_path and os.path.exists(photo_path):
            try:
                # Upload image to Gemini
                image = Path(photo_path)
                content_parts.append(genai.upload_file(photo_path))
                logger.info(f"Uploaded photo to Gemini: {photo_path}")
            except Exception as e:
                logger.error(f"Failed to upload photo: {e}")
        
        try:
            # Generate response
            response = self.model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['meal_type', 'ingredients', 'calories', 'description']
            for field in required_fields:
                if field not in result:
                    logger.error(f"Missing required field: {field}")
                    return None
            
            # Ensure meal_type is valid
            if result['meal_type'] not in ['main', 'snack']:
                logger.warning(f"Invalid meal_type: {result['meal_type']}, defaulting to 'main'")
                result['meal_type'] = 'main'
            
            # Add label for display
            result['meal_type_label'] = (
                "Pasto Principale" if result['meal_type'] == 'main' else "Snack"
            )
            
            # Ensure calories is an integer
            try:
                result['calories'] = int(result['calories'])
            except (ValueError, TypeError):
                logger.warning(f"Invalid calories value: {result['calories']}, setting to None")
                result['calories'] = None
            
            logger.info(f"Gemini analyzed meal: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response was: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return None
    
    def analyze_meal_sync(
        self, 
        text: str, 
        photo_path: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Synchronous version of analyze_meal for non-async contexts
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.analyze_meal(text, photo_path))


# Test function
def test_gemini():
    """Test Gemini integration with various inputs"""
    
    print("\n" + "="*60)
    print("TESTING GEMINI LLM PROCESSOR")
    print("="*60)
    
    try:
        processor = LLMProcessor()
        print("✅ Gemini processor initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test 1: Text only - Italian
    print("\n--- Test 1: Text only (Italian) ---")
    print("Input: 'Pizza margherita 🍕'")
    result = processor.analyze_meal_sync(text="Pizza margherita 🍕")
    if result:
        print("✅ Success:")
        print(f"  Type: {result['meal_type_label']}")
        print(f"  Ingredients: {result['ingredients']}")
        print(f"  Calories: {result['calories']} kcal")
        print(f"  Weight: {result.get('weight', 'N/A')}")
        print(f"  Description: {result['description']}")
    else:
        print("❌ Failed")
    
    # Test 2: Text with weight
    print("\n--- Test 2: Text with weight ---")
    print("Input: 'Pasta al pomodoro, circa 350g'")
    result = processor.analyze_meal_sync(text="Pasta al pomodoro, circa 350g")
    if result:
        print("✅ Success:")
        print(f"  Type: {result['meal_type_label']}")
        print(f"  Ingredients: {result['ingredients']}")
        print(f"  Calories: {result['calories']} kcal")
        print(f"  Weight: {result.get('weight', 'N/A')}")
    else:
        print("❌ Failed")
    
    # Test 3: Snack
    print("\n--- Test 3: Snack ---")
    print("Input: 'Mela e yogurt greco'")
    result = processor.analyze_meal_sync(text="Mela e yogurt greco")
    if result:
        print("✅ Success:")
        print(f"  Type: {result['meal_type_label']}")
        print(f"  Ingredients: {result['ingredients']}")
        print(f"  Calories: {result['calories']} kcal")
    else:
        print("❌ Failed")
    
    # Test 4: English input (should work too)
    print("\n--- Test 4: English input ---")
    print("Input: 'Big bowl of spaghetti carbonara, about 400g'")
    result = processor.analyze_meal_sync(text="Big bowl of spaghetti carbonara, about 400g")
    if result:
        print("✅ Success:")
        print(f"  Type: {result['meal_type_label']}")
        print(f"  Ingredients: {result['ingredients']}")
        print(f"  Calories: {result['calories']} kcal")
        print(f"  Weight: {result.get('weight', 'N/A')}")
    else:
        print("❌ Failed")
    
    # Test 5: Minimal input
    print("\n--- Test 5: Minimal input ---")
    print("Input: '🍝'")
    result = processor.analyze_meal_sync(text="🍝")
    if result:
        print("✅ Success:")
        print(f"  Type: {result['meal_type_label']}")
        print(f"  Ingredients: {result['ingredients']}")
        print(f"  Calories: {result['calories']} kcal")
    else:
        print("❌ Failed")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run tests
    test_gemini()
