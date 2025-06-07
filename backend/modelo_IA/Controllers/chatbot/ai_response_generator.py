import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env')

class AIResponseGenerator:
    def __init__(self):
        # Configurar la API de Google Generative AI
        genai.configure(api_key=os.getenv('API_KEY_G'))
        self.gen_model = genai.GenerativeModel("gemini-1.5-flash")
    
    def generate_response(self, prompt):
        try:
            response = self.gen_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
    def create_weather_prompt(self, city, days, weather_report, temp, humidity):
        return (
            f"Imagina que eres un experto meteorológico y genera una respuesta cálida, amigable y breve para un usuario "
            f"que consulta el clima en {city.capitalize()} para {days} días. Usa emojis y frases naturales. "
            f"El pronóstico es:\n{weather_report}\n"
            f"Genera una respuesta en español que mencione la temperatura de {temp}°C y la humedad de {humidity}%."
        )
    
    def generate_greeting(self):
        """Genera un saludo personalizado"""
        
        prompt = f"""
        Genera un saludo amigable y natural para un usuario que inicia conversación.
        Es en Colombia. Preséntate como asistente climatico.
        Usa emojis apropiados y mantén un tono cálido. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_farewell(self):
        """Genera una despedida personalizada"""
        prompt = """
        Genera una despedida amigable y profesional para un usuario que termina la conversación.
        Incluye buenos deseos, agradecimiento por usar el servicio e invitación a volver.
        Usa emojis apropiados. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_city_missing_response(self):
        """Genera respuesta cuando falta información de ciudad"""
        prompt = """
        El usuario quiere información pero no especificó la ciudad.
        Pide amigablemente que mencione el destino.
        Sugiere algunas ciudades populares de Colombia como ejemplos.
        Usa emojis y mantén tono entusiasta. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_days_missing_response(self, city):
        """Genera respuesta cuando faltan los días de estadía"""
        prompt = f"""
        El usuario pregunta sobre {city.capitalize()} pero no especificó cuántos días.
        Pide esta información de manera amigable.
        Explica brevemente por qué es útil saber la duración.
        Usa emojis apropiados. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_conversation_response(self, message, context=""):
        """Genera respuesta conversacional basada en el mensaje"""
        prompt = f"""
        El usuario dice: "{message}"
        Contexto previo: {context}
        
        Genera una respuesta natural y contextual.
        Si es pregunta, responde informativamente.
        Si es continuación de saludo, mantén el tono amigable.
        Si es comentario, mantén conversación fluida.
        Enfócate en clima cuando sea relevante.
        Usa emojis apropiados. Máximo 3 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_thanks_response(self):
        """Genera respuesta a agradecimientos"""
        prompt = """
        El usuario te está agradeciendo.
        Responde de manera humilde y amigable.
        Ofrece ayuda adicional si la necesita.
        Usa emojis cálidos. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_help_response(self):
        """Genera respuesta de ayuda"""
        prompt = """
        El usuario pide ayuda sobre qué puedes hacer.
        Explica que ayudas con información turística y meteorológica de Colombia.
        Menciona ejemplos de consultas que puede hacer.
        Usa emojis informativos. Máximo 3 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_identity_response(self):
        """Genera respuesta sobre identidad del bot"""
        prompt = """
        El usuario pregunta quién eres o qué eres.
        Explica que eres un asistente virtual especializado en turismo y clima de Colombia.
        Mantén tono amigable y profesional.
        Usa emojis apropiados. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_capabilities_response(self):
        """Genera respuesta sobre capacidades del bot"""
        prompt = """
        El usuario pregunta qué puedes hacer.
        Lista tus capacidades: información turística, pronósticos del clima, recomendaciones de destinos.
        Invita a hacer preguntas específicas.
        Usa emojis descriptivos. Máximo 3 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_affirmative_response(self, context=""):
        """Genera respuesta a afirmaciones del usuario"""
        prompt = f"""
        El usuario ha dado una respuesta afirmativa.
        Contexto: {context}
        
        Genera una respuesta positiva que continúe la conversación naturalmente.
        Mantén el flujo hacia información útil.
        Usa emojis positivos. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_negative_response(self, context=""):
        """Genera respuesta a negaciones del usuario"""
        prompt = f"""
        El usuario ha dado una respuesta negativa.
        Contexto: {context}
        
        Responde de manera comprensiva y ofrece alternativas.
        Mantén tono positivo y servicial.
        Usa emojis apropiados. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_contextual_response(self, user_message, conversation_history="", user_intent=""):
        """Método principal para respuestas contextuales avanzadas"""
        prompt = f"""
        Mensaje del usuario: "{user_message}"
        Historial: {conversation_history}
        Intención detectada: {user_intent}
        
        Genera una respuesta contextual apropiada.
        Mantén coherencia con la conversación previa.
        Si necesitas información específica, pídela naturalmente.
        Enfócate en turismo y clima de Colombia.
        Usa emojis apropiados. Máximo 3 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_error_response(self, error_type="general"):
        """Genera respuestas para diferentes tipos de errores"""
        error_prompts = {
            "general": "Genera una disculpa amigable por un error técnico general.",
            "weather_api": "Genera una disculpa por problemas al obtener información meteorológica.",
            "city_not_found": "Genera una respuesta cuando no se encuentra información de una ciudad.",
            "timeout": "Genera una disculpa por demora en la respuesta."
        }
        
        prompt = f"""
        {error_prompts.get(error_type, error_prompts["general"])}
        Ofrece intentar nuevamente y mantén tono positivo.
        Usa emojis apropiados. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_report_response(self):
        """Genera respuesta cuando el usuario solicita un reporte"""
        prompt = """
        El usuario ha solicitado un reporte de datos meteorológicos.
        Genera una respuesta amigable confirmando que se está generando el archivo Excel.
        Menciona que el archivo contiene datos históricos de predicciones meteorológicas.
        Usa emojis apropiados y mantén tono profesional. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)
    
    def generate_response_user_not_authenticated(self):
        """Genera respuesta cuando el usuario no está autenticado"""
        prompt = """
        El usuario no está autenticado y ha intentado acceder a una función restringida.
        Genera una respuesta amigable indicando que debe iniciar sesión o registrarse.
        Usa emojis apropiados y mantén un tono profesional. Máximo 2 líneas.
        """
        
        return self.generate_response(prompt)


