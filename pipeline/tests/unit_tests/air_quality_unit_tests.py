import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from pipeline.dags.air_quality import create_tables, extract_data_to_postgres, transform

class TestETLPipeline(unittest.TestCase):
    """Unit tests for the Air Quality model."""
    @patch('pipeline.dags.air_quality.PostgresHook')
    def test_create_table_if_not_exists(self, mock_postgres_hook):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_postgres_hook.return_value.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        create_tables()

        mock_postgres_hook.assert_called_once_with(postgres_conn_id="postgres_air_quality")
        mock_cursor.execute.assert_called()  
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('pandas.read_csv')  # Corrected: Mocking pandas directly as it's imported
    @patch('pipeline.dags.air_quality.PostgresHook')
    def test_extract_data_to_postgres(self, mock_postgres_hook, mock_read_csv):
        mock_df = pd.DataFrame({
            'Date': ['10/03/2004'],
            'Time': ['18.00.00'],
            'CO_GT': [2.5],
            'PT08_S1_CO': [1500.0],
            'NMHC_GT': [150.0],
            'C6H6_GT': [9.5],
            'PT08_S2_NMHC': [1600.0],
            'NOx_GT': [200.0],
            'PT08_S3_NOx': [1200.0],
            'NO2_GT': [150.0],
            'PT08_S4_NO2': [1800.0],
            'PT08_S5_O3': [900.0],
            'T': [13.5],
            'RH': [48.9],
            'AH': [0.7567]
        })
        mock_read_csv.return_value = mock_df
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_postgres_hook.return_value.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        extract_data_to_postgres()

        mock_postgres_hook.assert_called_once_with(postgres_conn_id="postgres_air_quality")
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('pipeline.dags.air_quality.PostgresHook')
    def test_transform(self, mock_postgres_hook):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_postgres_hook.return_value.get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ('2004-03-10', '18:00:00', 2.5, 1500, 300, 9.5, 800, 300, 1000, 200, 1700, 1000, 25.0, 45.0, 0.8)
        ]
        mock_cursor.description = [('date',), ('time',), ('CO_GT',), ('PT08_S1_CO',), ('NMHC_GT',), ('C6H6_GT',),
                                   ('PT08_S2_NMHC',), ('NOx_GT',), ('PT08_S3_NOx',), ('NO2_GT',), ('PT08_S4_NO2',),
                                   ('PT08_S5_O3',), ('T',), ('RH',), ('AH',)]

        transform()

        mock_postgres_hook.assert_called_once_with(postgres_conn_id="postgres_air_quality")
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
