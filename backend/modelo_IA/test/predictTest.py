import unittest
import sys, os
from sqlalchemy.orm import Session

# aseguramos que routes esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from config.db import get_db
from routes.prediction_route import predict

class PredictTest(unittest.TestCase):

    
    def setUp(self):
        """Prepara una sesion de base de datos y datos de prueba"""
        self.db: Session = next(get_db())

    def test_PR_01(self):
        """PR-01: city y days válidos → 200 + 24 items"""
        response = predict(city="Manizales", days=2, db=self.db)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertIsInstance(response.json()[0], dict)

    def test_PR_02(self):
        """PR-02: days correcto y city vacio → 400"""
        response = predict(city="", days=2, db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['response'], "El nombre de la ciudad no puede estar vacío.")

    def test_PR_03(self):
        """PR-03: el campo de city correcto y days vacio → 400"""
        response = predict(city="Manizales", days="", db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['response'], "El número de días no puede estar vacio.")

    def test_PR_04(self):
        """PR-04: tanto city como days estan vacios → 400"""
        response = predict(city="", days="", db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['response'], "Verifica los parámetros de la solicitud.")

    def test_PR_05(self):
        """PR-05: city contiene caracteres alfanumericos y days es correcto → 400"""
        response = predict(city="Manizales123", days=2, db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['response'], "El nombre de la ciudad solo puede contener letras y espacios.")
    
    def test_PR_06(self):
        """PR-06: city contiene caracteres especiales y days es correcto → 400"""
        response = predict(city="Manizales@#$", days=2, db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['response'], "El nombre de la ciudad solo puede contener letras y espacios.")

    def test_PR_07(self):
        """PR-07: city correcto y days contiene caracteres especiales → 400"""
        response = predict(city="Manizales", days="2@#$", db=self.db)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['response'], "El valor de días debe ser un número entero.")
    
if __name__ == '__main__':
    unittest.main()
