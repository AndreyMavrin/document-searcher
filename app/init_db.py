import os
import csv
from datetime import datetime
from app import config
from app.database import Base, engine, SessionLocal, es
from app.models import Document

def init_db_and_seed():
    Base.metadata.create_all(bind=engine)

    try:
        es.indices.create(index=config.INDEX_NAME)
        print(f"Создан индекс в Elasticsearch: {config.INDEX_NAME}", flush=True)
    except Exception as e:
        if "resource_already_exists_exception" in str(e):
            print(f"Индекс {config.INDEX_NAME} уже существует", flush=True)
        else:
            print(f"Не удалось подключиться к Elasticsearch: {e}", flush=True)
            return

    with SessionLocal() as db:
        if db.query(Document).count() == 0:
            if not os.path.exists(config.CSV_FILENAME):
                print(f" Файл {config.CSV_FILENAME} не найден")
                return

            with open(config.CSV_FILENAME, mode='r', newline='', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)

                for row in csv_reader:
                    if not row or len(row) < 3:
                        continue

                    date_obj = datetime.strptime(row[1].strip(), '%Y-%m-%d %H:%M:%S')
                    rubrics_str = row[2]
                    rubrics_list = [rubric.strip() for rubric in rubrics_str.split(',')] if rubrics_str else []

                    db_doc = Document(
                        text=row[0],
                        rubrics=rubrics_list,
                        created_date=date_obj
                    )
                    db.add(db_doc)
                    db.flush()

                    es_body = {
                        "id": db_doc.id,
                        "text": db_doc.text
                    }
                    es.index(index=config.INDEX_NAME, id=str(db_doc.id), document=es_body)

                db.commit()
            print("PostgreSQL и Elastic успешно заполнены данными", flush=True)