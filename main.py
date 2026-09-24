
import os
import sys
import time
import json
import secrets
import string
import urllib.request
import urllib.error

# ==========================================
# VOIDCORE AI - TERMINAL
# ==========================================

VERSION = "2.0"

# Ovde upisi adresu svog Cloudflare Worker-a.
WORKER_URL = os.environ.get(
    "VOIDCORE_WORKER_URL",
    "https://YOUR-WORKER.workers.dev"
)

# ==========================================
# COLORS
# ==========================================

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GRAY = "\033[90m"
WHITE = "\033[97m"
RESET = "\033[0m"

if os.name == "nt":
    os.system("")

# ==========================================
# MODELS
# ==========================================

MODELS = [
    "GPT-5.6 Sol",
    "GPT-5.6 Luna",
    "Astra X",
    "Claude Fable 5.1",
    "Gemini 3.8",
    "Grok",
    "NovaAI"
]

selected_model = MODELS[0]

# ==========================================
# EFFORT
# ==========================================

EFFORT_LEVELS = {
    "instant": 0,
    "medium": 3,
    "xhigh": 8,
    "max": 15,
    "ultra": 30
}

effort = "instant"

# ==========================================
# HISTORY
# ==========================================

history = []

# ==========================================
# API IDENTIFIER GENERATOR
# ==========================================

def generate_api_key():
    chars = string.ascii_letters + string.digits

    part1 = "".join(
        secrets.choice(chars) for _ in range(20)
    )

    part2 = "".join(
        secrets.choice(chars) for _ in range(8)
    )

    key = f"OU.{part1}-{part2}"

    print()
    print(
        GREEN +
        "Generating API key... [OK]" +
        RESET
    )

    print()
    print("Model: " + selected_model)
    print("API Key: " + key)
    print()


# ==========================================
# MODEL SELECTOR
# ==========================================

def show_models():
    print()
    print(CYAN + "AVAILABLE AI PROFILES" + RESET)
    print("-" * 35)

    for index, model in enumerate(MODELS, 1):
        marker = " [SELECTED]" if model == selected_model else ""
        print(f"{index}. {model}{marker}")

    print()


def change_model(value):
    global selected_model

    if not value:
        show_models()
        return

    try:
        index = int(value) - 1

        if index < 0 or index >= len(MODELS):
            raise ValueError()

        selected_model = MODELS[index]

    except ValueError:
        matches = [
            model for model in MODELS
            if model.lower() == value.lower()
        ]

        if not matches:
            print(RED + "Model not found." + RESET)
            return

        selected_model = matches[0]

    print()
    print(
        GREEN +
        f"[OK] {selected_model} selected." +
        RESET
    )
    print()


# ==========================================
# EFFORT SELECTOR
# ==========================================

def show_effort():
    print()
    print(CYAN + "REASONING EFFORT" + RESET)
    print("-" * 35)

    for level in EFFORT_LEVELS:
        marker = " [SELECTED]" if level == effort else ""
        print(f"{level.upper()}{marker}")

    print()


def change_effort(value):
    global effort

    if not value:
        show_effort()
        return

    value = value.lower()

    if value not in EFFORT_LEVELS:
        print(RED + "Invalid effort level." + RESET)
        show_effort()
        return

    effort = value

    print()
    print(
        GREEN +
        f"[OK] Effort set to {effort.upper()}" +
        RESET
    )
    print()


# ==========================================
# AI REQUEST
# ==========================================

