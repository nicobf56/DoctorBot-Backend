import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.yaml")

def load_config():
    """Carga la configuración desde un archivo YAML."""
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config

config = load_config()

# Configuracion Azure OpenAI para LLM
AZURE_OPENAI_API_KEY = config['azure_openai']['api_key']
AZURE_OPENAI_ENDPOINT = config['azure_openai']['api_endpoint']
AZURE_OPENAI_API_VERSION = config['azure_openai']['api_version']
AZURE_OPENAI_BASE_MODEL = config['azure_openai']['base_model']
AZURE_OPENAI_DEPLOYMENT_NAME = config['azure_openai']['deployment_name']

# Configuracion Azure OpenAI para Embeddings
AZURE_OPENAI_EMBEDDINGS_KEY = config['azure_openai_embeddings']['api_key']
AZURE_OPENAI_EMBEDDINGS_ENDPOINT = config['azure_openai_embeddings']['api_endpoint']
AZURE_OPENAI_EMBEDDINGS_API_VERSION = config['azure_openai_embeddings']['api_version']
AZURE_OPENAI_EMBEDDINGS_BASE_MODEL = config['azure_openai_embeddings']['base_model']
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME = config['azure_openai_embeddings']['deployment_name']

# Configuracion Cohere para ReRank
COHERE_API_KEY = config['cohere']['api_key']
COHERE_API_BASE = config['cohere']['api_base']