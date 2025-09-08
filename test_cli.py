from chat_service import chat

def init():
    print("""
    =====Discutidor3000[DeepSeek Edition] Test Console=====
          
    En el primer mensaje, indica la postura que quieres que defienda el bot.
    Durante toda la conversación, el bot defenderá esta postura.
          
    github: @econopapi
    
    COMANDOS:
          - /n : iniciar nueva conversación"
          - /q : salir""")
    
    current_conversation_id = None

    while True:
        if current_conversation_id is None:
            user_input = input("Nueva conversación - Indica la postura a defender:\n> ").strip()
            
            # terminar programa
            if user_input.lower() == "/q":
                print("Adiós!")
                break

            try:
                response = chat(message=user_input)
                if response is None:
                    print(" > [!] Error en la conversación, inténtalo de nuevo.")
                    continue
                current_conversation_id = response["conversation_id"]
            except Exception as e:
                print(f" > [!] Error al iniciar la conversación: {e}")
                continue

        else:
            user_input = input(f"> Conversación {current_conversation_id[:7]} - Escribe tu mensaje:\n> ").strip()

            # terminar programa
            if user_input.lower() == "/q":
                print("Adiós!")
                break

            # iniciar nueva conversación
            if user_input.lower() == "/n":
                current_conversation_id = None
                continue

            try:
                response = chat(
                    message=user_input,
                    conversation_id=current_conversation_id)
                if response is None:
                    print(" > [!] Error en la conversación, inténtalo de nuevo.")
                    continue

                print(f"> Bot: {response['response']}")
            except Exception as e:
                print(f" > [!] Error en la conversación: {e}")
                current_conversation_id = None


if __name__ == "__main__":
    init()