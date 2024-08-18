from utils.db_utils import execute_sql

def create_tables_if_not_exists():
    create_tables_query = """
    DROP TABLE IF EXISTS air_quality_data;
    CREATE TABLE air_quality_data (
        date DATE,
        time TIME,
        CO_GT FLOAT,
        PT08_S1_CO FLOAT,
        NMHC_GT FLOAT,
        C6H6_GT FLOAT,
        PT08_S2_NMHC FLOAT,
        NOx_GT FLOAT,
        PT08_S3_NOx FLOAT,
        NO2_GT FLOAT,
        PT08_S4_NO2 FLOAT,
        PT08_S5_O3 FLOAT,
        T FLOAT,
        RH FLOAT,
        AH FLOAT
    );
    DROP TABLE IF EXISTS air_quality_data_transformed;
    CREATE TABLE air_quality_data_transformed (
        timestamp BIGINT,
        CO_GT FLOAT,
        PT08_S1_CO FLOAT,
        NMHC_GT FLOAT,
        C6H6_GT FLOAT,
        PT08_S2_NMHC FLOAT,
        NOx_GT FLOAT,
        PT08_S3_NOx FLOAT,
        NO2_GT FLOAT,
        PT08_S4_NO2 FLOAT,
        PT08_S5_O3 FLOAT,
        T FLOAT,
        RH FLOAT,
        AH FLOAT
    );               
    """
    execute_sql(create_tables_query)