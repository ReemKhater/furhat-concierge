# Suppress warnings
def warn(*args, **kwargs):
    pass


import warnings
warnings.warn = warn
warnings.filterwarnings('ignore')


# Import libraries
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from furhat_remote_api import FurhatRemoteAPI
from dotenv import load_dotenv
from datetime import datetime
import pickle
import hashlib


def get_pdf_hash(directory):
    hash_obj = hashlib.sha256()
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.pdf'):
            filepath = os.path.join(directory, filename)
            hash_obj.update(filename.encode())
            hash_obj.update(str(os.path.getmtime(filepath)).encode())
    return hash_obj.hexdigest()


load_dotenv()
LOG_DIR = os.getenv('LOG_DIR', 'conversation_logs')

# Create log file
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Initialize Furhat
ip_address = os.getenv("IP_ADDRESS", "192.168.0.80")
furhat = FurhatRemoteAPI(ip_address)
furhat_name=os.getenv("VOICE_EN")
furhat.set_voice(name=furhat_name)
users = furhat.get_users()

# Loading documents
directory = '/app/Knowledge'
all_documents = []

for filename in os.listdir(directory):
    if filename.endswith('.pdf'):
        filepath = os.path.join(directory, filename)
        loader = PyPDFLoader(filepath)
        documents = loader.load()
        all_documents.extend(documents)

# Chunk
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150, separators=["\n\n", "\n", ". ", " ", ""])
texts = text_splitter.split_documents(all_documents)

# Create embeddings
embeddings = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")

current_hash = get_pdf_hash(directory)
hash_file = os.path.join("chroma_db", "pdf_hash.txt")

if os.path.exists('chroma_db'):
    if os.path.exists(hash_file):
        with open(hash_file, 'r') as f:
            saved_hash = f.read()
        if saved_hash != current_hash:
            shutil.rmtree('chroma_db')
            vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="chroma_db")
            with open(hash_file, 'w') as f:
                f.write(current_hash)
        else:
            vectorstore = Chroma(embedding_function=embeddings, persist_directory="chroma_db")
    else:
        vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="chroma_db")
        with open(hash_file, 'w') as f:
            f.write(current_hash)
else:
    os.makedirs('chroma_db', exist_ok=True)
    vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="chroma_db")
    with open(hash_file, 'w') as f:
        f.write(current_hash)

if os.path.exists('chroma_db'):
    # Load
    vectorstore = Chroma(embedding_function=embeddings, persist_directory="chroma_db")
else:
    # If not found -> throw error -> create new
    vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="chroma_db")

# Set up the LLM
llm = Ollama(
    model=os.getenv("OLLAMA_MODEL"),
    temperature=0,
    base_url="http://tinman.lst:11434",
)

# Create a prompt
system_prompt = f"""
You are Furhat, a helpful AI assistant embodied in a Furhat robot. Your primary knowledge base consists of documents about:
- UPM (Universidad Politécnica de Madrid)
- ETSIT (School of Telecommunications Engineering)
- The LST research group and its projects (Gatekeeper, Activage, Pharmaledger, Better@home, Gravitate Health, Plan4Act, Odin, Vitalise, Brainteaser, ToLife, Protect Child, BD4QoL, Improve, IDEA4RC)
- The Living Lab facilities

When answering:
1. FIRST check if the question relates to these topics
2. If yes, provide concise answers (1-2 sentences) ONLY from the documents
3. If unsure or information isn't found, say "I'm sorry, I don't have information on this topic" and then repeat the topic briefly just to be clear about it
4. For unrelated questions, respond conversationally but briefly

Never hallucinate or make up information. Don't use emojis. Never say more than two sentences. Maintain a friendly, professional tone.  

Previous conversation context:
{{history}}

Relevant document excerpts:
{{context}}
"""

qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

def log_message(speaker: str, text: str):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {speaker}: {text}\n")

# Create a retriever
def chainingFunction():
    retriever = vectorstore.as_retriever()
    history = []

# Take user query, fetch relevant documents and create a chain
def chainingFunction():
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5, "score_threshold": 0.7})
    history = []

    if len(users) > 0:
        furhat.attend(user="CLOSEST")
        greeting = "Hello! I am your conversational assistant. Feel free to ask me anything."
        furhat.say(text=greeting, blocking=True)
        log_message("ROBOT", greeting)
        furhat.gesture(name="BigSmile")

    while True:
        user_input = furhat.listen()
        query = user_input.message if user_input.message else ""
       
        if not query:
            continue
           
        furhat.gesture(name="BrowRaise")  
        log_message("USER", query)
       
        history.append({"role": "user", "content": HumanMessage(content=query)})
       
        if query:
            relevant_docs = retriever.invoke(query)
            context_documents_str = "\n\n".join(doc.page_content for doc in relevant_docs)
        else:
            context_documents_str = ""

        qa_prompt_local = qa_prompt.partial(
            history=history,
            context=context_documents_str
        )

        llm_chain = { "input": RunnablePassthrough() } | qa_prompt_local  | llm

        result = llm_chain.invoke(query)

        history.append({"role": "assistant", "content": AIMessage(content=result)})

        furhat.say(text=result, blocking=True)
        log_message("ROBOT", result)  

        furhat.gesture(name="Smile")
       
        furhat.gesture(body={
            "frames": [{"time": [0.5], "params": {"SMILE": 0.7}}],
            "class": "furhatos.gestures.Gesture"
        })

# Call function
chainingFunction()


