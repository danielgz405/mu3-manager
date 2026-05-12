# Ruta: stream_module.py
import requests
import time
from config import HEADERS

def test_stream_quality(url):
    """
    Verifica si el stream funciona y mide el tiempo que tarda en descargar 500KB.
    Devuelve (Boolean_Funciona, Float_TiempoRespuesta).
    """
    try:
        start_time = time.time()
        # Timeout para conectar (3s) y para leer (5s)
        with requests.get(url, stream=True, timeout=(3, 5), headers=HEADERS) as r:
            if r.status_code not in [200, 302]:
                return False, 999.0
            
            # Descargar un chunk de 512KB para validar estabilidad
            chunk = next(r.iter_content(chunk_size=512 * 1024))
            if not chunk:
                return False, 999.0
            
            elapsed = time.time() - start_time
            return True, elapsed
    except Exception:
        return False, 999.0