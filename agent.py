import os
import requests
from datetime import datetime
from typing import Dict, List

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Diccionario simple para mantener el historial en memoria
conversation_history: Dict[str, List[dict]] = {}

def add_to_history(user_id: str, role: str, content: str):
    """Agrega un mensaje al historial de conversación en memoria."""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # Mantener solo los últimos 5 mensajes para no sobrecargar la memoria
    if len(conversation_history[user_id]) >= 10:
        conversation_history[user_id] = conversation_history[user_id][-9:]
    
    conversation_history[user_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

def get_conversation_context(user_id: str) -> str:
    """Obtiene el contexto de la conversación desde la memoria."""
    if user_id not in conversation_history or not conversation_history[user_id]:
        return "No hay conversación previa."
    
    context = "Contexto de la conversación anterior:\n"
    for msg in conversation_history[user_id][-3:]:  # Últimos 3 mensajes
        role = "Usuario" if msg["role"] == "user" else "Asistente"
        context += f"{role}: {msg['content']}\n"
    return context

def search_web(query):
    """Hace una búsqueda en SerpAPI y devuelve los resultados principales."""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "num": 3,
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []

    if "organic_results" in data:
        for result in data["organic_results"]:
            title = result.get("title")
            link = result.get("link")
            if title and link:
                results.append(f"{title}: {link}")

    return "\n".join(results) if results else "No se encontraron resultados."

def ask_agent(message: str, user_id: str = "default"):
    """Procesa la consulta usando OpenRouter (razonamiento) y SerpAPI (búsqueda)."""
    # Paso 1: Buscar información en la web (opcional)
    web_results = search_web(message)

    # Obtener contexto de la conversación
    conversation_context = get_conversation_context(user_id)

    # Paso 2: Preguntar al modelo
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = """Eres un asistente experto que sigue un proceso estructurado para responder preguntas.
Tienes acceso al contexto de la conversación anterior para dar respuestas más coherentes y personalizadas.

1. ANÁLISIS:
   - Analiza la pregunta del usuario y el contexto de la conversación
   - Identifica los puntos clave a responder
   
2. INVESTIGACIÓN:
   - Revisa los resultados de búsqueda proporcionados
   - Identifica información relevante
   - Relaciona con conversaciones anteriores si es relevante
   
3. SÍNTESIS:
   - Combina tu conocimiento con la información encontrada
   - Organiza las ideas de manera lógica
   - Mantén coherencia con respuestas anteriores
   
4. RESPUESTA:
   - Proporciona una respuesta clara y estructurada
   - Incluye referencias cuando sea relevante
   - Mantén un tono profesional pero amigable
   - Haz referencias a la conversación anterior cuando sea útil

Formato de respuesta:
-------------------
💭 Análisis: [Breve análisis de la pregunta y contexto]

🔍 Información relevante: [Puntos clave encontrados]

📝 Respuesta: [Respuesta principal]

🔗 Fuentes: [Si aplica, lista de fuentes relevantes]"""

    payload = {
        "model": "microsoft/mai-ds-r1:free",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Contexto anterior:\n{conversation_context}\n\nConsulta actual: {message}\n\nResultados de búsqueda web:\n{web_results}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    
    if response.status_code == 200:
        response_content = response.json()['choices'][0]['message']['content']
        # Guardar la interacción en el historial
        add_to_history(user_id, "user", message)
        add_to_history(user_id, "assistant", response_content)
        return response_content
    else:
        error_message = f"Error en OpenRouter: {response.text}"
        add_to_history(user_id, "system", error_message)
        return error_message
