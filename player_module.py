# Ruta: player_module.py
import os
import re
import subprocess
from config import FOLDER_PROCESSED
from utils import parse_m3u_content

def mostrar_canales_menu(titulo, lista_canales):
    """
    Submenú dinámico que muestra una lista de canales y permite reproducirlos o filtrarlos.
    """
    while True:
        print("\n" + "-"*50)
        print(f" 📡 {titulo.upper()} ({len(lista_canales)} canales)")
        print("-" * 50)
        
        # Mostramos los canales disponibles en esta vista
        for i, c in enumerate(lista_canales):
            print(f" [{i+1}] {c['name']}")
        
        print("\n Opciones:")
        print("  [Número] Reproducir canal")
        print("  [B] Buscar / Filtrar en esta lista")
        print("  [0] Volver atrás")
        
        op = input("\n👉 Tu elección: ").strip().lower()
        
        if op == '0':
            break # Sale de este menú y vuelve al anterior
            
        elif op == 'b':
            termino = input("🔎 Ingresa el nombre (o parte del nombre) a buscar: ").strip().lower()
            # Filtrar la lista actual ignorando mayúsculas/minúsculas
            filtrados =[c for c in lista_canales if termino in c['name'].lower()]
            
            if not filtrados:
                print(f"❌ No se encontraron canales con la palabra '{termino}'.")
            else:
                # Llamada recursiva para mostrar los resultados del filtro
                mostrar_canales_menu(f"RESULTADOS DE: '{termino}'", filtrados)
                
        elif op.isdigit():
            c_sel = int(op)
            if 1 <= c_sel <= len(lista_canales):
                canal_url = lista_canales[c_sel-1]['url']
                nombre_canal = lista_canales[c_sel-1]['name']
                print(f"\n▶️ Abriendo stream de '{nombre_canal}'...")
                print("   (Deja esta terminal abierta. Cierra la ventana del video para elegir otro)")
                
                try:
                    # mpv en segundo plano
                    subprocess.Popen(['mpv', canal_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except FileNotFoundError:
                    try:
                        # VLC en segundo plano nativo de Mac
                        subprocess.Popen(['open', '-a', 'VLC', canal_url])
                    except Exception as e:
                        print(f"❌ Error: {e}. Instala mpv ('brew install mpv') o ten VLC en tu Mac.")
            else:
                print("❌ Número fuera de rango. Revisa la lista.")
        else:
            print("❌ Opción no válida.")

def reproductor_terminal():
    archivos = [f for f in os.listdir(FOLDER_PROCESSED) if f.endswith('.m3u')]
    if not archivos:
        print("❌ No hay listas procesadas para reproducir.")
        return

    print("\n🍿 SELECCIONA UNA LISTA PARA REPRODUCIR:")
    for i, a in enumerate(archivos): 
        print(f" [{i+1}] {a}")
    
    try:
        sel = int(input("👉 Número: ")) - 1
        archivo_seleccionado = archivos[sel]
    except (ValueError, IndexError):
        print("❌ Selección no válida.")
        return
    
    # Cargar y parsear la lista
    with open(os.path.join(FOLDER_PROCESSED, archivo_seleccionado), 'r', encoding='utf-8', errors='ignore') as f:
        entries = parse_m3u_content(f.readlines())

    # Agrupar canales por categorías
    grupos = {}
    for e in entries:
        grupo = "Otros"
        match = re.search(r'group-title="([^"]*)"', e['meta'])
        if match: 
            grupo = match.group(1)
        
        if grupo not in grupos: 
            grupos[grupo] =[]
        grupos[grupo].append(e)

    nombres_grupos = list(grupos.keys())
    
    # Menú principal de categorías
    while True:
        print("\n" + "="*50)
        print(" 📺 CATEGORÍAS DISPONIBLES")
        print("="*50)
        for i, g in enumerate(nombres_grupos):
            print(f"[{i+1}] {g} ({len(grupos[g])} canales)")
        
        print(f"\n[B] 🔎 Buscar un canal en TODA la lista ({len(entries)} canales)")
        print(f" [0] Salir al menú principal")
        
        g_sel = input("\n👉 Elige categoría, 'B' para buscar en todo, o '0' para salir: ").strip().lower()
        
        if g_sel == '0':
            break
            
        elif g_sel == 'b':
            termino = input("🔎 Ingresa el nombre a buscar en toda la lista: ").strip().lower()
            filtrados = [c for c in entries if termino in c['name'].lower()]
            if not filtrados:
                print(f"❌ No se encontró '{termino}' en ningún grupo.")
            else:
                mostrar_canales_menu(f"BÚSQUEDA GLOBAL: '{termino}'", filtrados)
                
        elif g_sel.isdigit():
            idx = int(g_sel)
            if 1 <= idx <= len(nombres_grupos):
                categoria_actual = nombres_grupos[idx-1]
                canales_cat = grupos[categoria_actual]
                # Llamamos a nuestra nueva función dinámica
                mostrar_canales_menu(f"CATEGORÍA: {categoria_actual}", canales_cat)
            else:
                print("❌ Número de categoría fuera de rango.")
        else:
            print("❌ Opción no válida.")