import os
import pandas as pd
import re
import pdfplumber

def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'\s+', ' ', texto) 
    texto = re.sub(r'[^\w\s]', '', texto) 
    return texto

def extraer_texto_pdf(pdf_path):
    texto = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto += page.extract_text()
    return texto

def procesar_entrevistas(data_path='data/raw/'):
    entrevistas = []
    for file in os.listdir(data_path):
        if file.endswith(".txt"):
            print(f"Leyendo archivo TXT: {file}")
            with open(os.path.join(data_path, file), 'r', encoding='utf-8') as f:
                texto = f.read()
                texto_limpio = limpiar_texto(texto)
                entrevistas.append({'archivo': file, 'texto': texto_limpio})

        elif file.endswith(".pdf"):
            print(f"Leyendo archivo PDF: {file}")
            texto_pdf = extraer_texto_pdf(os.path.join(data_path, file))
            texto_limpio = limpiar_texto(texto_pdf)
            entrevistas.append({'archivo': file, 'texto': texto_limpio})

    if not entrevistas:
        print("No se encontraron archivos de texto o PDF en la carpeta raw")
    else:
        print(f"Archivos procesados: {len(entrevistas)}")

    df_entrevistas = pd.DataFrame(entrevistas)
    return df_entrevistas

if __name__ == "__main__":
    df_entrevistas = procesar_entrevistas()
    if not df_entrevistas.empty:
        df_entrevistas.to_csv('data/processed/entrevistas_procesadas.csv', index=False)
        print("Entrevistas procesadas y guardadas en 'data/processed/'")
    else:
        print("No se procesaron entrevistas.")
