from dotenv import load_dotenv
import os
import openai
import time

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("La clave API de OpenAI no está definida. Revisa el archivo .env")

input_directory = 'data/raw'
output_directory = 'data/summaries'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def generar_resumen_gpt(texto):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un profesional encargado de resumir textos largos de entrevistas.",
                },
                {
                    "role": "user",
                    "content": f"Resume el siguiente texto: {texto}",
                }
            ]
        )
        resumen = completion['choices'][0]['message']['content']
        return resumen
    except openai.error.RateLimitError:
        print("Has alcanzado el límite de tasa de la API. Esperando 60 segundos antes de reintentar...")
        time.sleep(60)
        return generar_resumen_gpt(texto)
    except openai.error.InvalidRequestError as e:
        print(f"Error en la solicitud: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

for filename in os.listdir(input_directory):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, f"resumen_{filename}")

        with open(input_path, 'r', encoding='utf-8') as file:
            texto = file.read()

        print(f"Generando resumen para: {filename}")
        resumen = generar_resumen_gpt(texto)

        if resumen:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write("Texto Original:\n")
                file.write(texto)
                file.write("\n\nResumen Generado:\n")
                file.write(resumen)

            print(f"Resumen generado y guardado en {output_path}")
        else:
            print(f"No se pudo generar un resumen para {filename}")

print("Proceso completado.")
