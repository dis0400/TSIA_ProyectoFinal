import os

def contar_denuncias_violencia():
    directorio = 'data/raw'
    conteo_denuncias = 0

    for filename in os.listdir(directorio):
        if filename.endswith(".txt"):
            file_path = os.path.join(directorio, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                contenido = file.read().lower()
                # Verificar si hay mención de denuncia
                if "denuncia" in contenido or "denunció" in contenido:
                    conteo_denuncias += 1

    return conteo_denuncias

# Usar la función para contar
if __name__ == "__main__":
    conteo_total = contar_denuncias_violencia()
    print(f"Total de mujeres que han levantado denuncias de violencia de género: {conteo_total}")
