# Shipping a Data Product: From Raw Telegram Data to an Analytical API

An end-to-end data pipeline for Telegram, leveraging dbt for transformation, Dagster for orchestration, and YOLOv8 for data enrichment.

## Setup Instructions

1. **Clone the Repository**
    ```
    git clone https://github.com/mikek1337/Shipping-a-Data-Product-From-Raw-Telegram-Data-to-an-Analytical-API-week-7.git
    ```
    ```
    cd Shipping-a-Data-Product-From-Raw-Telegram-Data-to-an-Analytical-API-week-7
    ```

2. **Create and Activate a Virtual Environment**
    ```
    python3 -m venv .venv
    source venv/bin/activate
    ```

3. **Install Dependencies**
    ```
    pip install -r requirements.txt
    ```

6. **Enviroment variables**
    ```
    APP_ID=
    APP_KEY=
    PHONE=
    HOST=
    PASSWORD=
    USERNAME=
    PORT=
    DATABASE=
    ```
7. **To run Telegram scraper**
    ```
    python script/scrapy.py
    ```
    Note: The scraped data is stored in data/raw the messages are stored in data/raw/telegram-messages/YYYY-MM-DD/channel_name.json so make sure data/raw path exists
    
    Note: if you want to add more channels change the config.ini file. 
8. **Load scraped data to database**
    ```
    python script/load_data.py
    ```
9. **Move to DBT folder**
    ```
    cd telegram_analysis
    ```
10. **Run DBT model test**
    ```
    dbt test
    ```
11. **Run DBT model**
    ```
    dbt run
    ```