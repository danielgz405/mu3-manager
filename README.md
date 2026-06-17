# mu3-list — Gestor IPTV Modular con IA

Gestor de listas de reproducción M3U para IPTV con tres fases: fusión de listas crudas, limpieza y categorización con inteligencia artificial (Gemini), y reproductor por categorías en terminal.

## Características

- **Fusión inteligente** — Combina múltiples archivos `.m3u` eliminando canales duplicados por URL.
- **Limpieza con IA** — Estandariza nombres de canales y asigna categorías mediante Google Gemini.
- **Testeo de calidad** — Verifica la disponibilidad de cada stream descargando 512 KB con timeouts controlados (3s connect / 5s read).
- **Agrupación y ordenación** — Elige el mejor stream para cada canal (el más rápido) y ordena la lista final por categoría.
- **Reproductor por categorías** — Navega las listas procesadas por categoría, busca canales, y reproduce con **mpv** (recomendado) o **VLC**.

## Requisitos

- **Python 3.8+**
- [mpv](https://mpv.io/) (reproductor recomendado) o VLC
- Una **clave de API de Google Gemini** (gratuita en [Google AI Studio](https://aistudio.google.com/))

## Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/mu3-list.git
cd mu3-list

# 2. Instala las dependencias
pip install google-generativeai requests python-dotenv

# 3. Crea el archivo de configuración .env
echo "GEMINI_API_KEY=tu_clave_aqui" > .env

# 4. Crea las carpetas de trabajo
mkdir -p m3u-list m3u-procesadas m3u-logs

# 5. Coloca tus archivos .m3u dentro de m3u-list/

# 6. Ejecuta
python main.py
```

> **Nota:** Si usas un entorno virtual, créalo y actívalo antes del paso 2:
> ```bash
> python -m venv venv
> source venv/bin/activate
> ```

## Cómo usar

Al ejecutar `python main.py` verás un menú con cuatro opciones:

### 1. Fusionar listas crudas

Selecciona uno o varios archivos `.m3u` de la carpeta `m3u-list/`. El script los combina eliminando URLs duplicadas y guarda el resultado en `m3u-procesadas/` con el formato `FUSION_YYYYMMDD_HHMM.m3u`.

### 2. Limpiar, unificar canales con IA y testear calidad

Primero elige una lista de `m3u-procesadas/` (la que acabas de fusionar). Luego:

1. **(Opcional) Categorización con IA** — Si respondes `s`, el script envía los nombres de canales a Gemini en lotes de 40, con una pausa de 6s entre lotes para respetar la cuota gratuita. La IA devuelve un nombre estandarizado y una categoría para cada canal.
2. **Testeo de streams** — Agrupa los canales por nombre estandarizado, evalúa todos los streams de cada grupo en paralelo (20 hilos) y conserva únicamente el más rápido.
3. **Generación de lista limpia** — Guarda el resultado en `m3u-procesadas/` como `LIMPIA_<original>_HHMM.m3u`, ordenado por categoría.

### 3. Abrir reproductor IPTV

Selecciona una lista procesada (archivo `LIMPIA_*.m3u`). El menú muestra las categorías disponibles. Dentro de cada categoría puedes:

- Elegir un número para reproducir ese canal (se abre mpv o VLC en segundo plano).
- Presionar `B` para buscar por nombre dentro de la categoría.
- Presionar `0` para volver al menú anterior.

También puedes buscar en **toda** la lista desde el menú de categorías con la opción `B`.

> Para cerrar el stream, cierra la ventana del reproductor. La terminal queda libre para elegir otro canal.

### 4. Salir

Finaliza el programa.

## Estructura del proyecto

```
mu3-list/
├── main.py              # CLI menú principal
├── config.py            # Variables de entorno y rutas
├── manager_module.py    # Fusión, limpieza y testeo
├── ai_module.py         # Integración con Gemini API
├── stream_module.py     # Verificación de streams
├── player_module.py     # Reproductor en terminal
├── utils.py             # Utilidades (directorios, logs, parser M3U)
├── .env                 # GEMINI_API_KEY (no incluido en el repo)
├── m3u-list/            # Coloca aquí tus archivos .m3u originales
├── m3u-procesadas/      # Listas fusionadas y limpias (generadas)
└── m3u-logs/            # Logs diarios y debug de IA (generados)
```

## Formato M3U esperado

El parser reconoce el formato M3U estándar con `#EXTINF`:

```
#EXTM3U
#EXTINF:-1 tvg-id="..." group-title="Categoría" tvg-logo="...",Nombre del Canal
http://ejemplo.com/stream.m3u8
```

Los archivos en `m3u-list/` pueden contener cualquier formato de metadatos; la IA se encarga de normalizar los nombres durante la limpieza (opción 2).

## Dependencias

| Librería | Propósito |
|----------|-----------|
| `google-generativeai` | SDK oficial de Gemini para categorización con IA |
| `requests` | Descarga de chunks de stream para testeo de calidad |
| `python-dotenv` | Carga de `GEMINI_API_KEY` desde `.env` |

## Notas importantes

- La API gratuita de Gemini tiene límites de peticiones por minuto. El script incorpora una pausa de 60 s cuando recibe un error 429 y una pausa fija de 6 s entre lotes.
- Si no usas la IA (opción 2, responder `n`), los canales se agrupan por su nombre original sin categorizar (todos quedan como "Otros").
- Los archivos `.m3u` en `m3u-list/` están en `.gitignore`; si clonas el repo deberás agregar tus propias listas.
