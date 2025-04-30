import os
import pandas as pd
from langchain_openai import AzureChatOpenAI
from api.core.config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME
from api.core.search import search_with_rerank
from api.core.translator import detect_language, translate_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurar el modelo de lenguaje (LLM) de Azure OpenAI
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    openai_api_key=AZURE_OPENAI_API_KEY,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,  
    temperature=0.2,
    max_tokens=1500
)

print("LLM correctamente configurado")

# Cargar metadata desde CSV en un diccionario (NO SE MODIFICA)
def load_metadata():
    """Carga la metadata y la almacena en un diccionario usando el filename como clave."""
    metadata_path = os.path.join(BASE_DIR, "metadata.csv")
    metadata_df = pd.read_csv(metadata_path)
    metadata_dict = {
        row["filename"]: {key: value for key, value in row.items() if key != "filename"}
        for _, row in metadata_df.iterrows()
    }
    return metadata_dict

# Cargar metadata al iniciar la aplicación
metadata_dict = load_metadata()

def generate_answer(query):
    """Busca información en la base de datos, adjunta metadata y genera una respuesta con el LLM en el idioma original del usuario."""
    # Detectar idioma de la pregunta
    detected_lang = detect_language(query)

    # Traducir la pregunta al inglés
    query_translated = translate_text(query, "en")

    # Recuperar información con RAG
    retrieved_info = search_with_rerank(query_translated)
    if not retrieved_info:
        return translate_text(
            "Lo siento, no encontré información relevante en la base de datos.",
            detected_lang
        )

    # Construir contexto y metadata_info
    context = ""
    metadata_info = "<h2>Metadatos de origen:</h2>"

    for info in retrieved_info:
        source = info["source"]
        content = info["content"]
        content_translated = translate_text(content, "en")

        metadata = metadata_dict[source]

        # Construir la metadata SIN triple comillas y SIN sangría
        metadata_info += (
            "<br><hr><br>"
            f"<h3><b>Fuente:</b> {metadata['title']}</h3>"
            f"<p><b>Título:</b> {metadata['title']}</p>"
            f"<p><b>Autores:</b> {metadata['authors']}</p>"
            f"<p><b>Organización:</b> {metadata['organization']}</p>"
            f"<p><b>Fecha de publicación:</b> {metadata['publication_date']}</p>"
            f"<p><b>Citación:</b> {metadata['citation']}</p>"
            f"<p><b>Puntuación:</b> {metadata['score']}</p>"
        )

        # Construir el contexto
        context += (
            f"<b>Fuente:</b> {source}<br>{content_translated}<br><br>"
        )

    # Prompts para el LLM (mantenidos, pero sin sangría)
    prompts = [
        f"""
<role> Debes asumir el rol de un médico especialista en Obstetricia que atiende partos de emergencia. </role>

Eres un asistente experto que responde preguntas basadas únicamente en la información proporcionada.
NO inventes información adicional. Si no encuentras respuesta en el contexto, di que no tienes información suficiente.
Siempre debes indicar de qué documento proviene la información.

Haciendo uso de la información en contexto, debes indicar de forma efectiva los mejores procedimientos médicos para solventar el problema dado en la consulta del usuario.
La información obtenida será leída por médicos y funcionarios del área de la salud, por lo que debe mantenerse detallada, clara y con los tecnicismos médicos necesarios para garantizar precisión y evitar la pérdida de información valiosa.

**Requisitos para la respuesta:**
1. La respuesta debe proporcionar detalles clínicos específicos, incluyendo dosis, vías de administración, contraindicaciones y efectos adversos si están disponibles en el contexto.
2. Cada procedimiento médico debe ser estructurado y enumerado en secciones claras, con explicaciones detalladas de por qué se recomienda cada paso.
3. Debes incluir recomendaciones adicionales si el contexto menciona otras opciones, alertas sobre posibles complicaciones y advertencias de seguridad.
4. En caso de que haya varias alternativas, compáralas de manera estructurada, señalando ventajas y desventajas con base en la información disponible.
5. Incluye ejemplos de escenarios clínicos específicos si el contexto proporciona datos aplicables.

**Contexto relevante:**  
{context}

**Pregunta del usuario:**  
{query_translated}

**Respuesta detallada:**  
""",
        f"""
<system>
You are a specialized obstetric chatbot. You respond to questions from other doctors regarding obstetrical emergencies.
Your answers must be medically precise, structured, and must **not include metadata in your response**.
</system>

<context>
```{context}```
</context>

<question>
{query_translated}
</question>

From the support information that you are provided, delimited by triple backticks, extract the relevant information based on the asked question delimited by triple quotes. If there are any measurements or doses mentioned in the question, try to locate them in the provided information. Then, use these relevant details and any measurements or doses you extracted, and continue the conversation by answering the question.


### **Answer Format:**
1. **Medical Response**
- Provide a **detailed** answer, offering **further explanations** and elaborating on the information.
- The answer **must not** include special characters such as `/, ", —, *` etc.
- If the question **cannot be answered** with the provided information, simply write **"No sé."**

### **Review Process Before Answering:**
- Remove any references to "provided information."
- If the context is empty or does not contain relevant data, respond with: "No sé."
- Avoid advising the user to consult a healthcare professional unless explicitly requested.
- Respond in the **same language** as the question.
"""
    ]

    # Escoger el prompt
    prompt = prompts[1]

    # Invocar al LLM
    response = llm.invoke(prompt).content

    # Traducir la respuesta de vuelta al idioma original
    response_translated = translate_text(response, 'es')

    # Quitar triple backticks si el LLM los introdujo
    response_translated = response_translated.replace("```", "")

    # Combinar respuesta con la metadata
    final_response = response_translated + "<br><br>" + metadata_info

    return response_translated, metadata_info