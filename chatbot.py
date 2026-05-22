"""
Chatbot conversationnel utilisant l'API Anthropic (Claude)
===========================================================


Fonctionnalités :
- Conversation interactive dans le terminal
- Historique des messages (contexte conservé)
- Personnalisation du comportement (rôle, ton, contexte)
- Streaming des réponses en temps réel
- Commandes spéciales (/help, /reset, /system, /history, /quit)
"""

import os
import sys

# --- Installation automatique du SDK si nécessaire ---
try:
    import anthropic
except ImportError:
    print("📦 Installation du SDK Anthropic...")
    os.system(f"{sys.executable} -m pip install anthropic --quiet")
    import anthropic


# ============================================================
# CONFIGURATION
# ============================================================

# Modèle à utiliser (claude-sonnet-4-20250514 est un bon rapport qualité/coût)
MODEL = "claude-sonnet-4-20250514"

# Nombre max de tokens dans la réponse
MAX_TOKENS = 1024

# Prompt système par défaut (personnalité du chatbot)
DEFAULT_SYSTEM_PROMPT = (
    "Tu es un assistant amical et pédagogue. "
    "Tu réponds en français de manière claire et concise. "
    "Tu utilises des exemples concrets quand c'est utile. "
    "Si tu ne sais pas quelque chose, tu le dis honnêtement."
)

# Quelques personnalités pré-définies
PERSONALITIES = {
    "assistant": (
        "Tu es un assistant amical et pédagogue. "
        "Tu réponds en français de manière claire et concise."
    ),
    "pirate": (
        "Tu es un pirate des Caraïbes qui répond toujours en français. "
        "Tu ponctues tes phrases de 'Arrr!', 'Mille sabords!' et autres expressions pirates. "
        "Tu restes utile malgré ton personnage."
    ),
    "prof": (
        "Tu es un professeur d'université bienveillant et exigeant. "
        "Tu guides l'étudiant avec des questions socratiques plutôt que des réponses directes. "
        "Tu encourages la réflexion critique. Tu réponds en français."
    ),
    "coach": (
        "Tu es un coach de vie enthousiaste et motivant. "
        "Tu encourages l'utilisateur et donnes des conseils pratiques et actionnables. "
        "Tu réponds en français avec énergie et positivité."
    ),
}


# ============================================================
# CLASSE CHATBOT
# ============================================================

class Chatbot:
    """Chatbot conversationnel avec historique et personnalisation."""

    def __init__(self, api_key: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        """
        Initialise le chatbot.

        Args:
            api_key: Clé API Anthropic
            system_prompt: Prompt système définissant le comportement
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt = system_prompt
        self.conversation_history: list[dict] = []
        self.model = MODEL

    def reset(self):
        """Remet à zéro l'historique de conversation."""
        self.conversation_history = []
        print("🔄 Conversation réinitialisée.\n")

    def set_system_prompt(self, prompt: str):
        """Change le prompt système (personnalité du bot)."""
        self.system_prompt = prompt
        self.reset()
        print(f"🎭 Nouveau comportement défini.\n")

    def send_message(self, user_message: str, stream: bool = True) -> str:
        """
        Envoie un message et retourne la réponse du modèle.

        Args:
            user_message: Le message de l'utilisateur
            stream: Si True, affiche la réponse en temps réel

        Returns:
            La réponse complète du modèle
        """
        # Ajouter le message utilisateur à l'historique
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        if stream:
            response_text = self._stream_response()
        else:
            response_text = self._simple_response()

        # Ajouter la réponse à l'historique
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text,
        })

        return response_text

    def _simple_response(self) -> str:
        """Envoie la requête et retourne la réponse complète (sans streaming)."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=self.system_prompt,
            messages=self.conversation_history,
        )
        text = response.content[0].text
        print(f"\n🤖 Claude : {text}\n")
        return text

    def _stream_response(self) -> str:
        """Envoie la requête et affiche la réponse au fur et à mesure (streaming)."""
        print("\n🤖 Claude : ", end="", flush=True)

        full_response = ""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=self.system_prompt,
            messages=self.conversation_history,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text

        print("\n")
        return full_response

    def show_history(self):
        """Affiche l'historique de la conversation."""
        if not self.conversation_history:
            print("📭 Aucun message dans l'historique.\n")
            return

        print("\n" + "=" * 50)
        print("📜 HISTORIQUE DE CONVERSATION")
        print("=" * 50)
        for msg in self.conversation_history:
            role = "👤 Vous" if msg["role"] == "user" else "🤖 Claude"
            content = msg["content"]
            # Tronquer les messages longs pour l'affichage
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"\n{role} :\n{content}")
        print("\n" + "=" * 50 + "\n")


