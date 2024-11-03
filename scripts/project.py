import os
from dotenv import load_dotenv
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import keyboard  # Para detectar teclas presionadas

# Cargar configuración desde el archivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("La clave API de OpenAI no está definida. Revisa el archivo .env")

# Directorios del proyecto
raw_directory = 'data/raw'
summaries_directory = 'data/summaries'
persist_dir = 'data/processed/index_storage'

# Asegurarse de que el directorio de almacenamiento persistente exista
if not os.path.exists(persist_dir):
    os.makedirs(persist_dir)

# Usar el mismo modelo de embeddings para indexado y consultas
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Re-crear el índice si no existe
if not os.path.exists(os.path.join(persist_dir, "docstore.json")):
    # Cargar documentos desde data/raw y data/summaries
    documentos_raw = SimpleDirectoryReader(raw_directory).load_data()
    documentos_summaries = SimpleDirectoryReader(summaries_directory).load_data()
    todos_los_documentos = documentos_raw + documentos_summaries

    # Crear y guardar el índice
    index = VectorStoreIndex.from_documents(todos_los_documentos, embed_model=embed_model, show_progress=True)
    index.storage_context.persist(persist_dir=persist_dir)
    print("Índice creado y guardado exitosamente.")
else:
    # Cargar índice existente desde almacenamiento persistente
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context, embed_model=embed_model)  # Asegúrate de usar el mismo modelo
    print("Índice cargado exitosamente desde el almacenamiento.")

# Función para hacer una consulta y guardar el reporte
def query_con_indice(pregunta, respuestas):
    query_engine = index.as_query_engine()
    
    # Proporcionar un prompt adicional para ayudar al modelo a encontrar información cuantitativa
    prompt = (
        f"Dada la siguiente pregunta, por favor proporciona una respuesta cuantitativa o basada en datos "
        f"extraídos de las entrevistas disponibles: {pregunta}"
    )
    
    respuesta = query_engine.query(prompt)
    print(f"Pregunta: {pregunta}\nRespuesta: {respuesta}\n")

    # Añadir la respuesta a la lista de respuestas para luego guardar el reporte
    respuestas.append((pregunta, str(respuesta)))

# Función para guardar el reporte en un archivo
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
        # Detectar si se presiona la tecla 'ESC' para guardar el reporte y salir
        if keyboard.is_pressed('esc'):
            guardar_reporte(respuestas)
            break

        # Leer la pregunta del usuario
        pregunta = input("Tu pregunta: ")
        if pregunta.strip():  # Verifica que no sea una pregunta vacía
            query_con_indice(pregunta, respuestas)
