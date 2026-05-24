# Data Engineering & Science Reference

## Table of Contents
1. [Real-Time Event Streaming with Kafka](#kafka)
2. [Orchestration Pipelines using Airflow](#airflow)
3. [Data Science & ML Pipelines with Pandas/Scikit-learn](#ml-pipelines)
4. [Enterprise Data Warehousing (BigQuery & Snowflake)](#warehousing)

---

## 1. Real-Time Event Streaming with Kafka {#kafka}

To support event-driven applications, high-throughput transactions, and analytical enrichment, services stream data via Kafka clusters.

### Kafka Node / Publisher Pattern (NestJS)
```typescript
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { Kafka, Producer } from 'kafkajs';

@Injectable()
export class EventProducerService implements OnModuleInit, OnModuleDestroy {
  private kafka = new Kafka({
    clientId: 'titan-analytics',
    brokers: ['kafka-broker-1:9092', 'kafka-broker-2:9092'],
  });
  private producer: Producer = this.kafka.producer();

  async onModuleInit() {
    await this.producer.connect();
  }

  async emit(topic: string, event: { type: string; payload: any }) {
    await this.producer.send({
      topic,
      messages: [{ value: JSON.stringify(event) }],
    });
  }

  async onModuleDestroy() {
    await this.producer.disconnect();
  }
}
```

---

## 2. Orchestration Pipelines using Airflow {#airflow}

Analytical extraction, loading, and transformations (ELT) must run as scheduled Directed Acyclic Graphs (DAGs) on Apache Airflow.

### Production Airflow ETL DAG Template
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator

default_args = {
    'owner': 'titan-data-science',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['data-alerts@omega-titan.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'titan_daily_analytics_elt',
    default_args=default_args,
    description='ETL processing to denormalize daily workspace metrics',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    summarize_activity = BigQueryExecuteQueryOperator(
        task_id='summarize_workspace_activity',
        sql="""
            SELECT 
              workspace_id,
              DATE(timestamp) as date,
              COUNT(id) as total_interactions
            FROM `omega-titan-prod.logs.user_events`
            WHERE DATE(timestamp) = CURRENT_DATE() - 1
            GROUP BY workspace_id, date
        """,
        use_legacy_sql=False,
        destination_dataset_table='omega-titan-prod.analytics.daily_workspace_activity',
        write_disposition='WRITE_APPEND',
    )
```

---

## 3. Data Science & ML Pipelines with Pandas/Scikit-learn {#ml-pipelines}

Machine learning pipelines must enforce data quality, handle missing fields, and scale prediction operations.

### Python Prediction & Feature Engineering Pipeline
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

class ChurnModelPipeline:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def process_data(self, file_path: str):
        # 1. Feature Engineering
        df = pd.read_csv(file_path)
        df['interaction_frequency'] = df['total_clicks'] / (df['days_active'] + 1)
        
        X = df[['interaction_frequency', 'subscription_cost', 'days_active']]
        y = df['churned']
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train(self, X_train, y_train):
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)

    def save_artifacts(self, model_path: str, scaler_path: str):
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)

if __name__ == "__main__":
    pipeline = ChurnModelPipeline()
    X_train, X_test, y_train, y_test = pipeline.process_data('data/churn_records.csv')
    pipeline.train(X_train, y_train)
    pipeline.save_artifacts('models/churn_forest.pkl', 'models/standard_scaler.pkl')
    print("Model pipeline run successfully completed.")
```

---

## 4. Enterprise Data Warehousing (BigQuery & Snowflake) {#warehousing}

We separate transactional storage (PostgreSQL) from analytical data storage (BigQuery or Snowflake):

*   **BigQuery**: Used for high-throughput, low-cost analytical ad-hoc querying directly from raw event streams.
*   **Snowflake**: Standard for multi-party governed data storage, business intelligence dashboards, and cross-organization financial auditing.
*   **Partitioning Constraints**: Every analytical table containing log or timestamp information must enforce partition filters to prevent wasteful full-table scans.
