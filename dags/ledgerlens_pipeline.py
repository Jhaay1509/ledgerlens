from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

# Ingestion
from pipeline.ingestion.ingest_payments import ingest_payments_data
from pipeline.ingestion.ingest_orders import ingest_orders_data
from pipeline.ingestion.ingest_refunds import ingest_refund_data
from pipeline.ingestion.ingest_events import ingest_event_data

# Payment transformation
from pipeline.transformations.payments.normalise_payments import normalise_payment
from pipeline.transformations.payments.deduplicate_payments import deduplicate_payments
from pipeline.transformations.payments.load_canonical_payments import load_canonical_payments

# Order transformation
from pipeline.transformations.orders.normalise_orders import normalise_order
from pipeline.transformations.orders.deduplicate_orders import deduplicate_orders
from pipeline.transformations.orders.load_canonical_orders import load_canonical_orders

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
    normalise_payment_task = PythonOperator(
        task_id='normalise_payments',
        python_callable=normalise_payment
    )
    deduplicate_payment_task = PythonOperator(
        task_id='deduplicate_payments',
        python_callable=deduplicate_payments
    )
    load_payment_task = PythonOperator(
        task_id='load_canonical_payments',
        python_callable=load_canonical_payments
    )

    # ── Order transformation chain
    normalise_order_task = PythonOperator(
        task_id='normalise_orders',
        python_callable=normalise_order
    )
    deduplicate_order_task = PythonOperator(
        task_id='deduplicate_orders',
        python_callable=deduplicate_orders
    )
    load_order_task = PythonOperator(
        task_id='load_canonical_orders',
        python_callable=load_canonical_orders
    )

    # ── Reconciliation
    reconcile_task = PythonOperator(
        task_id='reconcile',
        python_callable=reconcile
    )

    # ── Refund application
    apply_refund_task = PythonOperator(
        task_id='apply_refunds',
        python_callable=apply_refunds
    )

    # ── Dependencies
    start >> [ingest_payment, ingest_order, ingest_refund, ingest_event]

    ingest_payment >> normalise_payment_task >> deduplicate_payment_task >> load_payment_task
    ingest_order   >> normalise_order_task   >> deduplicate_order_task   >> load_order_task

    [load_payment_task, load_order_task] >> reconcile_task

    [reconcile_task, ingest_refund] >> apply_refund_task

    [apply_refund_task, ingest_event] >> end