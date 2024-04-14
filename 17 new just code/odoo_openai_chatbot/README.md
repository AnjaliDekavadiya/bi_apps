# odoo_openai_chatbot

# Ai Chat Bot configuration steps:

# Python >3.8.1 Is required to install the dependencies
# Install requirements.txt

pip3 install -r odoo_openai_chatbot/requirements.txt



# Create vector extension (doc-> https://github.com/pgvector/pgvector#installation)

  cd /tmp \
 git clone --branch v0.4.4 https://github.com/pgvector/pgvector.git \
 cd pgvector \
 make \
 make install 

 
 CREATE EXTENSION vector;



# postgress version
/usr/lib/postgresql/9.3/bin/postgres -V

# install for postgres.h missing
apt install postgresql-server-dev-13.4 (Mention Postgres version after dev-)

# Clang-7 (If not found)
apt-get install clang-7



# Created Models by pgvector
1. langchain_pg_embedding
2. langchain_pg_collection


# langchain pgvector doc

https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/pgvector.html
