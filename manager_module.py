# Ruta: manager_module.py
import os
import re
import concurrent.futures
from datetime import datetime
from config import FOLDER_RAW, FOLDER_PROCESSED
from utils import parse_m3u_content, log_evento, preparar_carpetas
from ai_module import aplicar_ia_a_lista
from stream_module import test_stream_quality

def fusionar_listas_raw():
    preparar_carpetas()
    archivos =[f for f in os.listdir(FOLDER_RAW) if f.endswith('.m3u')]
    if not archivos:
        print(f"\n⚠️ No hay archivos en '{FOLDER_RAW}'.")
        return
    
    print("\n📂 SELECCIONA LISTAS PARA FUSIONAR:")
    for i, a in enumerate(archivos): 
        print(f" [{i+1}] {a}")
    seleccion = input("👉 Selección (ej: 1,2 o 'todos'): ").strip().lower()
    
    elegidos = archivos if seleccion == 'todos' else [archivos[int(i)-1] for i in seleccion.split(',') if i.strip().isdigit()]
    
    lista_maestra =[]
    urls_vistas = set()
    for nombre in elegidos:
        with open(os.path.join(FOLDER_RAW, nombre), 'r', encoding='utf-8', errors='ignore') as f:
            for e in parse_m3u_content(f.readlines()):
                if e['url'] not in urls_vistas:
                    urls_vistas.add(e['url'])
                    lista_maestra.append(e)

    nombre_archivo = f"FUSION_{datetime.now().strftime('%Y%m%d_%H%M')}.m3u"
    with open(os.path.join(FOLDER_PROCESSED, nombre_archivo), 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for item in lista_maestra: 
            f.write(f"{item['meta']}\n{item['url']}\n")
    log_evento(f"Fusión creada: {nombre_archivo} ({len(lista_maestra)} canales)")

def limpiar_y_agrupar_lista():
    archivos =[f for f in os.listdir(FOLDER_PROCESSED) if f.endswith('.m3u') and not f.startswith('LIMPIA_')]
    if not archivos:
        print(f"\n⚠️ No hay archivos base en '{FOLDER_PROCESSED}'. (Fusiona primero).")
        return
        
    for i, a in enumerate(archivos):
        print(f"[{i+1}] {a}")
    sel = int(input("👉 Elige la lista a limpiar: ")) - 1
    archivo_nombre = archivos[sel]
    
    ruta = os.path.join(FOLDER_PROCESSED, archivo_nombre)
    with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
        entries = parse_m3u_content(f.readlines())

    usar_ia = input("¿Deseas usar IA para categorizar y unificar nombres? (s/n): ").lower() == 's'
    
    if usar_ia:
        entries = aplicar_ia_a_lista(entries)
    
    # Agrupar por nombre estándar
    canales_agrupados = {}
    for e in entries:
        nombre = e['std_name']
        if nombre not in canales_agrupados:
            canales_agrupados[nombre] =[]
        canales_agrupados[nombre].append(e)

    lista_final =[]
    print(f"\n📡 Verificando estabilidad de {len(canales_agrupados)} canales (agrupados)...")
    
    def evaluar_grupo(nombre, grupo):
        mejor_canal = None
        mejor_tiempo = 999.0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            futuros = {ex.submit(test_stream_quality, c['url']): c for c in grupo}
            for fut in concurrent.futures.as_completed(futuros):
                funciona, tiempo = fut.result()
                if funciona and tiempo < mejor_tiempo:
                    mejor_tiempo = tiempo
                    mejor_canal = futuros[fut]
        return mejor_canal

    total = len(canales_agrupados)
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futuros_grupos =[executor.submit(evaluar_grupo, nom, grp) for nom, grp in canales_agrupados.items()]
        
        for i, futuro in enumerate(concurrent.futures.as_completed(futuros_grupos)):
            resultado = futuro.result()
            if resultado: 
                lista_final.append(resultado)
            if i % 10 == 0:
                print(f" Progreso: {i}/{total} canales evaluados...", end="\r")

    print("\n✅ Verificación completada.")
    
    ahora = datetime.now()
    nombre_limpio = archivo_nombre.replace('.m3u', '')
    ruta_guardado = os.path.join(FOLDER_PROCESSED, f"LIMPIA_{nombre_limpio}_{ahora.strftime('%H%M')}.m3u")
    
    with open(ruta_guardado, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        lista_final.sort(key=lambda x: x['category'])
        
        for item in lista_final:
            meta_parts = item['meta'].split(",")
            duracion_y_tags = meta_parts[0]
            
            if 'group-title' in duracion_y_tags:
                duracion_y_tags = re.sub(r'group-title="[^"]*"', f'group-title="{item["category"]}"', duracion_y_tags)
            else:
                duracion_y_tags += f' group-title="{item["category"]}"'
                
            f.write(f"{duracion_y_tags},{item['std_name']}\n{item['url']}\n")
            
    log_evento(f"Limpieza finalizada. Guardado en {ruta_guardado} ({len(lista_final)} canales óptimos).")