# Ruta: utils.py
import os
from datetime import datetime
from config import FOLDER_RAW, FOLDER_PROCESSED, FOLDER_LOGS

def preparar_carpetas():
    """Crea las carpetas necesarias si no existen."""
    for carpeta in[FOLDER_RAW, FOLDER_PROCESSED, FOLDER_LOGS]:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

def log_evento(mensaje):
    """Guarda un registro en un archivo txt diario y lo imprime en consola."""
    preparar_carpetas()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    ruta_log = os.path.join(FOLDER_LOGS, f"log_{fecha_hoy}.txt")
    
    with open(ruta_log, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {mensaje}\n")
    print(f"📝 {mensaje}")

def parse_m3u_content(content_lines):
    """Extrae metadatos, nombre del canal y URL de las líneas de una lista M3U."""
    entries =[]
    current_meta = None
    
    for line in content_lines:
        line = line.strip()
        if not line: continue
        
        if line.startswith('#EXTINF'):
            current_meta = line
        elif line.startswith('http') and current_meta:
            # Extraer el nombre del canal después de la coma
            nombre_canal = "Desconocido"
            if "," in current_meta:
                nombre_canal = current_meta.split(",")[-1].strip()
                
            entries.append({
                'meta': current_meta,
                'url': line,
                'name': nombre_canal,
                'category': 'Otros',
                'std_name': nombre_canal
            })
            current_meta = None
    return entries