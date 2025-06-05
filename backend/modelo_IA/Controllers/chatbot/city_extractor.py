import csv
from pathlib import Path
import spacy
from spacy.matcher import PhraseMatcher
from Controllers.chatbot.text_normalizer import TextNormalizer

class CityExtractor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.cities_file = (self.base_dir / "../../Data/cities.txt").resolve()
        self.nlp = spacy.load("es_core_news_sm")
        self.cities = self._load_cities()
        self.matcher = self._setup_phrase_matcher()
    
    def _load_cities(self):
        cities = set()
        try:
            with open(self.cities_file, "r", encoding="utf-8-sig") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)  # Saltar encabezado
                for row in reader:
                    if len(row) >= 2:
                        city_name = TextNormalizer.normalize_text(row[1].strip())
                        cities.add(city_name)
        except Exception as e:
            print(f"Error loading cities: {e}")
        return cities
    
    def _setup_phrase_matcher(self):
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp(city) for city in self.cities]
        matcher.add("CITIES", patterns)
        return matcher
    
    def extract_city(self, text):
        normalized_text = TextNormalizer.normalize_text(text)
        doc = self.nlp(text)
        matches = self.matcher(doc)

        if matches:
            matches.sort(key=lambda x: len(doc[x[1]:x[2]]), reverse=True)
            match_id, start, end = matches[0]
            matched_city = doc[start:end].text.lower()
            if matched_city in self.cities:
                return matched_city

        return None  # No se detectó ciudad explícita
