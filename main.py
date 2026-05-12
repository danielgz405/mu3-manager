# Ruta: main.py
from utils import preparar_carpetas, log_evento
from manager_module import fusionar_listas_raw, limpiar_y_agrupar_lista
from player_module import reproductor_terminal

def main():
    preparar_carpetas()
    log_evento("Gestor IPTV modular iniciado.")
    
    while True:
        print("\n" + "="*50)
        print(" 🌟 GESTOR IPTV MODULAR (CON IA) 🌟")
        print("="*50)
        print(" 1. FUSIONAR listas crudas (Carpeta 'm3u-list')")
        print(" 2. LIMPIAR, unificar canales con IA y testear calidad")
        print(" 3. ABRIR REPRODUCTOR IPTV (Terminal Mac)")
        print(" 4. Salir")
        print("-"*50)
        
        op = input("Selecciona una opción: ").strip()
        
        if op == '1': 
            fusionar_listas_raw()
        elif op == '2': 
            limpiar_y_agrupar_lista()
        elif op == '3': 
            reproductor_terminal()
        elif op == '4': 
            print("¡Adiós!")
            break
        else:
            print("⚠️ Opción no válida.")

if __name__ == '__main__':
    main()