import os
from flask import Flask, jsonify

# Initialisation de l'application Flask
app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello_world():
    """
    Point de terminaison /hello qui renvoie un message JSON.
    """
    # jsonify prépare la réponse au format JSON avec le bon Content-Type
    return jsonify(message="Bonjour, monde du serverless!")

if __name__ == "__main__":
    # Récupère le port depuis la variable d'environnement PORT
    # (utilisé par Cloud Run/Container Apps) ou utilise 8080 par défaut.
    port = int(os.environ.get('PORT', 8080))
    
    # Exécute l'application
    # host='0.0.0.0' est crucial pour que le serveur soit visible 
    # à l'extérieur du conteneur Docker.
    app.run(host='0.0.0.0', port=port, debug=True)
