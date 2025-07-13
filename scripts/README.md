## Project Structure

- **scripts/**
  - [`db_manager`](scripts/db_manager.py): manages postgres database connection
  - [`load_data.py`](scripts/load_data.py): loads scraped data to postgres database
  - [`scrapy.py`](scripts/scrapy.py): Functions for scrapinpy telegram channels message.
  - [`utils.py`](scripts/utils.py): Collection of function for support
- **tests/**
  - Contains unit tests for the processing modules, e.g., [`test_text_processor.py`](tests/test_text_processor.py).

- **data/**
  - Place your raw and processed data files here.
