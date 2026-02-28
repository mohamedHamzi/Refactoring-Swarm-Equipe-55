import json
import os
import uuid
from datetime import datetime
from enum import Enum

# Chemin du fichier de logs
LOG_FILE = os.path.join("logs", "experiment_data.json")

class ActionType(str, Enum):
    """
    Énumération des types d'actions possibles pour standardiser l'analyse.
    """
    ANALYSIS = "CODE_ANALYSIS"  # Audit, lecture, recherche de bugs
    GENERATION = "CODE_GEN"     # Création de nouveau code/tests/docs
    DEBUG = "DEBUG"             # Analyse d'erreurs d'exécution
    FIX = "FIX"                 # Application de correctifs

def log_experiment(agent_name: str, model_used: str, action: ActionType, details: dict, status: str, iteration: int = None):
    """
    Enregistre une interaction d'agent pour l'analyse scientifique.

    Args:
        agent_name (str): Nom de l'agent (ex: "Auditor", "Fixer").
        model_used (str): Modèle LLM utilisé (ex: "gemini-2.0-flash").
        action (ActionType): Le type d'action effectué (utiliser l'Enum ActionType).
        details (dict): Dictionnaire contenant les détails. DOIT contenir 'input_prompt' et 'output_response'.
        status (str): "SUCCESS" ou "FAILURE".
        iteration (int, optional): Numéro d'itération courante dans la boucle de correction.

    Raises:
        ValueError: Si les champs obligatoires sont manquants dans 'details' ou si l'action est invalide.
    """
    
    # --- 1. VALIDATION DU TYPE D'ACTION ---
    valid_actions = [a.value for a in ActionType]
    if isinstance(action, ActionType):
        action_str = action.value
    elif action in valid_actions:
        action_str = action
    else:
        raise ValueError(f"❌ Action invalide : '{action}'. Utilisez la classe ActionType (ex: ActionType.FIX).")

    # --- 2. VALIDATION STRICTE DES DONNÉES (Prompts) ---
    if action_str in [ActionType.ANALYSIS, ActionType.GENERATION, ActionType.DEBUG, ActionType.FIX]:
        required_keys = ["input_prompt", "output_response"]
        missing_keys = [key for key in required_keys if key not in details]
        
        if missing_keys:
            raise ValueError(
                f"❌ Erreur de Logging (Agent: {agent_name}) : "
                f"Les champs {missing_keys} sont manquants dans le dictionnaire 'details'. "
                f"Ils sont OBLIGATOIRES pour valider le TP."
            )

    # --- 3. PRÉPARATION DE L'ENTRÉE ---
    os.makedirs("logs", exist_ok=True)
    
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "model": model_used,
        "action": action_str,
        "iteration": iteration,
        "details": details,
        "status": status
    }

    # --- 4. LECTURE & ÉCRITURE ROBUSTE ---
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            print(f"⚠️ Attention : Le fichier de logs {LOG_FILE} était corrompu. Une nouvelle liste a été créée.")
            data = []

    data.append(entry)
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)