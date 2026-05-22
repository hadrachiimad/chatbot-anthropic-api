# Projet Chatbot — Rapport

---

## 1. Introduction

Ce projet consiste à créer un chatbot conversationnel en Python utilisant l'API Anthropic (Claude) comme modèle de langage. Le chatbot fonctionne dans le terminal et offre plusieurs fonctionnalités au-delà du simple envoi de prompt : gestion de l'historique de conversation, personnalisation du comportement, et streaming des réponses en temps réel.

## 2. Choix techniques

### Pourquoi l'API Anthropic (Claude) ?

Parmi les options disponibles (Ollama en local, OpenAI, HuggingFace), j'ai choisi l'API Anthropic pour plusieurs raisons :

- **Qualité des réponses** : Claude est reconnu pour ses réponses nuancées et sa capacité à suivre des instructions complexes.
- **SDK Python officiel** : Le package `anthropic` offre une intégration simple et bien documentée.
- **Streaming natif** : Le SDK supporte le streaming des réponses, améliorant l'expérience utilisateur.
- **Gestion du contexte** : L'API gère nativement les conversations multi-tours via un tableau de messages.

### Architecture du code

Le script est organisé autour d'une classe `Chatbot` qui encapsule toute la logique :

```
chatbot.py
├── Configuration (modèle, tokens, personnalités)
├── Classe Chatbot
│   ├── __init__()        → Connexion API + état initial
│   ├── send_message()    → Envoi avec historique
│   ├── _stream_response()→ Réponse en temps réel
│   ├── reset()           → RAZ de la conversation
│   └── set_system_prompt()→ Changement de personnalité
├── Commandes (/help, /reset, /persona, /system, /history, /quit)
└── main()                → Boucle interactive
```

### Librairies utilisées

| Librairie   | Rôle                               |
| ----------- | ---------------------------------- |
| `anthropic` | SDK officiel pour l'API Claude     |
| `os`, `sys` | Variables d'environnement, système |

Le choix de se limiter à la librairie standard + SDK Anthropic rend le projet simple à installer et exécuter.

## 3. Concepts clés implémentés

### 3.1 Historique de conversation

Le concept fondamental pour qu'un LLM "se souvienne" du contexte est de lui renvoyer l'ensemble des messages précédents à chaque requête. L'API Anthropic attend un paramètre `messages` sous forme de liste :

```python
messages = [
    {"role": "user", "content": "Bonjour, je m'appelle Alice."},
    {"role": "assistant", "content": "Bonjour Alice ! Comment puis-je t'aider ?"},
    {"role": "user", "content": "Tu te souviens de mon prénom ?"},
]
```

Le modèle n'a pas de mémoire propre : c'est le code client qui gère l'historique et le renvoie intégralement. C'est pourquoi la commande `/reset` vide simplement cette liste.

### 3.2 Prompt système (System Prompt)

Le prompt système est une instruction envoyée au modèle _avant_ la conversation. Il définit le comportement, le ton et le rôle du chatbot. Par exemple :

- **Mode assistant** : réponses claires et pédagogiques
- **Mode pirate** : réponses amusantes avec du vocabulaire de pirate
- **Mode prof** : guide l'utilisateur par des questions socratiques

Cela illustre le concept de _prompt engineering_ : la qualité du prompt système influence directement la pertinence des réponses.

### 3.3 Streaming

Sans streaming, l'utilisateur attend que toute la réponse soit générée avant de voir quoi que ce soit. Avec le streaming, les mots apparaissent au fur et à mesure, comme une conversation naturelle. Le SDK Anthropic fournit cette fonctionnalité via `client.messages.stream()`.

## 4. Installation et utilisation

### Prérequis

- Python 3.9 ou supérieur
- Une clé API Anthropic (disponible sur https://console.anthropic.com)

### Installation

```bash
pip install anthropic
```

### Lancement

```bash
# Définir la clé API
export ANTHROPIC_API_KEY="sk-ant-..."

# Lancer le chatbot
python chatbot.py
```

Le programme demande la clé API interactivement si la variable d'environnement n'est pas définie.

## 5. Exemples d'interactions

### Exemple 1 — Conversation simple avec mémoire

```
👤 Vous : Salut ! Je suis étudiant en B2 informatique.
🤖 Claude : Salut ! Bienvenue, c'est super que tu sois en B2 informatique.
   Sur quoi est-ce que tu travailles en ce moment ?

👤 Vous : Je travaille sur un projet de chatbot justement.
🤖 Claude : Ha, un projet de chatbot en B2, c'est un excellent exercice !
   Tu utilises quelle approche ? API distante ou modèle en local ?

👤 Vous : Tu te souviens de mon niveau d'études ?
🤖 Claude : Bien sûr, tu m'as dit que tu es étudiant en B2 informatique.
   C'est grâce à l'historique de notre conversation que je m'en souviens.
```

→ Le modèle "se souvient" car tout l'historique est renvoyé à chaque requête.

### Exemple 2 — Changement de personnalité

```
👤 Vous : /persona
🎭 Personnalités disponibles :
  1. assistant    → Tu es un assistant amical et pédagogue...
  2. pirate       → Tu es un pirate des Caraïbes qui répond...
  3. prof         → Tu es un professeur d'université bienveil...
  4. coach        → Tu es un coach de vie enthousiaste...

Votre choix : 2
✅ Personnalité 'pirate' activée !

👤 Vous : Explique-moi ce qu'est une API.
🤖 Claude : Arrr, moussaillon ! Une API, c'est comme une carte au trésor
   entre deux navires ! Mille sabords, laisse-moi t'expliquer...
```

### Exemple 3 — Commandes utiles

```
👤 Vous : /history       → Affiche tous les messages échangés
👤 Vous : /reset         → Efface l'historique et recommence à zéro
👤 Vous : /system        → Permet d'écrire un prompt système personnalisé
👤 Vous : /quit          → Quitte le programme
```

## 6. Différences entre local et API distante

| Critère         | API distante (Anthropic)    | Local (Ollama)                 |
| --------------- | --------------------------- | ------------------------------ |
| Installation    | Clé API uniquement          | Télécharger un modèle (~4 Go+) |
| Qualité         | Modèles très performants    | Variable selon le modèle       |
| Coût            | Payant à l'usage            | Gratuit après installation     |
| Confidentialité | Données envoyées au serveur | Tout reste sur la machine      |
| Vitesse         | Dépend de la connexion      | Dépend du matériel (GPU)       |
| Disponibilité   | Nécessite internet          | Fonctionne hors-ligne          |

## 7. Pistes d'amélioration

- **Interface web** : utiliser Flask ou Streamlit pour une UI graphique
- **RAG** (Retrieval-Augmented Generation) : connecter le chatbot à des documents locaux
- **Sauvegarde** : exporter/importer les conversations en JSON
- **Multi-modèles** : comparer les réponses de différents LLM
- **Fine-tuning** : adapter un modèle à un domaine spécifique

## 8. Conclusion

Ce projet montre qu'il est possible de construire un chatbot fonctionnel et personnalisable en moins de 200 lignes de Python. Les concepts clés — historique de conversation, prompt système, streaming — sont les briques fondamentales que l'on retrouve dans tous les assistants IA modernes. L'API Anthropic offre un accès simple et puissant à ces fonctionnalités.
