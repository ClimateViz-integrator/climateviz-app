# Controllers/chatbot/weather_bot.py
import string
from fastapi import HTTPException
from config.db import get_db
from Controllers.chatbot.city_extractor import CityExtractor
from Controllers.chatbot.time_extractor import TimeExtractor
from Controllers.chatbot.intent_detector import IntentDetector
from Controllers.chatbot.weather_data_processor import WeatherDataProcessor
from Controllers.chatbot.ai_response_generator import AIResponseGenerator
from Controllers.chatbot.context_manager import ContextManager
from Controllers.chatbot.response_generator import ResponseGenerator

class WeatherBot:
    def __init__(self):
        self.city_extractor = CityExtractor()
        self.time_extractor = TimeExtractor()
        self.intent_detector = IntentDetector(self.city_extractor, self.time_extractor)
        self.weather_processor = WeatherDataProcessor()
        self.ai_generator = AIResponseGenerator()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator()
    
    async def process_message(self, context_id, message, controller):
        """
        Procesa el mensaje del usuario:
         - Extrae ciudad y días.
         - Llama al modelo para obtener la predicción.
         - Extrae datos del pronóstico recién generado.
         - Genera una respuesta usando Generative AI.
        """
        original_message = message
        message_lower = message.lower()
        message_clean = message_lower.translate(str.maketrans("", "", string.punctuation))
        
        # Detectar la intención del mensaje
        intent = self.intent_detector.detect_intent(message_clean)
        
        # Obtener la última intención del contexto
        last_intent = self.context_manager.get_from_context(context_id, 'last_intent')
        
        # Guardar la intención actual en el contexto
        self.context_manager.add_to_context(context_id, 'last_intent', intent)
        
        # Extraer ciudad y días
        city = self.city_extractor.extract_city(message_clean)
        days = self.time_extractor.extract_days(message_clean)
        
        print(f"Mensaje: '{original_message}'")
        print(f"Intent: {intent}, Last Intent: {last_intent}, Ciudad: {city}, Días: {days}")
        
        # Manejar diferentes intenciones
        if intent == 'greeting':
            return {"response": self.response_generator.generate_greeting()}
        
        elif intent == 'farewell':
            self.context_manager.clear_context(context_id)
            return {"response": self.response_generator.generate_farewell()}
        
        elif intent == 'thanks':
            return {"response": self.response_generator.generate_thanks_response()}
        
        elif intent == 'help':
            return {"response": self.response_generator.generate_help_response()}
        
        elif intent == 'conversation':
            return {"response": self.response_generator.generate_conversation_response(message_clean)}
        
        elif intent == 'bot_identity':
            return {"response": self.response_generator.generate_identity_response()}
        
        elif intent == 'capabilities':
            return {"response": self.response_generator.generate_capabilities_response()}
        
        # Manejar respuestas afirmativas según el contexto previo
        elif intent == 'affirmative':
            # Si la última intención fue un saludo o una pregunta sobre capacidades,
            # el usuario probablemente quiere información del clima
            if last_intent in ['greeting', 'capabilities', 'help']:
                return {"response": self.response_generator.generate_affirmative_after_greeting()}
            
            # Si ya teníamos una ciudad en el contexto pero faltaban los días
            city_in_context = self.context_manager.get_from_context(context_id, 'city')
            if city_in_context and not self.context_manager.get_from_context(context_id, 'days'):
                return {"response": self.response_generator.generate_ask_days_response(city_in_context)}
            
            # Respuesta genérica afirmativa
            return {"response": self.response_generator.generate_generic_affirmative_response()}
        
        # Manejar respuestas negativas
        elif intent == 'negative':
            return {"response": self.response_generator.generate_negative_response()}
        
        elif intent == 'weather' or self.intent_detector.has_weather_intent(message_clean):
            # Si no se detectó ciudad, buscar en el contexto
            if city is None:
                city = self.context_manager.get_from_context(context_id, 'city')
                if city is None:
                    return {"response": self.response_generator.generate_city_missing_response()}
            else:
                self.context_manager.add_to_context(context_id, 'city', city)
            
            # Si no se detectaron días, buscar en el contexto
            if days == 0:
                days = self.context_manager.get_from_context(context_id, 'days')
                if days is None or days == 0:
                    return {"response": self.response_generator.generate_days_missing_response(city)}
            else:
                self.context_manager.add_to_context(context_id, 'days', days)
            
            # Si todo está bien, proceder con la predicción
            try:
                db = next(get_db())
                prediction, _ = await controller.predict_from_api(city, days, db)
                
                weather_data = self.weather_processor.extract_weather_data(prediction)
                if weather_data['condition'] == 'No disponible':
                    weather_data['condition'] = self.weather_processor.interpret_weather(
                        weather_data['temp_c'], 
                        weather_data['humidity']
                    )
                
                day_text = self.time_extractor.get_day_text(days)

                weather_report = (
                    f"Para {day_text} en {city.capitalize()}, la temperatura será de {weather_data['temp_c']}°C "
                    f"y la humedad es {weather_data['humidity']}%. "
                )
                if weather_data['condition'] != 'No disponible':
                    weather_report += f"Se espera un clima {weather_data['condition']}."
                else:
                    weather_report += "."

                db.close()
                time_of_day = self.time_extractor.get_time_of_day()
                
                prompt = self.ai_generator.create_weather_prompt(
                    city, days, weather_report, time_of_day, 
                    weather_data['temp_c'], weather_data['humidity']
                )
                
                response = self.ai_generator.generate_response(prompt)
                return {"response": response}
            except Exception as e:
                print(f"Error en process_message: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error obteniendo la predicción: {str(e)}")
        
        # Si hay contexto previo, intentar responder con él
        context = self.context_manager.get_full_context(context_id)
        
        # Si la última intención fue conversacional o un saludo, seguir la conversación
        if last_intent in ['greeting', 'conversation', 'thanks', 'capabilities', 'help']:
            return {"response": self.response_generator.generate_after_greeting_response()}
        
        # Si hay una ciudad en el contexto, sugerir consultar el clima
        if 'city' in context:
            return {"response": f"Parece que anteriormente hablamos sobre {context['city'].capitalize()}. ¿Quieres saber cómo estará el clima allí? Puedes preguntarme específicamente."}

        # No hay intención reconocida ni contexto previo útil
        return {"response": "No estoy seguro de entender tu pregunta. Puedo ayudarte con información del clima, por ejemplo: '¿Cómo estará el clima en Madrid mañana?' o '¿Lloverá en Barcelona en los próximos 3 días?'"}
