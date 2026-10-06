from fastapi import APIRouter, HTTPException, status
from app import config
from app.database import SessionLocal, es
from app.models import Document

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.get("/search", summary="Полнотекстовый поиск по тексту документов")
def search_documents(query: str):
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Запрос пустой")

    try:
        es_response = es.search(
            index=config.INDEX_NAME,
            query={"match": {"text": query}},
            size=100
        )
        hits = es_response['hits']['hits']
        document_ids = [int(hit['_source']['id']) for hit in hits]

        if not document_ids:
            return []
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Elastic error: {e}")

    with SessionLocal() as db:
        documents = db.query(Document)\
            .filter(Document.id.in_(document_ids))\
            .order_by(Document.created_date.desc())\
            .limit(20)\
            .all()
        return [doc.to_dict() for doc in documents]


@router.delete("/{id}", summary="Удалить документ по ID из БД и индекса")
def delete_document(id: int):
    with SessionLocal() as db:
        document = db.query(Document).get(id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")

        db.delete(document)

        try:
            if es.exists(index=config.INDEX_NAME, id=str(id)):
                es.delete(index=config.INDEX_NAME, id=str(id))
        except Exception as e:
            print(f"Не удалось удалить из Elastic: {e}", flush=True)

        db.commit()
        return document.to_dict()
