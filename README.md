LedgerLens Revenue Truth System (LRTS)
A production-quality, end-to-end fintech data pipeline that establishes a single, auditable source of truth for payment revenue. Built as a portfolio project demonstrating real-world data engineering patterns across ingestion, transformation, reconciliation, orchestration, and analytical modelling.

The Problem
LedgerLens operates a subscription and marketplace business across multiple countries and payment providers. Without a unified data system:

Finance and Growth teams reported conflicting revenue numbers
"Revenue" meant different things to different teams
No single auditable source of truth existed for payments, orders, or refunds
Late-arriving refunds and chargebacks made historical figures unreliable


The Solution
LRTS implements a multi-layer data pipeline that:

Ingests raw payment, order, refund, and event data from multiple sources
Normalises inconsistent formats across payment providers (Stripe, PayPal, FastPay)
Deduplicates retries and duplicate webhook events
Reconciles payments to orders using a deterministic-first, fuzzy-fallback priority ladder with confidence scoring
Applies late-arriving refunds and chargebacks with full audit trail
Loads clean canonical data into BigQuery for analytical reporting


Architecture
Raw Sources                  Operational Layer            Analytical Layer
───────────                  ─────────────────            ────────────────
raw_payments.csv   ──┐
raw_orders.json    ──┤──► PostgreSQL ──────────────────► BigQuery
raw_refunds.csv    ──┤    ├── stg_payments               ├── dim_date
raw_events.json    ──┘    ├── stg_orders                 ├── dim_product (SCD2)
                          ├── stg_refunds                ├── dim_country
                          ├── stg_events                 ├── dim_attribution
                          ├── canonical_payments         ├── fact_payments
                          ├── canonical_orders           ├── fact_orders
                          ├── refund_events              └── daily_revenue
                          └── reconciliation_log

Orchestration: Apache Airflow (Docker)

Tech Stack
LayerTechnologyOperational databasePostgreSQL 16Analytical warehouseGoogle BigQueryTransformation logicPython 3.11OrchestrationApache Airflow 3.xContainerisationDocker + Docker ComposeData generationPython (Faker)

Key Engineering Decisions
Dual-Layer Architecture
PostgreSQL serves as the operational layer for row-level processing, foreign key enforcement, and reconciliation logic. BigQuery serves as the analytical layer for fast aggregations and reporting. Each tool is used for what it does best.
Star Schema in BigQuery
A star schema was chosen over snowflake for the analytical layer — simpler queries, faster analytical performance, and easier maintenance at this scale.
Type 2 SCD on dim_product
Product prices change over time. dim_product preserves historical versions using valid_from, valid_to, and is_current columns, ensuring revenue reports reflect prices at the time of purchase rather than current prices.
Reconciliation Priority Ladder
Payments are matched to orders using a four-rule priority system:

Direct ID match — payment_reference = payment_id (confidence: 1.0)
Order ID match — payment.order_id = order.order_id (confidence: 1.0)
Amount + time window — same amount within 5 minutes (confidence: 0.8)
Unmatched — flagged as orphan for manual review

Every match attempt is logged to reconciliation_log as an immutable audit trail.
Idempotent Pipeline
All pipeline runs are idempotent — staging tables are truncated before each load and canonical tables use ON CONFLICT DO NOTHING. Running the pipeline multiple times produces identical results.
Orphan Payment Treatment
Payments with no matching order are excluded from revenue. Revenue requires proof of a real purchase — an unmatched payment could be a duplicate, test transaction, or processing error.

Project Structure
ledgerlens/
├── dags/
│   └── ledgerlens_pipeline.py      # Airflow DAG definition
├── data/
│   └── raw/                        # Generated synthetic source data
├── pipeline/
│   ├── ingestion/                  # Raw data → staging tables
│   ├── transformations/
│   │   ├── payments/               # Normalise, deduplicate, load payments
│   │   ├── orders/                 # Normalise, deduplicate, load orders
│   │   ├── reconciliation/         # Match payments to orders
│   │   └── refunds/                # Apply refunds to canonical payments
│   └── loaders/                    # Canonical → BigQuery dimensional tables
├── sql/
│   ├── postgres/                   # Operational schema definitions
│   └── bigquery/                   # Dimensional schema definitions
├── scripts/
│   ├── generate_data.py            # Synthetic data generation
│   ├── setup_bigquery.py           # BigQuery dataset setup
│   └── create_bigquery_tables.py   # BigQuery table creation
├── credentials/                    # GCP service account (gitignored)
├── docker-compose.yaml             # Airflow Docker setup
├── requirements.txt
└── .env                            # Environment variables (gitignored)

Running the Pipeline
Prerequisites

Docker and Docker Compose
Google Cloud project with BigQuery API enabled
GCP service account JSON key with BigQuery Admin role

Setup
bash# Clone the repository
git clone https://github.com/YOUR_USERNAME/ledgerlens.git
cd ledgerlens

# Copy environment template and fill in values
cp .env.example .env

# Place GCP service account key
mkdir credentials
cp /path/to/your/key.json credentials/service_account.json

# Generate synthetic data
python3 scripts/generate_data.py

# Set up BigQuery
python3 scripts/setup_bigquery.py
python3 scripts/create_bigquery_tables.py

# Start Airflow
docker compose up airflow-init
docker compose up -d
Trigger the Pipeline
Open http://localhost:8080, log in with admin/admin, and trigger ledgerlens_revenue_pipeline.
DAG Structure
start
  ├── ingest_payments
  ├── ingest_orders
  ├── ingest_refunds
  └── ingest_events
        ├── payment_pipeline (normalise → deduplicate → load)
        └── order_pipeline   (normalise → deduplicate → load)
                └── reconcile
                      └── apply_refunds
                            └── end

Data Model
PostgreSQL — Operational Layer
TablePurposestg_paymentsRaw payments exactly as receivedstg_ordersRaw orders exactly as receivedstg_refundsRaw refunds exactly as receivedstg_eventsRaw attribution events exactly as receivedcanonical_paymentsCleaned, deduplicated, reconciled paymentscanonical_ordersOrders enriched with payment outcomerefund_eventsIndividual refund and chargeback recordsreconciliation_logImmutable audit trail of every match attempt
BigQuery — Analytical Layer (Star Schema)
TableTypePurposedim_dateDimensionPre-generated calendar (2020–2030)dim_productDimension (SCD2)Product catalogue with price historydim_countryDimensionGeographic referencedim_attributionDimensionMarketing channel and UTM datafact_paymentsFactOne row per payment transactionfact_ordersFactOne row per orderdaily_revenueAggregate martPre-aggregated revenue by date/country/product/attribution

Business Definitions
TermDefinitionGross RevenueSum of successful payment amounts before refundsRefundsTotal reversed amounts for a periodNet RevenueGross Revenue minus Refunds/ChargebacksPaid OrderAn order with at least one successful reconciled paymentOrphan PaymentA payment that cannot be matched to any orderRevenue RecognitionAt successful payment timestamp, adjusted when refunds arrive

Known Limitations and Future Improvements

dbt integration — planned as a transformation layer in BigQuery, replacing direct Python loads with SQL models
Incremental loading — current pipeline is full-refresh; production would process only new daily data
Real data sources — synthetic data generation would be replaced with actual provider API connections
Grafana monitoring — data quality dashboards planned for orphan rates, duplicate rates, and reconciliation health
Attribution completeness — currently ~10% of orders have no marketing attribution; production would improve linkage with user event logs


Author
Built by Julius Idowu as a portfolio project targeting data engineering roles.