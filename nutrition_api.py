"""
Nutrition API wrapper for USDA FoodData Central
Free API with no rate limits - https://fdc.nal.usda.gov/api-guide.html
"""
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class NutritionAPI:
    """Wrapper for USDA FoodData Central API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the nutrition API client
        
        Args:
            api_key: USDA API key (optional - API works without it but with limits)
        """
        self.api_key = api_key or "DEMO_KEY"  # DEMO_KEY allows 30 requests/hour
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
    
    def search_food(self, query: str, page_size: int = 5) -> List[Dict]:
        """
        Search for foods by name
        
        Args:
            query: Search term (e.g., "banana", "pasta")
            page_size: Number of results to return
            
        Returns:
            List of food items with name, fdcId, and description
        """
        try:
            url = f"{self.base_url}/foods/search"
            params = {
                "api_key": self.api_key,
                "query": query,
                "pageSize": page_size,
                "dataType": ["Foundation", "SR Legacy"]  # Use high-quality data
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            foods = data.get("foods", [])
            
            return [
                {
                    "fdcId": food.get("fdcId"),
                    "description": food.get("description"),
                    "dataType": food.get("dataType")
                }
                for food in foods[:page_size]
            ]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching food '{query}': {e}")
            return []
    
    def get_food_calories(self, fdc_id: int) -> Optional[int]:
        """
        Get calories for a specific food by FDC ID
        
        Args:
            fdc_id: USDA FoodData Central ID
            
        Returns:
            Calories per 100g or None if not found
        """
        try:
            url = f"{self.base_url}/food/{fdc_id}"
            params = {"api_key": self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Find energy nutrient (calories)
            nutrients = data.get("foodNutrients", [])
            for nutrient in nutrients:
                nutrient_info = nutrient.get("nutrient", {})
                # Look for Energy (nutrient ID 1008)
                if nutrient_info.get("number") == "208" or nutrient_info.get("name", "").lower() == "energy":
                    amount = nutrient.get("amount", 0)
                    return int(amount)
            
            logger.warning(f"No calorie information found for FDC ID {fdc_id}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting calories for FDC ID {fdc_id}: {e}")
            return None
    
    def estimate_calories_from_ingredients(self, ingredients_text: str) -> Optional[int]:
        """
        Estimate total calories from an ingredients string
        
        Args:
            ingredients_text: Comma-separated ingredients (e.g., "pasta, tomato, cheese")
            
        Returns:
            Estimated total calories or None if unable to calculate
        """
        if not ingredients_text or ingredients_text.strip() == "":
            return None
        
        # Split ingredients by common separators
        separators = [",", ";", "\n", " e ", " and "]
        ingredients_list = [ingredients_text]
        
        for sep in separators:
            new_list = []
            for item in ingredients_list:
                new_list.extend(item.split(sep))
            ingredients_list = new_list
        
        # Clean up ingredient names
        ingredients_list = [ing.strip() for ing in ingredients_list if ing.strip()]
        
        if not ingredients_list:
            return None
        
        logger.info(f"Searching calories for {len(ingredients_list)} ingredients: {ingredients_list}")
        
        total_calories = 0
        found_count = 0
        
        for ingredient in ingredients_list[:5]:  # Limit to first 5 ingredients to avoid rate limits
            # Search for the ingredient
            foods = self.search_food(ingredient, page_size=1)
            
            if foods:
                fdc_id = foods[0].get("fdcId")
                calories = self.get_food_calories(fdc_id)
                
                if calories:
                    # Use a standard portion estimate (100g)
                    total_calories += calories
                    found_count += 1
                    logger.info(f"  {ingredient}: {calories} kcal/100g")
                else:
                    logger.warning(f"  {ingredient}: calories not found")
            else:
                logger.warning(f"  {ingredient}: not found in database")
        
        if found_count == 0:
            logger.warning("No ingredients found in database")
            return None
        
        # Average across ingredients found (rough estimate)
        logger.info(f"Total estimated calories: {total_calories} kcal (from {found_count}/{len(ingredients_list)} ingredients)")
        
        return total_calories if total_calories > 0 else None


def test_api():
    """Test function for the nutrition API"""
    api = NutritionAPI()
    
    # Test 1: Search for a single food
    print("\n=== Test 1: Search for 'banana' ===")
    foods = api.search_food("banana")
    for food in foods:
        print(f"  - {food['description']}")
    
    # Test 2: Get calories for first result
    if foods:
        print(f"\n=== Test 2: Get calories for '{foods[0]['description']}' ===")
        calories = api.get_food_calories(foods[0]['fdcId'])
        print(f"  Calories: {calories} kcal/100g")
    
    # Test 3: Estimate calories from ingredients
    print("\n=== Test 3: Estimate calories from 'pasta, tomato, olive oil' ===")
    total = api.estimate_calories_from_ingredients("pasta, tomato, olive oil")
    print(f"  Total estimated: {total} kcal")


if __name__ == "__main__":
    # Run tests
    test_api()
