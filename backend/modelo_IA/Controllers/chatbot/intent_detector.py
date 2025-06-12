import re
import json
import spacy
from Controllers.chatbot.text_normalizer import TextNormalizer
from Utils.config import CONFIG
from Utils.read_file import readFile

class IntentDetector:
    def __init__(self, city_extractor, time_extractor):
        self.city_extractor = city_extractor
        self.time_extractor = time_extractor
        self.nlp = spacy.load("es_core_news_sm")
        
        # Cargar patrones desde el JSON
        path = CONFIG['RUTAS']['INTENT_PATTERNS']
        self.intent_patterns = readFile(path)

    def detect_intent(self, text):
        normalized_text = TextNormalizer.normalize_text(text.lower())
        
        # Detectar intención de reporte con prioridad alta
        if self._is_report_intent(normalized_text):
            return 'report'
        
        # Buscar en patrones de intenciones
        intent_match = self._check_intent_patterns(normalized_text)
        if intent_match:
            return intent_match
        
        # Verificar preguntas de conversación
        if self._is_conversation_question(normalized_text):
            return 'conversation'
        
        # Verificar respuestas afirmativas/negativas
        response_type = self._check_response_type(normalized_text)
        if response_type:
            return response_type
        
        # Verificar intención de clima
        if self._is_weather_intent(normalized_text, text):
            return 'weather'
        
        return 'unknown'
    
    def _check_intent_patterns(self, normalized_text):
        """Verifica patrones de intenciones específicas."""
        for intent, patterns in self.intent_patterns.items():
            if intent == 'report':  # Ya manejado anteriormente
                continue
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', normalized_text):
                    return intent
        return None

    def _is_conversation_question(self, normalized_text):
        """Detecta si es una pregunta de conversación."""
        conversation_questions = [
            r'cómo', r'qué', r'cuál', r'cuándo', r'dónde', r'por qué'
        ]
        
        words = normalized_text.split()
        if len(words) >= 5:
            return False
        
        return any(pattern in normalized_text for pattern in conversation_questions)

    def _check_response_type(self, normalized_text):
        """Verifica si es una respuesta afirmativa o negativa."""
        words = normalized_text.split()
        if not (1 <= len(words) <= 3):
            return None
        
        affirmative_words = ['si', 'sí', 'ok', 'vale', 'bueno', 'bien', 'claro', 'dale']
        negative_words = ['no', 'nope', 'nunca', 'jamas', 'jamás']
        
        for word in words:
            if word in affirmative_words:
                return 'affirmative'
            if word in negative_words:
                return 'negative'
        
        return None

    def _is_weather_intent(self, normalized_text, original_text):
        """Detecta si la intención está relacionada con el clima."""
        # Verificar ciudad
        if self.city_extractor.extract_city(normalized_text):
            return True
        
        # Verificar días
        if self.time_extractor.extract_days(normalized_text) > 0:
            return True
        
        # Verificar palabras relacionadas con clima
        return self._has_weather_keywords(original_text)

    def _has_weather_keywords(self, text):
        """Verifica si el texto contiene palabras clave del clima."""
        doc = self.nlp(text)
        weather_related_words = ['clima', 'tiempo', 'temperatura', 'lluvia']
        
        return any(token.lemma_ in weather_related_words for token in doc)

    
    def _is_report_intent(self, normalized_text):
        """
        Detecta específicamente si el usuario quiere generar un reporte
        """
        # Patrones específicos para reportes
        report_patterns = [
            r'\breporte\b',
            r'\breportar\b', 
            r'\breport\b',
            r'\bexcel\b',
            r'\bdescargar\b',
            r'\bexportar\b',
            r'\barchivo\b',
            r'generar.*reporte',
            r'crear.*reporte',
            r'datos.*excel',
            r'archivo.*excel',
            r'descarga.*datos',
            r'exportar.*datos',
            r'quiero.*reporte',
            r'necesito.*reporte',
            r'dame.*reporte',
            r'enviar.*reporte',
            r'mostrar.*reporte'
        ]
        
        for pattern in report_patterns:
            if re.search(pattern, normalized_text):
                return True
        
        # Detectar combinaciones de palabras que indican reporte
        words = normalized_text.split()
        report_indicators = ['reporte', 'reportar', 'excel', 'descargar', 'exportar', 'archivo']
        action_words = ['generar', 'crear', 'hacer', 'dame', 'quiero', 'necesito', 'enviar', 'mostrar']
        
        # Si hay una palabra indicadora de reporte y una palabra de acción
        has_report_word = any(word in words for word in report_indicators)
        has_action_word = any(word in words for word in action_words)
        
        if has_report_word and (has_action_word or len(words) <= 3):
            return True
            
        return False

    def has_weather_intent(self, text):
        return self.detect_intent(text) == 'weather'

    def detect_topic_change(self, current_intent, last_intent):
        if not last_intent:
            return False
        if last_intent != current_intent:
            if current_intent not in ['affirmative', 'negative', 'unknown']:
                return True
        return False
