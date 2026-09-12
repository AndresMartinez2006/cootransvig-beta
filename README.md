# COOTRANSVIG - Inspección Preoperacional

## Estructura

- app.py
- requirements.txt
- assets/logo_cootransvig.jpg
- assets/flota_cootransvig.jpg
- data/inspecciones.json

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Usuarios

- admin / 1234
- conductor1 / 1234
- conductor2 / 1234
- conductor3 / 1234
- conductor4 / 1234
- conductor5 / 1234

## Funcionamiento

Los conductores guardan cada inspección en `data/inspecciones.json`.
El administrador consulta ese archivo mediante un fragmento de Streamlit
que se actualiza automáticamente cada 3 segundos.

La cámara fue eliminada del formulario.
