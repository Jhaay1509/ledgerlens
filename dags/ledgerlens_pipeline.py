from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

# Ingestion
from pipeline.ingestion.ingest_payments import ingest_payments_data
from pipeline.ingestion.ingest_orders import ingest_orders_data
from pipeline.ingestion.ingest_refunds import ingest_refund_data
from pipeline.ingestion.ingest_events import ingest_event_data

# Transformation
from pipeline.transformations.run_pipelines import (
    run_payment_pipeline, run_order_pipeline,
    run_reconciliation, run_apply_refunds
)
# Reconciliation and refunds
from pipeline.transformations.reconciliation.reconcile import reconcile
from pipeline.transformations.refunds.apply_refunds import apply_refunds

default_args = {
    'owner': 'ledgerlens',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='ledgerlens_revenue_pipeline',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    description='Daily revenue pipeline — ingest, normalise, reconcile, apply refunds'
) as dag:

    # ── Anchors
    start = EmptyOperator(task_id='start')
    end   = EmptyOperator(task_id='end')

    # ── Ingestion
    ingest_payment = PythonOperator(
        task_id='ingest_payments',
        python_callable=ingest_payments_data
    )
    ingest_order = PythonOperator(
        task_id='ingest_orders',
        python_callable=ingest_orders_data
    )
    ingest_refund = PythonOperator(
        task_id='ingest_refunds',
        python_callable=ingest_refund_data
    )
    ingest_event = PythonOperator(
        task_id='ingest_events',
        python_callable=ingest_event_data
    )

    # ── Payment transformation chain
    payment_pipeline_task = PythonOperator(
    task_id='payment_pipeline',
    python_callable=run_payment_pipeline
)

    # ── Order transformation chain
    order_pipeline_task = PythonOperator(
    task_id='order_pipeline',
    python_callable=run_order_pipeline
)

    # ── Reconciliation
    reconcile_task = PythonOperator(
        task_id='reconcile',
        python_callable=run_reconciliation
    )

    # ── Refund application
    apply_refund_task = PythonOperator(
        task_id='apply_refunds',
        python_callable= run_apply_refunds
    )

    # ── Dependencies
    start >> [ingest_payment, ingest_order, ingest_refund, ingest_event]

    ingest_payment >> payment_pipeline_task
    ingest_order   >> order_pipeline_task

    [payment_pipeline_task, order_pipeline_task] >> reconcile_task

    [reconcile_task, ingest_refund] >> apply_refund_task

    [apply_refund_task, ingest_event] >> end