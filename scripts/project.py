import os
from dotenv import load_dotenv
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import keyboard  

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("La clave API de OpenAI no está definida. Revisa el archivo .env")

raw_directory = 'data/raw'
summaries_directory = 'data/summaries'
persist_dir = 'data/processed/index_storage'

if not os.path.exists(persist_dir):
    os.makedirs(persist_dir)

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

if not os.path.exists(os.path.join(persist_dir, "docstore.json")):
    documentos_raw = SimpleDirectoryReader(raw_directory).load_data()
    documentos_summaries = SimpleDirectoryReader(summaries_directory).load_data()
    todos_los_documentos = documentos_raw + documentos_summaries

    index = VectorStoreIndex.from_documents(todos_los_documentos, embed_model=embed_model, show_progress=True)
    index.storage_context.persist(persist_dir=persist_dir)
    print("Índice creado y guardado exitosamente.")
else:
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context, embed_model=embed_model)
    print("Índice cargado exitosamente desde el almacenamiento.")

def query_con_indice(pregunta, respuestas):
    query_engine = index.as_query_engine()
    
    prompt = (
        f"Dada la siguiente pregunta, por favor proporciona una respuesta cuantitativa o basada en datos "
        f"extraídos de las entrevistas disponibles: {pregunta}"
    )
    
    respuesta = query_engine.query(prompt)
    print(f"Pregunta: {pregunta}\nRespuesta: {respuesta}\n")

    respuestas.append((pregunta, str(respuesta)))

def guardar_reporte(respuestas):
    reporte_path = os.path.join('data/processed', "reporte_interactivo.txt")
    with open(reporte_path, 'w', encoding='utf-8') as file:
        for pregunta, respuesta in respuestas:
            file.write(f"Pregunta: {pregunta}\nRespuesta: {respuesta}\n\n")

    print(f"\nReporte guardado en {reporte_path}")

if __name__ == "__main__":
    respuestas = []

    print("Interactúa con el sistema de preguntas. Escribe tu pregunta y presiona Enter.")
    print("Para finalizar y guardar el reporte, presiona la tecla 'ESC'.\n")

    while True:
        if keyboard.is_pressed('esc'):
            guardar_reporte(respuestas)
            break

        pregunta = input("Tu pregunta: ")
        if pregunta.strip():
            query_con_indice(pregunta, respuestas)
