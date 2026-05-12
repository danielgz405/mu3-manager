# Ruta: ai_module.py
import json
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, CATEGORIAS_PERMITIDAS
from utils import log_evento

def seleccionar_modelo_ia():
    if not GEMINI_API_KEY:
        print("❌ ERROR: No se encontró GEMINI_API_KEY en el archivo .env")
        return None
        
    genai.configure(api_key=GEMINI_API_KEY)
    print("\nBuscando modelos disponibles...")
    modelos =[]
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos.append(m.name)
    except Exception as e:
        print(f"❌ Error conectando a Gemini: {e}")
        return None
            
    print("\n🤖 MODELOS DE GEMINI DISPONIBLES:")
    for i, m in enumerate(modelos):
        print(f" [{i+1}] {m}")
        
    sel = int(input("👉 Elige el modelo (Ej. 1): ")) - 1
    return modelos[sel]

def procesar_nombres_con_ia(nombres_canales, modelo_nombre):
    modelo = genai.GenerativeModel(modelo_nombre)
    
    prompt = f"""
    Actúa como un experto en IPTV. Te daré una lista de nombres brutos de canales de TV.
    1. Estandarizar el nombre (Ej: "CO: Caracol TV HD" -> "Caracol TV", "Win Spts+" -> "Win Sports+").
    2. Asignarle UNA de estas categorías estrictamente: {', '.join(CATEGORIAS_PERMITIDAS)}.
       (RCN, Caracol van en 'Noticias' o 'General'. Deportes en 'Deportivo').
       
    Devuelve ÚNICAMENTE un objeto JSON válido. Clave: nombre original. Valor: objeto con 'std_name' y 'category'. Ejemplo:
    {{
        "Caracol FHD VIP": {{"std_name": "Caracol TV", "category": "General"}},
        "Fox Sports 2": {{"std_name": "Fox Sports 2", "category": "Deportivo"}}
    }}
    
    Lista de canales:
    {json.dumps(nombres_canales)}
    """
    
    try:
        respuesta = modelo.generate_content(prompt)
        texto_limpio = respuesta.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except Exception as e:
        log_evento(f"Error con IA en un lote: {e}")
        return {}

def aplicar_ia_a_lista(entries):
    modelo = seleccionar_modelo_ia()
    if not modelo: return entries

    nombres_unicos = list(set([e['name'] for e in entries]))
    diccionario_ia = {}
    
    lote_size = 50 # Enviar de a 50 canales
    total_lotes = (len(nombres_unicos) // lote_size) + 1
    
    print(f"\n🧠 Iniciando análisis IA ({len(nombres_unicos)} canales únicos en {total_lotes} lotes)...")
    
    for i in range(0, len(nombres_unicos), lote_size):
        lote = nombres_unicos[i:i+lote_size]
        print(f" Consultando lote {(i//lote_size)+1}/{total_lotes}...")
        resultado_lote = procesar_nombres_con_ia(lote, modelo)
        diccionario_ia.update(resultado_lote)
        time.sleep(2) # Pausa preventiva para Rate Limits de Gemini
        
    for e in entries:
        nombre_orig = e['name']
        if nombre_orig in diccionario_ia:
            e['std_name'] = diccionario_ia[nombre_orig].get('std_name', nombre_orig)
            cat = diccionario_ia[nombre_orig].get('category', 'Otros')
            e['category'] = cat if cat in CATEGORIAS_PERMITIDAS else 'Otros'
            
    print("✅ Categorización por IA completada.")
    return entries