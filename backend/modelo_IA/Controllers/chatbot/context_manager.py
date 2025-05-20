# Controllers/chatbot/context_manager.py
from datetime import datetime, timedelta

class ContextManager:
    def __init__(self, expiration_time=30):
        # Diccionario para almacenar el contexto
        self.contexts = {}
        # Tiempo en minutos antes de que expire un contexto
        self.expiration_time = expiration_time
    
    def add_to_context(self, context_id, key, value):
        """Agrega información al contexto"""
        if context_id not in self.contexts:
            self.contexts[context_id] = {
                'last_updated': datetime.now(),
                'data': {}
            }
        
        self.contexts[context_id]['data'][key] = value
        self.contexts[context_id]['last_updated'] = datetime.now()
    
    def get_from_context(self, context_id, key, default=None):
        """Obtiene información del contexto"""
        self._clean_expired_contexts()
        
        if context_id in self.contexts and key in self.contexts[context_id]['data']:
            self.contexts[context_id]['last_updated'] = datetime.now()
            return self.contexts[context_id]['data'][key]
        return default
    
    def get_full_context(self, context_id):
        """Obtiene todo el contexto"""
        self._clean_expired_contexts()
        
        if context_id in self.contexts:
            self.contexts[context_id]['last_updated'] = datetime.now()
            return self.contexts[context_id]['data']
        return {}
    
    def clear_context(self, context_id):
        """Limpia el contexto específico"""
        if context_id in self.contexts:
            del self.contexts[context_id]
    
    def _clean_expired_contexts(self):
        """Elimina contextos expirados"""
        current_time = datetime.now()
        expired_contexts = []
        
        for context_id, context in self.contexts.items():
            expiration = context['last_updated'] + timedelta(minutes=self.expiration_time)
            if current_time > expiration:
                expired_contexts.append(context_id)
        
        for context_id in expired_contexts:
            del self.contexts[context_id]
