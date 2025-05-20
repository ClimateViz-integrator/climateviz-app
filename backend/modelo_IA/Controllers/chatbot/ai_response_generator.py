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
    
    def create_weather_prompt(self, city, days, weather_report, time_of_day, temp, humidity):
        return (
            f"Imagina que eres un experto meteorológico y genera una respuesta cálida, amigable y breve para un usuario "
            f"que consulta el clima en {city.capitalize()} para {days} días. Es actualmente {time_of_day}. Usa emojis y frases naturales. "
            f"El pronóstico es:\n{weather_report}\n"
            f"Genera una respuesta en español que mencione la temperatura de {temp}°C y la humedad de {humidity}%."
        )
