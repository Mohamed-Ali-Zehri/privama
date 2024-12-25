import requests
import json

class LLMHandler:
    def __init__(self):
        self.api_url = "http://localhost:11434"  # Remplacez avec l'URL correcte

    def generate_response(self, prompt):
        payload = {
            "model": "llama2",  # Remplacez par le modèle correct
            "prompt": prompt
        }
        response = requests.post(f"{self.api_url}/api/generate", json=payload, stream=True)
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse chaque objet JSON dans le flux
                        line_json = json.loads(line.decode('utf-8'))
                        full_response += line_json.get('response', '')
                        # Arrêter si la réponse est terminée
                        if line_json.get('done', False):
                            break
                    except json.JSONDecodeError as e:
                        print(f"Erreur de déchiffrage JSON : {e}")
            return full_response
        else:
            return f"Erreur : {response.status_code} - {response.text}"

# Exemple d'utilisation
if __name__ == "__main__":
    llm_handler = LLMHandler()
    prompt = "Describe the process of Linux privilege escalation."
    response = llm_handler.generate_response(prompt)
    print(response)
