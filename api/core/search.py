import os
import cohere
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from api.core.config import AZURE_OPENAI_EMBEDDINGS_KEY, AZURE_OPENAI_EMBEDDINGS_ENDPOINT, AZURE_OPENAI_EMBEDDINGS_API_VERSION, AZURE_OPENAI_EMBEDDINGS_BASE_MODEL, AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME, COHERE_API_KEY, COHERE_API_BASE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
persist_directory = os.path.join(BASE_DIR, "vector_db")

embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME,
    azure_endpoint=AZURE_OPENAI_EMBEDDINGS_ENDPOINT,
    openai_api_key=AZURE_OPENAI_EMBEDDINGS_KEY,
    openai_api_version=AZURE_OPENAI_EMBEDDINGS_API_VERSION,
    chunk_size=500
)

# Cargar base de datos de vectores desde el almacenamiento
vector_db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model
)

# Inicializar Cohere para Rerank
co = cohere.Client(api_key=COHERE_API_KEY,base_url=COHERE_API_BASE)

def search_with_rerank(query, top_k=10):
    """Realiza una búsqueda en la base de datos y aplica reranking con Cohere."""
    print(f"🔍 Buscando: {query}")
    
    # Buscar en la base de datos vectorial usando embeddings
    docs = vector_db.similarity_search(query, k=top_k)

    if not docs:
        print("⚠️ No se encontraron resultados.")
        return []

    # Preparar los documentos para Cohere Rerank
    doc_texts = [doc.page_content for doc in docs]

    # Aplicar Cohere Rerank
    rerank_results = co.rerank(
        query=query,
        documents=doc_texts,
        top_n=5,  # Devuelve los 5 mejores resultados reordenados
        model="rerank-multilingual-v3.0"
    )

    # Obtener los documentos reordenados con metadata
    reranked_docs = [docs[result.index] for result in rerank_results.results]
    
    # Extraer contenido y metadata (nombre del archivo fuente)
    retrieved_info = []
    for doc in reranked_docs:
        retrieved_info.append({
            "source": doc.metadata.get("source"),  # Nombre del PDF
            "content": doc.page_content
        })

    return retrieved_info  # Devuelve tanto el contenido como el nombre del PDF

