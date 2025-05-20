# Controllers/chatbot/response_generator.py
import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from Utils.config import CONFIG
from Utils.read_file import readFile

class ResponseGenerator:
    def __init__(self):
        # Plantillas para diferentes tipos de respuestas
        path = CONFIG['RUTAS']['RESPONSES']
        data = readFile(path)

        self.greeting_templates = data["greeting_templates"]
        self.farewell_templates = data["farewell_templates"]
        self.city_missing_templates = data["city_missing_templates"]
        self.days_missing_templates = data["days_missing_templates"]
        self.conversation_templates = data["conversation_templates"]
        self.thanks_templates = data["thanks_templates"]
        self.help_templates = data["help_templates"]
        self.identity_templates = data["identity_templates"]
        self.capabilities_templates = data["capabilities_templates"]
        self.affirmative_after_greeting_templates = data["affirmative_after_greeting_templates"]
        self.ask_days_templates = data["ask_days_templates"]
        self.generic_affirmative_templates = data["generic_affirmative_templates"]
        self.negative_templates = data["negative_templates"]
        self.after_greeting_templates = data["after_greeting_templates"]
    
    def generate_greeting(self):
        """Genera un saludo aleatorio"""
        colombia_time = datetime.now(ZoneInfo("America/Bogota"))
        current_hour = colombia_time.hour
        
        if 5 <= current_hour < 12:
            time_prefix = "¡Buenos días!"
        elif 12 <= current_hour < 18:
            time_prefix = "¡Buenas tardes!"
        else:
            time_prefix = "¡Buenas noches!"
        
        template = random.choice(self.greeting_templates)
        return f"{time_prefix} {template}"
    
    def generate_farewell(self):
        """Genera una despedida aleatoria"""
        return random.choice(self.farewell_templates)
    
    def generate_city_missing_response(self):
        """Genera una respuesta cuando falta la ciudad"""
        return random.choice(self.city_missing_templates)
    
    def generate_days_missing_response(self, city):
        """Genera una respuesta cuando faltan los días"""
        template = random.choice(self.days_missing_templates)
        return template.format(city=city.capitalize())
    
    def generate_conversation_response(self, message):
        """Genera una respuesta conversacional basada en el mensaje"""
        # Buscar en las plantillas específicas
        for key, templates in self.conversation_templates.items():
            if key in message:
                return random.choice(templates)
        
        # Si no hay coincidencia específica, usar la plantilla por defecto
        return random.choice(self.conversation_templates["default"])
    
    def generate_thanks_response(self):
        """Genera una respuesta a un agradecimiento"""
        return random.choice(self.thanks_templates)
    
    def generate_help_response(self):
        """Genera una respuesta de ayuda"""
        return random.choice(self.help_templates)
    
    def generate_identity_response(self):
        """Genera una respuesta sobre la identidad del bot"""
        return random.choice(self.identity_templates)
    
    def generate_capabilities_response(self):
        """Genera una respuesta sobre las capacidades del bot"""
        return random.choice(self.capabilities_templates)
    
    def generate_affirmative_after_greeting(self):
        """Genera una respuesta después de una afirmación tras un saludo"""
        return random.choice(self.affirmative_after_greeting_templates)
    
    def generate_ask_days_response(self, city):
        """Genera una respuesta para pedir los días después de tener la ciudad"""
        template = random.choice(self.ask_days_templates)
        return template.format(city=city.capitalize())
    
    def generate_generic_affirmative_response(self):
        """Genera una respuesta genérica a una afirmación"""
        return random.choice(self.generic_affirmative_templates)
    
    def generate_negative_response(self):
        """Genera una respuesta a una negación"""
        return random.choice(self.negative_templates)
    
    def generate_after_greeting_response(self):
        """Genera una respuesta después de un saludo o conversación"""
        return random.choice(self.after_greeting_templates)
