# Controllers/chatbot/weather_bot.py
import string
from Controllers.report.export_data import ReportController
from fastapi import HTTPException
from config.db import get_db
from Controllers.chatbot.city_extractor import CityExtractor
from Controllers.chatbot.time_extractor import TimeExtractor
from Controllers.chatbot.intent_detector import IntentDetector
from Controllers.chatbot.weather_data_processor import WeatherDataProcessor
from Controllers.chatbot.ai_response_generator import AIResponseGenerator
from Controllers.chatbot.context_manager import ContextManager


class WeatherBot:
    def __init__(self):
        self.city_extractor = CityExtractor()
        self.time_extractor = TimeExtractor()
        self.intent_detector = IntentDetector(self.city_extractor, self.time_extractor)
        self.weather_processor = WeatherDataProcessor()
        self.ai_generator = AIResponseGenerator()
        self.context_manager = ContextManager()

    async def process_message(self, context_id, message, controller, db, user_id=None):
        """
        Procesa el mensaje del usuario de forma modular.
        """
        # Preparación inicial
        original_message = message
        message_clean = self._clean_message(message)
        
        # Detectar y guardar intención
        intent = self._detect_and_store_intent(context_id, message_clean)
        
        # Extraer datos del mensaje
        city, days = self._extract_location_and_time(message_clean)
        
        self._log_processing_info(original_message,context_id, intent, city, days)
        
        # Procesar según la intención
        return await self._handle_intent(intent, context_id, city, days, controller, db, user_id, message_clean)

    def _clean_message(self, message):
        """Limpia y normaliza el mensaje."""
        message_lower = message.lower()
        return message_lower.translate(str.maketrans("", "", string.punctuation))

    def _detect_and_store_intent(self, context_id, message_clean):
        """Detecta la intención y la guarda en el contexto."""
        intent = self.intent_detector.detect_intent(message_clean)
        self.context_manager.get_from_context(context_id, "last_intent")
        self.context_manager.add_to_context(context_id, "last_intent", intent)
        return intent

    def _extract_location_and_time(self, message_clean):
        """Extrae ciudad y días del mensaje."""
        city = self.city_extractor.extract_city(message_clean)
        days = self.time_extractor.extract_days(message_clean)
        return city, days

    def _log_processing_info(self, original_message,context_id, intent, city, days):
        """Registra información de procesamiento."""
        last_intent = self.context_manager.get_from_context(context_id, "last_intent")
        print(f"Mensaje: '{original_message}'")
        print(f"Intent: {intent}, Last Intent: {last_intent}, Ciudad: {city}, Días: {days}")

    async def _handle_intent(self, intent, context_id, city, days, controller, db, user_id, message_clean):
        """Maneja la intención usando el patrón Strategy."""
        
        # Diccionario de estrategias para intenciones simples
        simple_intent_handlers = {
            "greeting": lambda: {"response": self.ai_generator.generate_greeting()},
            "farewell": lambda: self._handle_farewell(context_id),
            "thanks": lambda: {"response": self.ai_generator.generate_thanks_response()},
            "help": lambda: {"response": self.ai_generator.generate_help_response()},
            "conversation": lambda: {"response": self.ai_generator.generate_conversation_response(message_clean)},
            "bot_identity": lambda: {"response": self.ai_generator.generate_identity_response()},
            "capabilities": lambda: {"response": self.ai_generator.generate_capabilities_response()}
        }
        
        # Manejar intenciones simples
        if intent in simple_intent_handlers:
            return simple_intent_handlers[intent]()
        
        # Manejar intenciones complejas
        if intent == "report":
            return await self._handle_report_intent(user_id, db)
        
        if intent == "affirmative":
            return self._handle_affirmative_intent(context_id)
        
        if intent == "negative":
            return {"response": self.ai_generator.generate_negative_response()}
        
        if intent == "weather" or self.intent_detector.has_weather_intent(message_clean):
            return await self._handle_weather_intent(context_id, city, days, controller, db, user_id)
        
        # Manejar contexto previo o respuesta por defecto
        return self._handle_fallback_response(context_id)

    def _handle_farewell(self, context_id):
        """Maneja la intención de despedida."""
        self.context_manager.clear_context(context_id)
        return {"response": self.ai_generator.generate_farewell()}

    async def _handle_report_intent(self, user_id, db):
        """Maneja la generación de reportes."""
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail=self.ai_generator.generate_response_user_not_authenticated(),
            )
        
        try:
            report_controller = ReportController()
            report_file = report_controller.export_data_excel(db, user_id)
            response_text = self.ai_generator.generate_report_response()
            
            return {
                "response": response_text,
                "report": report_file,
                "download_available": True,
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error generando reporte: {str(e)}")
            return {
                "response": self.ai_generator.generate_error_response("general"),
                "download_available": False,
            }

    def _handle_affirmative_intent(self, context_id):
        """Maneja respuestas afirmativas según el contexto."""
        last_intent = self.context_manager.get_from_context(context_id, "last_intent")
        
        if last_intent in ["greeting", "capabilities", "help"]:
            return {"response": self.ai_generator.generate_affirmative_after_greeting()}
        
        city_in_context = self.context_manager.get_from_context(context_id, "city")
        if city_in_context and not self.context_manager.get_from_context(context_id, "days"):
            return {"response": self.ai_generator.generate_ask_days_response(city_in_context)}
        
        return {"response": self.ai_generator.generate_affirmative_response()}

    async def _handle_weather_intent(self, context_id, city, days, controller, db, user_id):
        """Maneja las consultas del clima."""
        # Validar y obtener ciudad
        city = self._validate_and_get_city(context_id, city)
        if isinstance(city, dict):  # Es una respuesta de error
            return city
        
        # Validar y obtener días
        days = self._validate_and_get_days(context_id, days, city)
        if isinstance(days, dict):  # Es una respuesta de error
            return days
        
        # Procesar predicción del clima
        return await self._process_weather_prediction(city, days, controller, db, user_id)

    def _validate_and_get_city(self, context_id, city):
        """Valida y obtiene la ciudad del contexto si es necesario."""
        if city is None:
            city = self.context_manager.get_from_context(context_id, "city")
            if city is None:
                return {"response": self.ai_generator.generate_city_missing_response()}
        else:
            self.context_manager.add_to_context(context_id, "city", city)
        return city

    def _validate_and_get_days(self, context_id, days, city):
        """Valida y obtiene los días del contexto si es necesario."""
        if days == 0:
            days = self.context_manager.get_from_context(context_id, "days")
            if days is None or days == 0:
                return {"response": self.ai_generator.generate_days_missing_response(city)}
        else:
            self.context_manager.add_to_context(context_id, "days", days)
        return days

    async def _process_weather_prediction(self, city, days, controller, db, user_id):
        """Procesa la predicción del clima y genera la respuesta."""
        try:
            prediction, _ = await controller.predict_from_api(city, days, db, user_id)
            
            weather_data = self._extract_and_process_weather_data(prediction)
            weather_report = self._generate_weather_report(city, days, weather_data)
            
            prompt = self.ai_generator.create_weather_prompt(
                city, days, weather_report, 
                weather_data["temp_c"], weather_data["humidity"]
            )
            
            response = self.ai_generator.generate_response(prompt)
            return {"response": response}
            
        except Exception as e:
            print(f"Error en process_message: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error obteniendo la predicción: {str(e)}"
            )

    def _extract_and_process_weather_data(self, prediction):
        """Extrae y procesa los datos del clima."""
        weather_data = self.weather_processor.extract_weather_data(prediction)
        
        if weather_data["condition"] == "No disponible":
            weather_data["condition"] = self.weather_processor.interpret_weather(
                weather_data["temp_c"], weather_data["humidity"]
            )
        
        return weather_data

    def _generate_weather_report(self, city, days, weather_data):
        """Genera el reporte textual del clima."""
        day_text = self.time_extractor.get_day_text(days)
        
        weather_report = (
            f"Para {day_text} en {city.capitalize()}, la temperatura será de {weather_data['temp_c']}°C "
            f"y la humedad es {weather_data['humidity']}%. "
        )
        
        if weather_data["condition"] != "No disponible":
            weather_report += f"Se espera un clima {weather_data['condition']}."
        else:
            weather_report += "."
        
        return weather_report

    def _handle_fallback_response(self, context_id):
        """Maneja respuestas de fallback basadas en el contexto."""
        context = self.context_manager.get_full_context(context_id)
        last_intent = self.context_manager.get_from_context(context_id, "last_intent")
        
        if last_intent in ["greeting", "conversation", "thanks", "capabilities", "help"]:
            return {"response": self.ai_generator.generate_after_greeting_response()}
        
        if "city" in context:
            return {
                "response": f"Parece que anteriormente hablamos sobre {context['city'].capitalize()}. "
                        f"¿Quieres saber cómo estará el clima allí? Puedes preguntarme específicamente."
            }
        
        return {
            "response": "No estoy seguro de entender tu pregunta. Puedo ayudarte con información del clima, "
                    "por ejemplo: '¿Cómo estará el clima en Madrid mañana?' o '¿Lloverá en Barcelona en los próximos 3 días?'"
        }
