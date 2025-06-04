import unittest
import sys, os
from schemas.chatRequest import ChatRequest
from sqlalchemy.orm import Session

# aseguramos que routes esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config.db import get_db
from routes.prediction_route import chat_endpoint


class chatTest(unittest.TestCase):
    """Test de la ruta de predicción del clima"""

    def setUp(self):
        """Prepara una sesion de base de datos y datos de prueba"""
        self.db: Session = next(get_db())

    def test_CB_01(self):
        """CB-01: se le pasa al chatbot el message correcto → 200"""
        response = chat_endpoint(
            "¿Cómo será el clima para Manizales dentro de 2 días?", db=self.db
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertIn("response", response.json())

    def test_CB_02(self):
        """CB-02: en el message no se proporciona el nombre de la ciudad → 400"""
        response = chat_endpoint("¿Cómo será el clima dentro de 2 días?", db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["response"],
            "¿Para qué ciudad quieres saber el clima? No pude identificar la ciudad en tu mensaje.",
        )

    def test_CB_03(self):
        """CB-03: en el message no se proporciona el número de días → 400"""
        response = chat_endpoint("¿Cómo será el clima para Manizales?", db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["response"],
            "¿Cuántos días quieres saber el clima? No pude identificar los días en tu mensaje.",
        )

    def test_CB_04(self):
        """CB-04: en el message esta vacio → 400"""
        response = chat_endpoint("", db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["response"],
            "No entendí bien la pregunta. Por ejemplo, pregunta: '¿Cómo estará el clima en Madrid mañana?' o '¿Lloverá en Barcelona en los próximos 3 días?'",
        )

    def test_CB_05(self):
        """CB-05: el mensaje contiene caracteres especiales en el numero de dias → 400"""
        response = chat_endpoint(
            "¿Cómo será el clima para Manizales dentro de 2@ días?", db=self.db
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["response"],
            "No entendí bien la pregunta. Por ejemplo, pregunta: '¿Cómo estará el clima en Madrid mañana?' o '¿Lloverá en Barcelona en los próximos 3 días?'",
        )
