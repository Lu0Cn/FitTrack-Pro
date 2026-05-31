import os
import json
from openai import OpenAI

# Initialize client with placeholder, will be updated with user key at runtime
# DeepSeek API uses OpenAI-compatible endpoint
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

def get_client(api_key):
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

def parse_food_log(api_key, text_input, lang='en'):
    """
    Parses natural language food input into structured JSON.
    Example: "2 eggs and toast" -> [{"food": "Egg", "calories": 140...}, ...]
    """
    client = get_client(api_key)
    if not client:
        return {"error": "No API Key provided"}

    lang_instruction = "Respond in JSON only."
    if lang == 'zh':
        lang_instruction += " Ensure food_name is in Chinese if the input is Chinese."

    prompt = f"""
    You are a Nutritionist AI. Analyze the following food log text:
    "{text_input}"

    Return ONLY a JSON array with the nutritional breakdown for each item. 
    Format:
    [
        {{
            "food_name": "Standardized Name",
            "quantity": "estimated quantity",
            "calories": number (kcal),
            "protein": number (g),
            "carbs": number (g),
            "fat": number (g)
        }}
    ]
    Estimate values based on standard portion sizes if not specified.
    Do not output markdown code blocks, just raw JSON.
    {lang_instruction}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        # Clean up if model adds markdown formatting
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

def generate_daily_advice(api_key, user_profile, daily_data, recent_weight_trend, lang='en'):
    """
    Generates personalized advice based on the day's data.
    """
    client = get_client(api_key)
    if not client:
        return "Please configure your API Key in Settings to get AI advice."

    context = f"""
    User Profile: {user_profile}
    Today's Data: {daily_data}
    Recent Weight Trend: {recent_weight_trend}
    """

    lang_instruction = "Respond in English."
    if lang == 'zh':
        lang_instruction = "Respond in Chinese (Simplified)."

    prompt = f"""
    You are a compassionate but strict Health Coach. Based on the user's data today:
    {context}

    Provide a concise bullets-point summary (max 3 points):
    1. Acknowledgment (Good job or Needs improvement)
    2. Specific observation (e.g., "Protein is low", "Sleep was great")
    3. Actionable tip for tomorrow.
    Keep it under 100 words.
    {lang_instruction}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate advice: {str(e)}"

def chat_with_coach(api_key, message, history=[]):
    """
    General Q&A with context.
    """
    client = get_client(api_key)
    if not client:
        return "Please configure your API Key."

    messages = [{"role": "system", "content": "You are a helpful Health & Fitness Coach."}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
