# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import _
from odoo.exceptions import ValidationError
import pickle
import logging
_logger = logging.getLogger(__name__)

try:
    import langchain
    import langchain_community
    import openai
    import tiktoken
    import pgvector
    import psycopg2

    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.text_splitter import CharacterTextSplitter
    from langchain.document_loaders import TextLoader
    from langchain.vectorstores.pgvector import PGVector
    from langchain.vectorstores.pgvector import DistanceStrategy
    from langchain_community.chat_models import ChatOpenAI
    from langchain.chains.question_answering import load_qa_chain

except ImportError:
    raise ValidationError(_(f'Dependencies missing, please run requirements.txt file of this module using command, pip3 install -r odoo_openai_chatbot/requirements.txt'))
except Exception as e:
    _logger.error(_(e))


class AiChatBot():
    
    def __init__(self, api_key, **kwargs) -> None:
        self.api_key = api_key
        openai.api_key = api_key
        
    
    def _get_model_list(self):
        try:
            models = openai.Model.list()
            return [(i.id,i.id) for i in models['data'] if i['id'] in ['gpt-4', 'gpt-3.5-turbo']]   
        except openai.error.OpenAIError as e:
            raise ValidationError(f"OpenAI API error: {e}")
        except Exception as e:
            raise ValidationError(f"Error: {e}")

    def load_knowledge_base(self, file_path):
        loader = TextLoader(file_path)
        documents = loader.load()
        return documents
    
    def get_connection_string(self, connection_info):
        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=connection_info.get('host', "localhost"),
            port=connection_info.get('port', 5432),
            database=connection_info.get('dbname', "odoo"),
            user=connection_info.get('user', "odoo"),
            password=connection_info.get('password', "odoo"),
        )
        return CONNECTION_STRING


    def split_data_to_chunks(self, documents):
        # if os.path.exists("chunks.pkl"):
        #     with open("chunks.pkl", "rb") as file:
        #         docs = pickle.load(file)
        # else:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        docs = text_splitter.split_documents(documents)
        with open("chunks.pkl", "wb") as file:
            pickle.dump(docs, file)
        return docs


    def compute_embeddings(self):
        # text-embedding-ada-002 used by default model_name
        embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        return embeddings


    def store_and_retrieve_embeddings(self, docs, embeddings, CONNECTION_STRING, collection_name):
        db = PGVector.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=collection_name,
            connection_string=CONNECTION_STRING,
            distance_strategy=DistanceStrategy.COSINE,
            openai_api_key= self.api_key,
            pre_delete_collection=True,
        )

        retriever = db.as_retriever()
        return retriever
    
    def chatbot(self, query, connection_info, collection_name,**kwargs):
        model_name = kwargs.get('model_name', False) or 'gpt-3.5-turbo'
        temperature = kwargs.get('temperature', False) or 0
        max_tokens = kwargs.get('max_tokens', False) or 200
        CONNECTION_STRING = self.get_connection_string(connection_info)
        retriever = self.get_retriever(CONNECTION_STRING, collection_name)
        docs = retriever.get_relevant_documents(query)
        if not docs:
            return [False, "You need to train me first !!!"]
        else:
            docs = docs[0]
        chain = load_qa_chain(ChatOpenAI(openai_api_key=str(
            self.api_key), model=model_name, temperature=temperature, max_tokens=max_tokens, request_timeout=120), chain_type="stuff")
        response = chain.run(input_documents=[docs], question=query)
        return [True, response and response.strip()]
    
    def train_model(self, file_path, connection_info={}, collection_name="ai_livechat_bot"):
        try:
            documents = self.load_knowledge_base(file_path)
        except FileNotFoundError:
            []
            print("You have not loaded your knowledge base kindly run load_knowledge_base.py file and provide the file path to it.")
        docs = self.split_data_to_chunks(documents)
        CONNECTION_STRING = self.get_connection_string(connection_info)
        embeddings = self.compute_embeddings()
        retriever = self.store_and_retrieve_embeddings(
            docs, embeddings, CONNECTION_STRING, collection_name)
        return retriever
    
    def get_retriever(self, CONNECTION_STRING, collection_name):
        embeddings = self.compute_embeddings()
        store = PGVector(
            connection_string=CONNECTION_STRING,
            embedding_function=embeddings,
            collection_name=collection_name,
            distance_strategy=DistanceStrategy.COSINE,
        )

        retriever = store.as_retriever()
        return retriever


