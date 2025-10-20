# 🚀 Real-Time Stocks Market Data Pipeline

![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)
![DBT](https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apacheairflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?logo=apachekafka&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)

---

## 📘 Overview
This project demonstrates an **end-to-end real-time data pipeline** using the **Modern Data Stack**.  
It captures **live stock market data** from an external API, streams it using **Kafka**, orchestrates transformations with **Airflow**, loads data into **Snowflake**, transforms it using **DBT**, and visualizes insights in **Power BI**.

![Architecture](https://github.com/user-attachments/assets/6b49eb4d-4bf7-473d-9281-50c20b241760)

---

## ⚙️ Tech Stack
- **Snowflake** → Cloud Data Warehouse  
- **DBT** → SQL-based Transformations  
- **Apache Airflow** → Workflow Orchestration  
- **Apache Kafka** → Real-time Streaming  
- **Python** → Data Fetching & API Integration  
- **Docker** → Containerization  
- **Power BI** → Data Visualization  

---

## ✅ Key Features
- Fetches **real-time stock market data** (not simulated) via API  
- Streams data in **real time** using Kafka  
- Stores raw data into **MinIO** (S3-compatible object storage)  
- Orchestrates ETL using **Airflow DAGs**  
- Performs data transformations with **DBT** inside **Snowflake**  
- Creates analytics-ready dashboards in **Power BI**

---

## 📂 Repository Structure

```text
real-time-stocks-pipeline/
├── producer/                     # Kafka producer (Finnhub API)
│   └── producer.py
├── consumer/                     # Kafka consumer (MinIO sink)
│   └── consumer.py
├── dbt_stocks/models/
│   ├── bronze
│   │   ├── bronze_stg_stock_quotes.sql
│   │   └── sources.yml
│   ├── silver
│   │   └── silver_clean_stock_quotes.sql
│   └── gold
│       ├── gold_candlestick.sql
│       ├── gold_kpi.sql
│       └── gold_treechart.sql
├── dag/
│   └── minio_to_snowflake.py
├── docker-compose.yml            # Kafka, Zookeeper, MinIO, Airflow, Postgres
├── requirements.txt
└── README.md                     # Documentation
```

---

## 🚀 Getting Started

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/<your-username>/real-time-stocks-pipeline.git
cd real-time-stocks-pipeline
```

---

### **2️⃣ Setup Docker Compose**
Create a `docker-compose.yml` file with the following content:

```yaml
version: "3.8"
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.1
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.4.1
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,PLAINTEXT_HOST://0.0.0.0:29092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1

  kafdrop:
    image: obsidiandynamics/kafdrop:latest
    container_name: kafdrop
    depends_on:
      - kafka
    ports:
      - "9000:9000"
    environment:
      KAFKA_BROKERCONNECT: "kafka:9092"

  minio:
    image: minio/minio:latest
    container_name: minio
    ports:
      - "9001:9001"
      - "9002:9000"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: password123
    command: server /data --console-address ":9001"

  airflow-webserver:
    image: apache/airflow:2.9.3
    container_name: airflow-webserver
    restart: always
    depends_on:
      - airflow-scheduler
      - postgres
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: "False"
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    command: webserver

  airflow-scheduler:
    image: apache/airflow:2.9.3
    container_name: airflow-scheduler
    restart: always
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: "False"
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: scheduler

  postgres:
    image: postgres:15
    container_name: airflow-postgres
    restart: always
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

---

### **3️⃣ Launch the Containers**
```bash
docker compose up -d
```

---

### **4️⃣ Initialize Airflow Database**
```bash
docker compose exec airflow-scheduler airflow db init
docker compose run airflow-webserver airflow db migrate
docker compose exec airflow-webserver airflow users create \
  --username <USER_NAME> \
  --firstname <FIRST_NAME> \
  --lastname <LAST_NAME> \
  --role Admin \
  --email <EMAIL> \
  --password password123
```

---

### **5️⃣ Setup Kafka Topics & MinIO**
- Open **Kafdrop UI** → [http://localhost:9000](http://localhost:9000)  
  → Create a new topic: `stocks-topic`
- Open **MinIO Console** → [http://localhost:9001](http://localhost:9001)  
  → Login with `admin / password123`  
  → Create a new bucket, e.g., `stock-data`

---

### **6️⃣ Configure Airflow DAG**
Place your DAG file (`minio_to_snowflake.py`) inside the `dags/` folder.  
The DAG should:
1. Download stock data from MinIO  
2. Load data into **Snowflake**  
3. Run every **1 minute**

View DAGs at → [http://localhost:8080](http://localhost:8080)

---

### **7️⃣ DBT Setup**
Initialize DBT:
```bash
mkdir dbt_stocks && cd dbt_stocks
dbt init dbt_stocks
```

Follow **Bronze → Silver → Gold** model structure:
- **Bronze** → Raw data from Snowflake staging  
- **Silver** → Cleaned & validated data  
- **Gold** → Analytical views (KPIs, candlestick charts, trends)

Run:
```bash
dbt run
```

---

### **8️⃣ Power BI Dashboard**
Connect Power BI to **Snowflake (Gold Layer)** using **Direct Query**.  
Create visuals:
- 📈 Candlestick chart – market trends  
- 🌳 Tree chart – stock movements  
- 🎯 KPI & Gauge charts – volume & performance  

---

## 📊 Final Deliverables
✅ Automated **real-time data pipeline**  
✅ **Snowflake** data layers (Bronze → Silver → Gold)  
✅ **DBT** models for transformations  
✅ **Airflow** for orchestration  
✅ **Power BI** dashboards for insights  

---


---
