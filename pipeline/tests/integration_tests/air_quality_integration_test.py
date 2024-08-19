import unittest
from unittest.mock import patch, MagicMock
from airflow.models import DagBag, TaskInstance
from airflow.utils.state import State
import uuid
import pendulum
from airflow.providers.postgres.hooks.postgres import PostgresHook


class TestETLAirQualityPipeline(unittest.TestCase):
    
    def setUp(self):
        # Load the DAGBag (Airflow DAGs)
        self.dagbag = DagBag()

    def test_dag_loaded(self):
        # Ensure the DAG is loaded correctly
        dag = self.dagbag.get_dag(dag_id='etl_air_quality_postgres_training_pipeline')
        self.assertIsNotNone(dag)
        # Ensure that all the expected tasks are present in the DAG
        task_ids = [task.task_id for task in dag.tasks]
        self.assertListEqual(
            task_ids,  # Sort task IDs for comparison
            ['create_tables', 'extract_to_postgres', 'transform', 'train']
        )
    
    
    def test_task_dependencies(self):
        # Check task dependencies
        dag = self.dagbag.get_dag(dag_id='etl_air_quality_postgres_training_pipeline')
        create_table_task = dag.get_task('create_tables')
        extract_task = dag.get_task('extract_to_postgres')
        transform_task = dag.get_task('transform')
        train_task = dag.get_task('train')
        
        self.assertEqual(create_table_task.downstream_list, [extract_task])
        self.assertEqual(extract_task.downstream_list, [transform_task])
        self.assertEqual(transform_task.downstream_list, [train_task])

if __name__ == '__main__':
    unittest.main()
