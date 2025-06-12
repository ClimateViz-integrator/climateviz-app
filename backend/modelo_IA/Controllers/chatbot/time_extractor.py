import re
from datetime import datetime

class TimeExtractor:
    def __init__(self):
        self.maniana = "mañana"
        self.day_terms = {
            "hoy": 1, "el día de hoy": 1, "ahora": 1, "actual": 1,
            "mañana": 2, "el día siguiente": 2, "el día de mañana": 2,
            "pasado mañana": 3, "en dos dias": 3,
            "en tres dias": 3, "en 3 dias": 3,
            "en cuatro dias": 4, "en 4 dias": 4,
            "en cinco dias": 5, "en 5 dias": 5,
            "en seis dias": 6, "en 6 dias": 6,
            "en siete dias": 7, "en 7 dias": 7, "en una semana": 7,
            "próxima semana": 7, "semana que viene": 7
        }
    
    def extract_days(self, text):
        for term, days in self.day_terms.items():
            if term in text:
                return days
        
        patterns = [
            r'(\d+)\s*d[ií]as?',
            r'pr[oó]ximos?\s*(\d+)\s*d[ií]as?',
            r'siguientes?\s*(\d+)\s*d[ií]as?',
            r'(\d+)\s*d[ií]as?\s*siguientes?',
            r'en\s*(\d+)\s*d[ií]as?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except (IndexError, ValueError):
                    continue
        
        match = re.search(r'\b(\d+)\b', text)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 14:
                return num
        
        return 0  # Valor predeterminado: hoy
    
    def get_time_of_day(self):
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return self.maniana
        elif 12 <= hour < 18:
            return "tarde"
        elif 18 <= hour < 22:
            return "noche"
        else:
            return "madrugada"
    
    def get_day_text(self, days):
        if days == 1:
            return "hoy"
        elif days == 2:
            return self.maniana
        else:
            return f"los próximos {days} dias"
