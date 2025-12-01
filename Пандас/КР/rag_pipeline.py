from abc import ABC, abstractmethod
from gigachat import GigaChat
from qdrant_client import QdrantClient
from langchain_gigachat.embeddings import GigaChatEmbeddings

class LLMService(ABC):
    @abstractmethod
    def ask(self, message:str):
        pass

    @abstractmethod
    def query_embedding(self, query:str):
        pass

class GigaChatService(LLMService):
    def __init__(self, api_key: str, model: str='GigaChat'):
        self.llm = GigaChat(verify_ssl_certs=False,
            model = model,
            credentials = api_key,
            scope="GIGACHAT_API_PERS"
        )

        self.embeddings = GigaChatEmbeddings(
            credentials=api_key,
            verify_ssl_certs=False)


    def ask(self, message: str):
        try:
            response = self.llm.chat(message)
            return response.choices[0].message.content
        except Exception as e:
            return e

    def query_embedding(self, query: str):
        embedding = self.embeddings.embed_query(query)
        return embedding

class RAGPipeline:
    def __init__(self, llm_service: LLMService, host: str='localhost', port: int=6565, url: str=None, api_key: str=None, collection_name: str='subject_databases', k: int=10):
        if url is None:
            self.q_client = QdrantClient(host=host, port=port)
        else:
            self.q_client = QdrantClient(url=url, api_key=api_key)

        self.collection_name = collection_name
        self.llm_service = llm_service
        self.k = k

        self.prompt = '''
"role": "system",
"content": "Ты - интеллектуальный ассистент. Твоя задача - отвечать на вопросы пользователей на основе предоставленных ответов. Предметная область: базы данных (sql и nosql), хранилища данных. Ты будешь помогать студенту изучать дисциплину базы данных."

"role": "user",
"content": "Инструкция:
1. Используя предоставленные ответы, реши какой подходит больше всего и используй его (только 1), иначе ответь сам.
2. НЕМНОГО подформатируй предоставленный ответ, если ты его выбрал, для более приятного вида
3. Добавь начальные/конечные слова, если предложение оборвалось.
---
!ЗДЕСЬ ПРЕДЛОЖЕННЫЕ ВАРИАНТЫ ОТВЕТОВ ДЛЯ ТЕБЯ!
Ответы:
{context}

!ФОРМАТ ОТВЕТА ОТ ТЕБЯ!
Вопрос: {question}
Источник: !ЕСЛИ ТЫ ВЫБРАЛ ПРЕДОСТАВЛЕННЫЙ ОТВЕТ, ОТВЕТЬ ЭТО: 'Базы данных'. Учебник. ИНАЧЕ: 'Сгенерировано GigaChat'!
Ответ:"
'''

    def chunks_search(self, query: str):
        search_result = self.q_client.query_points(
            collection_name = self.collection_name,
            query=self.llm_service.query_embedding(query),
            with_payload = True,
            limit = self.k
        ).points

        chunks = [s.payload['chunk'] for s in search_result]
        chunks = [f'Вариант {i+1}: {chunk}' for i, chunk in enumerate(chunks)]
        chunks = '\n\n'.join(chunks)
        print(chunks)
        return chunks

    def run(self, query: str):
        answers = self.chunks_search(query)
        message = self.prompt.format(context=answers, question=query)
        response = self.llm_service.ask(message)

        return response
