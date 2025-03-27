from airflow import DAG
from airflow.providers.google.cloud.transfers.s3_to_gcs import S3ToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from datetime import datetime
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.slack.operators.slack_api import SlackAPIPostOperator

# Define the DAG
dag = DAG(
    'etl_proj1',  
    schedule_interval='@daily',  
    start_date=datetime(2023, 3, 15),
    catchup=False,  
)

# Ingest data from S3 to GCS
s3_to_gcs = S3ToGCSOperator(
    task_id='s3_to_gcs',
    bucket='product-usage-data',  
    aws_conn_id='etl_proj1_aws',  
    dest_gcs='gs://minsoggy_etl_bucket/',  
    gcp_conn_id='etl_proj1_gcs',  
    prefix='product_usage_data.csv',  
    dag=dag,  
)

# Upload data from GCS to BigQuery
gcs_to_bq = GCSToBigQueryOperator(
    task_id='gcs_to_bq',
    bucket='minsoggy_etl_bucket',  
    source_objects=['product_usage_data.csv'],  
    destination_project_dataset_table='ryans-etl-project.etl_proj1_product_usage.etl_proj1_product_usage_table',  
    write_disposition='WRITE_TRUNCATE',  
    skip_leading_rows=1,  
    field_delimiter=',',  
    autodetect=True,  
    dag=dag,
)

# Data validation task (Staging)
validate_cleaned_data = BigQueryCheckOperator(
    task_id="validate_cleaned_data",
    sql="""
        -- Ensure no duplicate events exist
        SELECT COUNT(*) 
            FROM (
            SELECT 
                user_id, 
                DATE_TRUNC(usage_start_time, MONTH) AS start_time,
                event_type, 
                COUNT(*) as cnt
            FROM ryans-etl-project.etl_proj1_product_usage.etl_proj1_product_usage_table  
            GROUP BY 1, 2, 3
            HAVING COUNT(*) > 1
        ) 
    """,
    use_legacy_sql=False,
    gcp_conn_id="etl_proj1_gcs",
    dag=dag,
)

# Ensuring valid event types
validate_event_types = BigQueryCheckOperator(
    task_id="validate_event_types",
    sql="""
        -- Ensure event_type only contains expected values
        SELECT COUNT(*) 
        FROM etl_proj1_product_usage.cleaned_data
        WHERE event_type NOT IN ('click', 'purchase', 'view', 'unknown')
    """,
    use_legacy_sql=False,
    gcp_conn_id="etl_proj1_gcs",
    dag=dag,
)

# Ensuring session_duration is valid (Can't be negative)
validate_session_duration = BigQueryCheckOperator(
    task_id="validate_session_duration",
    sql="""
        -- Ensure no negative session durations exist
        SELECT COUNT(*) 
        FROM etl_proj1_product_usage.cleaned_data
        WHERE session_duration < 0
    """,
    use_legacy_sql=False,
    gcp_conn_id="etl_proj1_gcs",
    dag=dag,
)

# Data cleaning step
clean_data = BigQueryInsertJobOperator(
    task_id="clean_data",
    configuration={
        "query": {
            "query": """ 
                CREATE OR REPLACE TABLE etl_proj1_product_usage.cleaned_data AS
                WITH deduplicated AS (
                    SELECT 
                        *, 
                        ROW_NUMBER() OVER (PARTITION BY user_id, event_time, event_type ORDER BY event_time DESC) AS row_num
                    FROM etl_proj1_product_usage.raw_data
                )
                SELECT 
                    user_id, 
                    COALESCE(NULLIF(LOWER(event_type), ''), 'unknown') AS event_type,
                    SAFE_CAST(event_time AS TIMESTAMP) AS event_time,
                    CASE 
                        WHEN session_duration < 0 THEN NULL 
                        ELSE session_duration 
                    END AS session_duration
                FROM deduplicated
                WHERE row_num = 1
                AND event_type IN ('click', 'purchase', 'view');
            """,
            "useLegacySql": False,
        }
    },
    gcp_conn_id="etl_proj1_gcs",
    dag=dag,
)

# Quarantine bad event types instead of failing
log_invalid_events = BigQueryInsertJobOperator(
    task_id="log_invalid_events",
    configuration={
        "query": {
            "query": """
                CREATE OR REPLACE TABLE etl_proj1_product_usage.quarantine_table AS
                SELECT * FROM etl_proj1_product_usage.cleaned_data
                WHERE event_type NOT IN ('click', 'purchase', 'view');
            """,
            "useLegacySql": False,
        }
    },
    gcp_conn_id="etl_proj1_gcs",
    dag=dag,
)

# Send Slack alert for validation issues
slack_alert = SlackAPIPostOperator(
    task_id="slack_alert",
    token="YOUR_SLACK_TOKEN",
    channel="#data-pipeline-alerts",
    text="Validation issue detected in ETL pipeline. Check quarantine table for invalid event types.",
    dag=dag,
)

# Task dependencies
s3_to_gcs >> gcs_to_bq 
validate_cleaned_data >> validate_event_types >> validate_session_duration
validate_session_duration >> log_invalid_events

