import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_gigachat.embeddings import GigaChatEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

q_client = QdrantClient(
    host='localhost',
    port=6565)
collection_name = "subject_databases"
if not q_client.collection_exists(collection_name):
    q_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

gigachat_embeddings = GigaChatEmbeddings(
    credentials=os.getenv('GIGACHAT_API_KEY'),
    verify_ssl_certs=False)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 600,
    chunk_overlap = 120,
    separators = ['\n\n', '\n', '. ', ' ', ''])


with open(BASE_DIR / 'book.md', encoding='utf-8') as f:
    text = f.read()
    chunks = text_splitter.split_text(text)
    n = len(chunks)
    print(f'Количество чанков: {n}')

    for i, chunk_text in enumerate(chunks):
        print(f'Загрузка чанка {i + 1}/{n}')

        point = PointStruct(
            id = str(uuid.uuid4()),
            vector = gigachat_embeddings.embed_documents(texts=[chunk_text])[0],
            payload = {'file': 'book.pdf', 'chunk': chunk_text})

        _ = q_client.upsert(
            collection_name = collection_name,
            points = [point], wait = True)

q_client.close()
