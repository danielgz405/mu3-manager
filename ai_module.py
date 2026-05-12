# Ruta: ai_module.py
import json
import time
import re
import os
from datetime import datetime
import google.generativeai as genai
from config import GEMINI_API_KEY, CATEGORIAS_PERMITIDAS, FOLDER_LOGS
from utils import log_evento, preparar_carpetas

def debug_log(mensaje):
    """Guarda un log crudo de lo que pasa con la IA para auditar errores."""
    preparar_carpetas()
    ruta_debug = os.path.join(FOLDER_LOGS, "debug_ia_logs.txt")
    with open(ruta_debug, 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")

def seleccionar_modelo_ia():
    if not GEMINI_API_KEY:
        print("❌ ERROR: No se encontró GEMINI_API_KEY en el archivo .env")
        return None
        
    genai.configure(api_key=GEMINI_API_KEY)
    print("\nBuscando modelos de texto disponibles...")
    modelos =[]
    
    excluir_keywords =[
        'tts', 'image', 'vision', 'audio', 'robotics', 'lyria', 
        'nano', 'computer-use', 'deep-research', 'embed', 'clip'
    ]
    
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                nombre_lower = m.name.lower()
                if 'gemini' in nombre_lower or 'gemma' in nombre_lower:
                    if not any(excluido in nombre_lower for excluido in excluir_keywords):
                        modelos.append(m.name)
    except Exception as e:
        print(f"❌ Error conectando a Gemini: {e}")
        return None
            
    if not modelos:
        print("❌ No se encontraron modelos válidos.")
        return None

    print("\n🤖 MODELOS DE TEXTO DISPONIBLES:")
    for i, m in enumerate(modelos):
        print(f"[{i+1}] {m}")
        
    while True:
        try:
            sel = int(input("👉 Elige el modelo (Ej. 1): ")) - 1
            if 0 <= sel < len(modelos):
                return modelos[sel]
            else:
                print("❌ Opción fuera de rango.")
        except ValueError:
            print("❌ Por favor, ingresa un número válido.")

def procesar_nombres_con_ia(nombres_canales, modelo_nombre):
    modelo = genai.GenerativeModel(modelo_nombre)
    
    prompt = f"""
    Actúa como un experto en IPTV. Te daré una lista de nombres brutos de canales de TV.
    1. Estandarizar el nombre (Ej: "CO: Caracol TV HD" -> "Caracol TV", "Win Spts+" -> "Win Sports+").
    2. Asignarle UNA de estas categorías estrictamente: {', '.join(CATEGORIAS_PERMITIDAS)}.
       
    Devuelve ÚNICAMENTE un objeto JSON válido. Clave: nombre original. Valor: objeto con 'std_name' y 'category'. Ejemplo:
    {{
        "Caracol FHD VIP": {{"std_name": "Caracol TV", "category": "General"}},
        "Fox Sports 2": {{"std_name": "Fox Sports 2", "category": "Deportivo"}}
    }}
    
    Lista de canales:
    {json.dumps(nombres_canales)}
    """
    
    intentos_maximos = 3
    for intento in range(intentos_maximos):
        try:
            respuesta = modelo.generate_content(prompt)
            texto_bruto = respuesta.text
            
            # Buscamos el JSON real usando expresiones regulares (desde el primer { hasta el último })
            match = re.search(r'\{.*\}', texto_bruto, re.DOTALL)
            
            if match:
                texto_limpio = match.group(0)
                # Intentamos parsearlo
                diccionario = json.loads(texto_limpio)
                debug_log(f"✅ Éxito al parsear JSON ({len(diccionario)} items).")
                return diccionario
            else:
                debug_log(f"⚠️ IA no devolvió JSON en el intento {intento+1}. Respuesta cruda:\n{texto_bruto}")
                raise ValueError("No se detectó un formato JSON en la respuesta.")
                
        except Exception as e:
            error_str = str(e).lower()
            debug_log(f"❌ Error en intento {intento+1}: {error_str}")
            
            # Si el error es por cuota o demasiadas peticiones (Rate Limit / Quota Exceeded)
            if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                print(f" ⚠️ Límite de la API gratuita alcanzado. Esperando 60 segundos para enfriar... (Intento {intento+1}/{intentos_maximos})")
                time.sleep(60) # Pausa de 1 minuto para resetear el límite por minuto de Google
            else:
                # Si es un error de parseo u otro problema, esperamos unos segundos y reintentamos
                time.sleep(5)
                
    print(" ❌ Se agotaron los intentos para este lote. Se omitirá.")
    return {}

def aplicar_ia_a_lista(entries):
    modelo = seleccionar_modelo_ia()
    if not modelo: return entries

    nombres_unicos = list(set([e['name'] for e in entries]))
    diccionario_ia = {}
    
    lote_size = 40 # Bajamos a 40 canales por lote para aligerar la carga a la API
    total_lotes = (len(nombres_unicos) // lote_size) + 1
    
    print(f"\n🧠 Iniciando análisis IA ({len(nombres_unicos)} canales únicos en {total_lotes} lotes)...")
    print(" 💡 [INFO] Eres libre de tomar un café. Para no saturar la API gratuita, este proceso tomará tiempo.\n")
    
    for i in range(0, len(nombres_unicos), lote_size):
        lote = nombres_unicos[i:i+lote_size]
        print(f" 🔄 Consultando lote {(i//lote_size)+1} de {total_lotes}...")
        
        resultado_lote = procesar_nombres_con_ia(lote, modelo)
        diccionario_ia.update(resultado_lote)
        
        # Pausa de 6 segundos entre lotes (10 peticiones por min aprox. Respeta la cuota gratis de Google)
        time.sleep(6) 
        
    for e in entries:
        nombre_orig = e['name']
        if nombre_orig in diccionario_ia:
            e['std_name'] = diccionario_ia[nombre_orig].get('std_name', nombre_orig)
            cat = diccionario_ia[nombre_orig].get('category', 'Otros')
            e['category'] = cat if cat in CATEGORIAS_PERMITIDAS else 'Otros'
            
    print("✅ Categorización por IA completada.")
    return entries