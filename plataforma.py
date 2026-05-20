import streamlit as st
import pandas as pd
import json
import os
from groq import Groq

# Configuración de la página web corporativa
st.set_page_config(page_title="Enterprise Customer Intelligence", layout="wide")

# Inicializar cliente de Groq de forma segura
try:
    cliente_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception:
    cliente_groq = None

st.title("📊 Sistema Inteligente de Análisis de Clientes B2B")
st.subheader("SaaS de Procesamiento Masivo de Datos con Inteligencia Artificial")

# ---- CANDADO DE COBRO CON TU WHATSAPP DIRECTO ----
st.warning("⚠️ VERSIÓN DE EVALUACIÓN ACTIVADA. Tu cuenta gratuita te permite procesar archivos de prueba de hasta 3 filas.")

# !!! REEMPLAZA LOS CEROS POR TU NÚMERO REAL DE CELULAR (Ejemplo: 573101234567) !!!
# IMPORTANTE: Debes poner el 57 al principio que es el código de Colombia
numero_celular = "573208040294" 

mensaje_whatsapp = "Hola Juan Diego, probé tu software de análisis masivo de clientes y quiero activar la suscripción comercial mensual para procesar mis archivos de Excel completos."
link_whatsapp = f"https://wa.me{numero_celular}?text={mensaje_whatsapp.replace(' ', '%20')}"

st.markdown(f"### 🚀 [▶️ HAZ CLIC AQUÍ PARA COMPRAR TU LICENCIA COMERCIAL ($100.000 COP/Mes)]({link_whatsapp})")
st.info("💳 Medios de pago aceptados al instante: **NEQUI** o **DAVIPLATA**.")
st.markdown("---")
# --------------------------------------------------

# 1. Zona de carga de archivos en la interfaz web
st.markdown("### 📥 1. Sube la base de datos de tu empresa")
archivo_cargado = st.file_uploader("Arrastra aquí tu archivo Excel o CSV con los comentarios", type=["xlsx", "csv"])

def analizar_texto_ia(texto):
    if not cliente_groq:
        return {"sentimiento": "NEUTRO", "departamento_responsable": "SOPORTE", "alerta_urgente": False}
        
    prompt_sistema = (
        "Eres un sistema experto de análisis de datos de clientes. "
        "Analiza el texto y responde ÚNICAMENTE con un objeto JSON válido. Estructura exacta:\n"
        "{\n"
        "  \"sentimiento\": \"POSITIVO\" o \"NEGATIVO\" o \"NEUTRO\",\n"
        "  \"departamento_responsable\": \"SOPORTE\" o \"VENTAS\" o \"LOGISTICA\",\n"
        "  \"alerta_urgente\": true o false\n"
        "}"
    )
    try:
        respuesta = cliente_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(respuesta.choices.message.content)
    except Exception:
        return {"sentimiento": "ERROR", "departamento_responsable": "GENERAL", "alerta_urgente": False}

if archivo_cargado is not None:
    try:
        if archivo_cargado.name.endswith('.xlsx'):
            df = pd.read_excel(archivo_cargado)
        else:
            df = pd.read_csv(archivo_cargado)
            
        st.success(f"✅ Archivo '{archivo_cargado.name}' cargado con éxito. Se detectaron {len(df)} registros.")
        
        # Limitar a 3 filas en la versión gratuita
        df_recortado = df.head(3)
        if len(df) > 3:
            st.warning("⚠️ Archivo limitado automáticamente a las primeras 3 filas por ser cuenta de evaluación. Adquiere la licencia comercial arriba para procesar todo el archivo completo.")
        
        col_texto = [c for c in df_recortado.columns if 'texto' in c.lower() or 'comentario' in c.lower() or 'opinion' in c.lower() or 'review' in c.lower()][0]
        col_cliente = [c for c in df_recortado.columns if 'nombre' in c.lower() or 'usuario' in c.lower() or 'cliente' in c.lower()][0]
        
        if st.button("🚀 Iniciar Procesamiento Masivo con IA"):
            progreso = st.progress(0)
            resultados_totales = []
            
            for i, fila in df_recortado.iterrows():
                texto_cliente = str(fila[col_texto])
                nombre_cliente = str(fila[col_cliente])
                analisis_ia = analizar_texto_ia(texto_cliente)
                
                resultados_totales.append({
                    "id": i + 1,
                    "cliente": nombre_cliente,
                    "texto_original": texto_cliente,
                    "inteligencia_ia": analisis_ia
                })
                progreso.progress((i + 1) / len(df_recortado))
            
            st.session_state['datos_procesados'] = resultados_totales
            st.success("🎉 ¡Procesamiento completado con éxito!")
    except Exception as e:
        st.error(f"Asegúrate de que tu archivo tenga una columna llamada 'Cliente' y otra llamada 'Texto'.")

st.markdown("---")

if 'datos_procesados' in st.session_state:
    datos = st.session_state['datos_procesados']
    col1, col2, col3 = st.columns(3)
    total = len(datos)
    alertas = sum(1 for item in datos if item["inteligencia_ia"].get("alerta_urgente") == True)
    positivos = sum(1 for item in datos if item["inteligencia_ia"].get("sentimiento") == "POSITIVO")
    
    with col1: st.metric(label="Total Comentarios Analizados", value=total)
    with col2: st.metric(label="Alertas Críticas", value=alertas, delta="Casos", delta_color="inverse")
    with col3: st.metric(label="Clientes Satisfechos", value=f"{(positivos/total)*100:.1f}%" if total > 0 else "0%")
        
    for item in datos:
        ia = item["inteligencia_ia"]
        with st.container():
            c_info, c_ia = st.columns()
            with c_info:
                st.markdown(f"👤 **Cliente:** {item['cliente']}")
                st.write(f"💬 *Texto:* \"{item['texto_original']}\"")
            with c_ia:
                sent = ia.get("sentimiento", "NEUTRO")
                if sent == "POSITIVO": st.success(f"😊 Sentimiento: {sent}")
                elif sent == "NEGATIVO": st.error(f"😡 Sentimiento: {sent}")
                else: st.warning(f"😐 Sentimiento: {sent}")
            st.markdown("---")
