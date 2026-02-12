import os
from dotenv import load_dotenv
from rag_pipeline import RAGPipeline, GigaChatService

load_dotenv()

gigchat_api_key = os.getenv('GIGACHAT_API_KEY')

service = GigaChatService(api_key=gigchat_api_key)
pipeline = RAGPipeline(service, k=5)

print(pipeline.run('Что такое внешний ключ?'))
