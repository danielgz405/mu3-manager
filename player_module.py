# Ruta: player_module.py
import os
import re
import subprocess
from config import FOLDER_PROCESSED
from utils import parse_m3u_content

def reproductor_terminal():
    archivos =[f for f in os.listdir(FOLDER_PROCESSED) if f.endswith('.m3u')]
    if not archivos:
        print("❌ No hay listas procesadas para reproducir.")
        return

    print("\n🍿 SELECCIONA UNA LISTA PARA REPRODUCIR:")
    for i, a in enumerate(archivos): 
        print(f" [{i+1}] {a}")
    
    sel = int(input("👉 Número: ")) - 1
    
    with open(os.path.join(FOLDER_PROCESSED, archivos[sel]), 'r', encoding='utf-8', errors='ignore') as f:
        entries = parse_m3u_content(f.readlines())

    grupos = {}
    for e in entries:
        grupo = "Otros"
        match = re.search(r'group-title="([^"]*)"', e['meta'])
        if match: 
            grupo = match.group(1)
        
        if grupo not in grupos: 
            grupos[grupo] = []
        grupos[grupo].append(e)

    nombres_grupos = list(grupos.keys())
    
    while True:
        print("\n" + "="*40)
        print(" 📺 CATEGORÍAS DISPONIBLES")
        print("="*40)
        for i, g in enumerate(nombres_grupos):
            print(f"[{i+1}] {g} ({len(grupos[g])} canales)")
        print(f"[0] Salir al menú principal")
        
        g_sel = int(input("\n👉 Selecciona una categoría: "))
        if g_sel == 0: break
        
        categoria_actual = nombres_grupos[g_sel-1]
        canales_cat = grupos[categoria_actual]
        
        while True:
            print("\n" + "-"*40)
            print(f" 📡 CANALES: {categoria_actual.upper()}")
            print("-"*40)
            for i, c in enumerate(canales_cat):
                print(f" [{i+1}] {c['name']}")
            print(f"[0] Volver a categorías")
            
            c_sel = int(input("\n👉 Selecciona un canal para ver: "))
            if c_sel == 0: break
            
            canal_url = canales_cat[c_sel-1]['url']
            print(f"\n▶️ Abriendo stream... (Cierra la ventana del video para elegir otro)")
            
            try:
                subprocess.Popen(['mpv', canal_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                try:
                    subprocess.Popen(['open', '-a', 'VLC', canal_url])
                except Exception as e:
                    print(f"❌ Error: {e}. Instala mpv ('brew install mpv') o ten VLC en tu Mac.")