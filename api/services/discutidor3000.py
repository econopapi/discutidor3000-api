
import requests, json
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Union, Optional
from dotenv import load_dotenv

from ..structures import ChatRequest, ChatResponse, Message, Conversation

load_dotenv()

class Discutidor3000:
    """Chatbot que defiente una postura dada durante toda la conversación."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_base = "https://api.deepseek.com"
        self.api_endpoint = "/chat/completions"
        self.api_key = api_key
        self.model = "deepseek-chat"
        self.temperature = 0.7
        self.max_tokens = 3750
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        self.conversations: Dict[str, List[Dict]] = {}
        self.new_chat_prompt = """
        En la primer interacción, recibirás un mensaje del usuario indicándote una postura,
        que debes defender durante toda la conversación. Necesito que interpretes el mensaje y
        extraigas la postura que el usuario quiere que defiendas. Luego, me la serialices y
        me devuelvas un JSON con la siguiente estructura:
        { "posture": str }
        """


    def _gen_system_prompt(self, posture: str) -> str:
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


    def _api_request(self,
                     messages: List[Dict[str,str]],
                     use_json: bool = False) -> Optional[Dict]:
        """Esta función centraliza toda la comunicación con la API de DeepSeek.
        Args:
            messages (List[Dict[str,str]]): Lista de mensajes en el formato esperado por la API.
            use_json (bool): Si es True, se espera que la respuesta sea un JSON.
        Returns:
            Optional[Dict]: Respuesta de la API en formato JSON.
            None si hay un error."""
        payload = {
            "messages": messages,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens  
        }

        if use_json:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            response = requests.post(
                url = f"{self.api_base}{self.api_endpoint}",
                headers=self.headers,
                json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f" > [!] Error en la API: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f" > [!] Error en la petición a la API: {e}")
            return None
        

    def _get_posture(self, message: str) -> Optional[str]:
        """Extrae la postura del mensaje inicial del usuario.
        Args
            message (str): Mensaje del usuario.
        Returns:
            Optional[str]: Postura extraída del mensaje.
            None si hay un error."""
        messages = [
            {"role": "system", "content": self.new_chat_prompt},
            {"role": "user", "content": message}
        ]

        response = self._api_request(messages, use_json=True)
        if response is None:
            return None
        
        try:
            content = response["choices"][0]["message"]["content"]
            if isinstance(content, str):
                content = json.loads(content)
            posture = content["posture"]
            return posture
        except Exception as e:
            print(f" > [!] Error al extraer la postura: {e}")
            return None
        

    def _init_conversation(self,
                           conversation_id: str,
                           posture: str,
                           initial_message: str) -> None:
        """Inicializa una nueva conversación.
        Args:
            conversation_id (str): ID de la conversación.
            posture (str): Postura a defender.
            initial_message (str): Mensaje inicial del usuario."""
        conversation = Conversation(
            conversation_id=conversation_id,
            posture=posture,
            messages=[
                Message(role="system", content=self._gen_system_prompt(posture)),
                Message(role="user", content=initial_message)
            ],
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        self.conversations[conversation_id] = conversation.model_dump()
        # self.conversations[conversation_id] = {
        #     "conversation_id": conversation_id,
        #     "posture": posture,
        #     "messages": [
        #         {"role": "system", "content": self._gen_system_prompt(posture)},
        #         {"role": "user", "content": initial_message} ]}
        

    def _gen_response(self, conversation_id: str) -> Optional[Dict]:
        """Genera una respuesta del chatbot para una conversación existente.,
        utilizando el historial de mensajes.
        Args:
            conversation_id (str): ID de la conversación.
        Returns:
            Optional[Dict]: Diccionario con la respuesta del chatbot y el ID de la conversación.
            None si hay un error."""
        if conversation_id not in self.conversations:
            raise ValueError("ID de conversación no válido.")
        conversation = self.conversations[conversation_id]
        messages = conversation["messages"]
        response = self._api_request(messages)
        if response is None:
            return None
        chatbot_response = response["choices"][0]["message"]["content"]
        print(f" > [*] Respuesta del bot: {chatbot_response}")
        messages.append({"role": "assistant", "content": chatbot_response})
        conversation["messages"] = messages
        return {
            "conversation_id": conversation_id,
            "response": chatbot_response,
            "posture": conversation["posture"],
            "messages": messages }
    

    def _format_response(self, conversation_data: Dict) -> ChatResponse:
        """Formatea la respuesta del chatbot a la estructura ChatResponse.
        Args:
            conversation_data (Dict): Datos de la conversación.
        Returns:
            ChatResponse: Respuesta formateada."""
        conversation_id = conversation_data["conversation_id"]
        messages = conversation_data["messages"][1:]  # excluir system prompt
        recent_messages = messages[-5:]  # 5 últimos mensajes
        history = list()
        for m in recent_messages[::-1]:
            role = "bot" if m["role"] == "assistant" else m["role"]
            history.append(Message(role=role,
                                   content=m["content"]))
        return ChatResponse(
            conversation_id=conversation_id,
            message=history)


    def new_conversation(self, message: str) -> Optional[Dict]:
        """Inicia una nueva conversación, extrayendo la postura del mensaje inicial.
        Args:
            message (str): Mensaje inicial del usuario.
        Returns:
            Optional[Dict]: Diccionario con la respuesta del chatbot y el ID de la conversación.
            None si hay un error."""
        conversation_id = str(uuid4())
        posture = self._get_posture(message)
        if posture is None:
            return None
        self._init_conversation(conversation_id, posture, message)
        return self._gen_response(conversation_id)
    

    def continue_conversation(self,
                            conversation_id: str,
                            message: str) -> Optional[Dict]:
        """Continúa una conversación existente, con un nuevo mensaje del usuario.
        Args:
            conversation_id (str): ID de la conversación.
            message (str): Mensaje del usuario.
        Returns:
            Optional[Dict]: Diccionario con la respuesta del chatbot y el ID de la conversación.
            None si hay un error."""
        if conversation_id not in self.conversations:
            raise ValueError("ID de conversación no válido.")
        user_message = {"role": "user", "content": message}
        self.conversations[conversation_id]["messages"].append(user_message)
        return self._gen_response(conversation_id)
    

    # función principal para interfaz externa
    def chat(self,
             message: str,
             conversation_id: Optional[str] = None) -> Optional[Dict]:
        """Función principal para interactuar con el chatbot.
        Si no se proporciona conversation_id, se inicia una nueva conversación.
        Args:
            message (str): Mensaje del usuario.
            conversation_id (Optional[str]): ID de la conversación.
                Si es None, se inicia una nueva conversación.
        Returns:
            Optional[Dict]: Diccionario con la respuesta del chatbot y el ID de la conversación.
            None si hay un error."""
        if conversation_id is None:
            response = self.new_conversation(message)
        else:
            response = self.continue_conversation(conversation_id, message)
        if response is None:
            return None
        return self._format_response(response)
    

    def list_conversations(self) -> List[str]:
        """Lista los IDs de todas las conversaciones generadas.
        Returns:
            List[str]: Lista de IDs de conversaciones."""
        return list(self.conversations.keys())
    

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Obtiene el historial completo de una conversación dada su ID.
        Args:
            conversation_id (str): ID de la conversación.
        Returns:
            Optional[Dict]: Diccionario con el historial de la conversación.
            None si no existe la conversación."""
        return self.conversations.get(conversation_id, None)