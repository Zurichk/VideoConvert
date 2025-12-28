"""
Pruebas unitarias para el módulo de conversión.
"""

import unittest
from unittest.mock import patch, MagicMock
from app.src.converter import AEPMediaConverter

class TestAEPMediaConverter(unittest.TestCase):
    """
    Clase de pruebas para AEPMediaConverter.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.converter = AEPMediaConverter()

    @patch('app.src.converter.subprocess.run')
    def test_convert_file_success(self, mock_run):
        """
        Prueba una conversión exitosa.
        """
        # Configurar el mock para simular éxito (returncode 0)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = self.converter.convert_file(
            'input.mp4', 'output.mp3', 'mp3', compress=False
        )

        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch('app.src.converter.subprocess.run')
    def test_convert_file_failure(self, mock_run):
        """
        Prueba una conversión fallida.
        """
        # Configurar el mock para simular fallo (returncode 1)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error simulado"
        mock_run.return_value = mock_result

        result = self.converter.convert_file(
            'input.mp4', 'output.mp3', 'mp3', compress=False
        )

        self.assertFalse(result)
        mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
