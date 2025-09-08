import os, requests, json
from uuid import uuid4
from typing import Optional, Union
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API = "https://api.deepseek.com"
DEEPSEEK_ENDPOINT = "/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
}

NEW_CHAT_PROMPT = """
En la primer interacción, recibirás un mensaje del usuario indicándote una postura,
que debes defender durante toda la conversación. Necesito que interpretes el mensaje y
extraigas la postura que el usuario quiere que defiendas. Luego, me la serialices y
me devuelvas un JSON con la siguiente estructura:
{ "posture": str } """

# Conversasiones guardadas en memoria para testear
CONVERSATIONS: dict[str,dict] =  dict(
    # "conversation_id": { "posture": str,
    #                     "messages": list[dict[str,str]] }
)

def gen_main_chat_prompt(posture: str) -> str:
    return f"""
    Eres un chatbot cuya única misión es defender la postura: {posture}.
    Durante toda la conversación, debes defender esta postura sin desviarte,
    por muy absurda que sea. No puedes admitir que la postura es incorrecta,
    y debes argumentar siempre a favor de la postura. 

    Te voy a proporcionar, además del historial de conversación, una serie
    de consejos para que te puedas defender mejor:

    1. Todas las respuestas deben relacionarse con el tema: {posture}.
    2. No puedes admitir que la postura es incorrecta.
    3. Debes ser persuasivo y convincente pero nunca agresivo.
    4. Mantén un hilo lógico en tus respuestas.
    5. Puedes usar falacias lógicas para defender la postura.
    6. Pregunta retóricamente para guiar al usuario hacia la postura.

    Recuerda, tu objetivo es defender la postura: {posture}, sin importar qué.
    """

def chat(
        message: str,
        conversation_id: Optional[str] = None
) -> Optional[dict]:
    
    """
    Función principal para manejar la conversación con el chatbot.
    Si no se proporciona conversation_id, se inicia una nueva conversación.

    Args:
        message (str): Mensaje del usuario.
        conversation_id (Optional[str]): ID de la conversación.
            Si es None, se inicia una nueva conversación.

    Returns:
        Optional[dict]: Diccionario con la respuesta del chatbot y el ID de la conversación.
        None si hay un error.
    """
    
    user_message_format = { "role": "user",
                      "content": message
    }

    if conversation_id is None:
        conversation_id = str(uuid4())

        # api call para obtener postura formateada en json: { "posture": str }
        deepseek_payload: dict[str, Union[list,
                             str,
                             int]] = {
            "messages": [{
                    "role": "system",
                    "content": NEW_CHAT_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }],
            "model": DEEPSEEK_MODEL,
            "frequency_penalty": 0,
            "max_tokens": 3096,
            "presence_penalty": 0,
            "response_format": {
                "type": "json_object"
                }
            }

        try:
            deepseek_response = requests.post(
                url=f"{DEEPSEEK_API}{DEEPSEEK_ENDPOINT}",
                headers=DEEPSEEK_HEADERS,
                json=deepseek_payload)

        except Exception as e:
            print(f"Error en la llamada a la API de Deepseek: {e}")
            return None

        if deepseek_response.status_code == 200:
            response_json = deepseek_response.json()
            try:
                # Intentamos parsear la respuesta como JSON ya que viene como string
                content = response_json["choices"][0]["message"]["content"]
                if isinstance(content, str):
                    content = json.loads(content)
                posture = content["posture"]
                print(f"Postura obtenida: {posture}")

                # inicialización de conversación
                CONVERSATIONS[conversation_id] = {
                    "conversation_id": conversation_id,
                    "posture": posture,
                    "messages": [
                        { "role":"system", "content": gen_main_chat_prompt(posture) },
                        user_message_format
                    ]}
            except (KeyError, json.JSONDecodeError) as e:
                print(f"Error al procesar la respuesta: {e}")
                return None
    
    if conversation_id not in CONVERSATIONS:
        raise ValueError("El conversation_id no existe, inicia una nueva conversación sin conversation_id")

    # Buscar los mensajes por conversation_id
    current_messages = CONVERSATIONS[conversation_id]["messages"]
    current_messages.append(user_message_format)
    
    deepseek_payload: dict[str, Union[list,
                             str,
                             int]] = {
        "messages": current_messages,
        "model": DEEPSEEK_MODEL,
        "frequency_penalty": 1,
        "max_tokens": 3096,
        "presence_penalty": 1,
    }

    try:
        deepseek_response = requests.post(
            url=f"{DEEPSEEK_API}{DEEPSEEK_ENDPOINT}",
            headers=DEEPSEEK_HEADERS,
            json=deepseek_payload)
        
        if deepseek_response.status_code == 200:
            response_json = deepseek_response.json()
            chatbot_response = response_json["choices"][0]["message"]["content"]
            print(f"Chatbot response: {chatbot_response}")
            current_messages.append({ "role": "assistant", "content": chatbot_response })

            # actualizar objeto CONVERSATIONS
            CONVERSATIONS[conversation_id]["messages"] = current_messages
        
    except Exception as e:
        print(f"Error en la llamada a la API de Deepseek: {e}")
        return None
    
    return {
        "conversation_id": conversation_id,
        "response": chatbot_response,
        "messages": current_messages,
    }