# ============================================================
# COMMANDES ET INTERFACE TERMINAL
# ============================================================

def print_help():
    """Affiche l'aide des commandes disponibles."""
    print("""
╔══════════════════════════════════════════════════╗
║              📋 COMMANDES DISPONIBLES            ║
╠══════════════════════════════════════════════════╣
║  /help        Afficher cette aide                ║
║  /reset       Réinitialiser la conversation      ║
║  /system      Changer le prompt système          ║
║  /persona     Choisir une personnalité           ║
║  /history     Voir l'historique des messages      ║
║  /quit        Quitter le chatbot                 ║
╚══════════════════════════════════════════════════╝
    """)


def choose_persona(bot: Chatbot):
    """Permet à l'utilisateur de choisir une personnalité prédéfinie."""
    print("\n🎭 Personnalités disponibles :")
    for i, (name, desc) in enumerate(PERSONALITIES.items(), 1):
        preview = desc[:70] + "..." if len(desc) > 70 else desc
        print(f"  {i}. {name:12s} → {preview}")

    choice = input("\nVotre choix (nom ou numéro) : ").strip().lower()

    # Accepter un numéro ou un nom
    names = list(PERSONALITIES.keys())
    if choice.isdigit() and 1 <= int(choice) <= len(names):
        choice = names[int(choice) - 1]

    if choice in PERSONALITIES:
        bot.set_system_prompt(PERSONALITIES[choice])
        print(f"✅ Personnalité '{choice}' activée !")
    else:
        print("❌ Choix invalide.")
    print()


def handle_command(command: str, bot: Chatbot) -> bool:
    """
    Gère les commandes spéciales.

    Returns:
        True si le programme doit continuer, False pour quitter.
    """
    cmd = command.strip().lower()

    if cmd == "/quit":
        print("👋 Au revoir !")
        return False
    elif cmd == "/help":
        print_help()
    elif cmd == "/reset":
        bot.reset()
    elif cmd == "/history":
        bot.show_history()
    elif cmd == "/persona":
        choose_persona(bot)
    elif cmd == "/system":
        print(f"\n📝 Prompt actuel :\n{bot.system_prompt}\n")
        new_prompt = input("Nouveau prompt système (vide = annuler) : ").strip()
        if new_prompt:
            bot.set_system_prompt(new_prompt)
    else:
        print(f"❌ Commande inconnue : {cmd}. Tapez /help pour l'aide.\n")

    return True


# ============================================================
# POINT D'ENTRÉE
# ============================================================

def main():
    """Fonction principale : lance le chatbot interactif."""

    print("""
╔══════════════════════════════════════════════════╗
║        🤖 CHATBOT CLAUDE — NEXA B2 2026         ║
║                                                  ║
║  Tapez votre message pour commencer.             ║
║  Tapez /help pour voir les commandes.            ║
╚══════════════════════════════════════════════════╝
    """)

    # --- Récupération de la clé API ---
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("⚠️  Variable d'environnement ANTHROPIC_API_KEY non trouvée.")
        api_key = input("Entrez votre clé API Anthropic : ").strip()
        if not api_key:
            print("❌ Clé API requise. Quittez et définissez ANTHROPIC_API_KEY.")
            sys.exit(1)

    # --- Initialisation du chatbot ---
    bot = Chatbot(api_key=api_key)
    print("✅ Chatbot initialisé ! Bonne conversation.\n")

    # --- Boucle de conversation ---
    while True:
        try:
            user_input = input("👤 Vous : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Au revoir !")
            break

        if not user_input:
            continue

        # Vérifier si c'est une commande
        if user_input.startswith("/"):
            if not handle_command(user_input, bot):
                break
            continue

        # Envoyer le message au LLM
        try:
            bot.send_message(user_input, stream=True)
        except anthropic.AuthenticationError:
            print("❌ Clé API invalide. Vérifiez votre ANTHROPIC_API_KEY.\n")
        except anthropic.RateLimitError:
            print("⏳ Limite de requêtes atteinte. Attendez un moment.\n")
        except anthropic.APIError as e:
            print(f"❌ Erreur API : {e}\n")
        except Exception as e:
            print(f"❌ Erreur inattendue : {e}\n")


if __name__ == "__main__":
    main()
