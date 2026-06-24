import json
import google.generativeai as genai

def analyze_vendor_document(api_key, document_text, custom_prompt):
    """
    Sends the document text and custom prompt to Gemini API,
    requesting a structured JSON response for TPRM analysis.
    """
    genai.configure(api_key=api_key)
    
    prompt = f"""
    You are an expert Third-Party Risk Management (TPRM) AI. 
    Analyze the provided vendor document text. 
    Adhere to the user's custom instructions if provided.
    
    Extract the following information and return ONLY a valid JSON object with the following schema:
    {{
        "vendor": "Vendor Name",
        "scope": "Services provided and data types handled",
        "risk_score": "Critical", "High", "Medium", or "Low",
        "findings": ["Finding 1", "Finding 2"],
        "next_steps": ["Step 1", "Step 2"],
        "summary": "2-3 sentences explaining their context.",
        "postscript": "A 1-paragraph, ultra-concise status summary for leadership."
    }}

    Custom Instructions from User: {custom_prompt}
    
    --- Vendor Document Text ---
    {document_text[:30000]}
    """
    try:
        # Dynamically fetch available models for this API key
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not valid_models:
            return {"error": "No generative models found for this API key. Please check your Google AI Studio account."}
            
        # Build ordered list of models to try
        models_to_try = []
        preferences = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-pro']
        for pref in preferences:
            for vm in valid_models:
                if pref in vm and vm not in models_to_try:
                    models_to_try.append(vm)
                    
        if not models_to_try:
            models_to_try = valid_models
            
        last_error = ""
        for selected_model in models_to_try:
            try:
                model = genai.GenerativeModel(model_name=selected_model)
                response = model.generate_content(prompt)
                
                # Parse JSON
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                result = json.loads(text.strip())
                return result
            except Exception as e:
                last_error = str(e)
                # If the quota limit is hard-coded to 0 (model unavailable for this tier/region), try the next model!
                if "limit: 0" in last_error or "404" in last_error:
                    continue
                # If it's a standard rate limit (e.g. 15 per minute), return it so app.py can wait 45s and retry
                return {"error": f"API Error (Model: {selected_model}): {last_error}"}
                
        return {"error": f"All available models failed or have 0 quota. Last error: {last_error}"}
    except Exception as e:
        return {"error": f"Global API Error: {str(e)}"}