def ask_ai(message):
    global history

    if "YOUR-WORKER" in WORKER_URL:
        return (
            "Connection error: Configure "
            "VOIDCORE_WORKER_URL first."
        )

    payload = {
        "message": message,
        "model": selected_model,
        "effort": effort,
        "history": history[-20:]
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        WORKER_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        answer = (
            result.get("reply")
            or result.get("response")
            or result.get("answer")
            or result.get("text")
        )

        if not answer:
            return "Error: Empty AI response."

        history.append({
            "role": "user",
            "content": message
        })

        history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except urllib.error.HTTPError as error:
        return f"Connection error: HTTP {error.code}"

    except urllib.error.URLError as error:
        return f"Connection error: {error.reason}"

    except Exception as error:
        return f"Connection error: {error}"


# ==========================================
# THINKING DISPLAY
# ==========================================

def generate_response(message):
    print()

    start = time.perf_counter()

    print(
        GRAY +
        f"Thinking [{effort.upper()}]..." +
        RESET
    )

    answer = ask_ai(message)

    elapsed = time.perf_counter() - start

    minimum = EFFORT_LEVELS[effort]

    if (
        elapsed < minimum
        and not answer.startswith("Connection error:")
    ):
        time.sleep(minimum - elapsed)

    elapsed = time.perf_counter() - start

    print(
        GRAY +
        f"Completed in {elapsed:.1f}s" +
        RESET
    )

    print()
    print(
        GREEN +
        selected_model +
        " > " +
        RESET +
        answer
    )
    print()


# ==========================================
# HELP
# ==========================================

def show_help():
    print()
    print(CYAN + "VOIDCORE AI COMMANDS" + RESET)
    print("-" * 40)

    print("/models          Show AI profiles")
    print("/model NUMBER    Select AI profile")
    print("/effort          Show effort levels")
    print("/effort LEVEL    Change effort")
    print("/api             Generate local identifier")
    print("api              Generate local identifier")
    print("/about           Show terminal information")
    print("/clear           Clear terminal")
    print("/reset           Clear conversation history")
    print("/help            Show commands")
    print("/exit            Exit terminal")

    print()


# ==========================================
# ABOUT
# ==========================================

def show_about():
    print()
    print(CYAN + "VOIDCORE AI" + RESET)
    print(f"Version: {VERSION}")
    print(f"Selected profile: {selected_model}")
    print(f"Effort: {effort.upper()}")

    print(
        "AI provider: Configured through "
        "Cloudflare Worker"
    )

    print(
        "API identifiers generated locally "
        "do not authenticate to AI services."
    )

    print()


# ==========================================
# STARTUP
# ==========================================

def startup():
    print()
    print(GREEN + "VOIDCORE AI" + RESET)
    print("=" * 40)

    print("Type /help for available commands.")
    print()

    time.sleep(0.3)

    print(
        GREEN +
        "Initializing VOIDCORE AI... [OK]" +
        RESET
    )

    time.sleep(0.3)

    print(
        GREEN +
        "Loading AI profiles... [OK]" +
        RESET
    )

    time.sleep(0.3)

    print(
        GREEN +
        "Loading terminal... [OK]" +
        RESET
    )

    print()
    print(
        GREEN +
        f"[OK] {selected_model} selected." +
        RESET
    )

    print()


# ==========================================
# MAIN LOOP
# ==========================================

def main():
    global history

    startup()

    while True:

        try:
            message = input(
                GREEN + "You > " + RESET
            ).strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting VOIDCORE AI...")
            break

        if not message:
            continue

        parts = message.split(maxsplit=1)

        command = parts[0].lower()

        value = (
            parts[1].strip()
            if len(parts) > 1
            else ""
        )

        # API identifier command
        if command in ("api", "/api"):
            generate_api_key()

        # Model commands
        elif command in ("/models", "models"):
            show_models()

        elif command in ("/model", "model"):
            change_model(value)

        # Effort commands
        elif command in ("/effort", "effort"):
            change_effort(value)

        # About
        elif command in ("/about", "about"):
            show_about()

        # Help
        elif command in ("/help", "help"):
            show_help()

        # Clear screen
        elif command in ("/clear", "clear"):
            os.system(
                "cls" if os.name == "nt" else "clear"
            )

        # Reset conversation
        elif command in ("/reset", "reset"):
            history = []

            print(
                GREEN +
                "[OK] Conversation reset." +
                RESET
            )

        # Exit
        elif command in ("/exit", "exit", "quit"):
            print("\nExiting VOIDCORE AI...")
            break

        # Normal AI message
        else:
            generate_response(message)


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
