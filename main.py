
import os
import time
import json
import secrets
import string
import urllib.request
import urllib.error

# ==========================================
# VOIDCORE AI - TERMINAL
# ==========================================

VERSION = "2.1"

WORKER_URL = os.environ.get(
    "VOIDCORE_WORKER_URL",
    "https://voidcore-ai.marexcartmsvc.workers.dev"
)

# ==========================================
# COLORS
# ==========================================

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GRAY = "\033[90m"
RESET = "\033[0m"

if os.name == "nt":
    os.system("")

# ==========================================
# MODELS - NEPROMENJENO
# ==========================================

MODELS = [
    # OpenAI — GPT
    "GPT-5.6 Sol",
    "GPT-5.6 Luna",
    "GPT-5.6 Terra",
    "GPT-6 Astra",

    # Anthropic — Claude
    "Claude Opus 4.6",
    "Claude Sonnet 4.6",
    "Claude Haiku 4.5",
    "Claude Opus 5",
    "Claude Sonnet 5",
    "Claude Fable 5",
    "Claude Fable 5.1",

    # Google — Gemini
    "Gemini 2.5 Pro",
    "Gemini 2.5 Flash",
    "Gemini 3 Pro",
    "Gemini 3 Flash Preview",
    "Gemini 3.1 Pro",
    "Gemini 3.5 Pro",
    "Gemini 3.8 Flash",
    "Gemini 4 Ultra",

    # xAI — Grok
    "Grok 3",
    "Grok 3 Mini",
    "Grok 4",
    "Grok 4 Heavy",
    "Grok 4.6",
    "Grok 5",

    # DeepSeek
    "DeepSeek V3",
    "DeepSeek R1",
    "DeepSeek V3.2",
    "DeepSeek V4",
    "DeepSeek V4 Pro",

    # Alibaba — Qwen
    "Qwen3 235B",
    "Qwen3 Coder",
    "Qwen3 Max",
    "Qwen3.5 Plus",
    "Qwen4 Ultra"
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
# LOCAL IDENTIFIER GENERATOR
# ==========================================

def generate_api_key():
    chars = string.ascii_letters + string.digits

    part1 = "".join(
        secrets.choice(chars) for _ in range(20)
    )

    part2 = "".join(
        secrets.choice(chars) for _ in range(8)
    )

    identifier = f"OU.{part1}-{part2}"

    print()
    print(GREEN + "Generating identifier... [OK]" + RESET)
    print()
    print("Model: " + selected_model)
    print("Identifier: " + identifier)
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
        GREEN + f"[OK] {selected_model} selected." + RESET
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
        GREEN + f"[OK] Effort set to {effort.upper()}" + RESET
    )
    print()


# ==========================================
# AI REQUEST
# ==========================================

def ask_ai(message):
    global history

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
            "Content-Type": "application/json",
            "User-Agent": "curl/8.0.0",
            "Accept": "*/*"
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
        details = error.read().decode(
            "utf-8",
            errors="replace"
        )

        return (
            f"Connection error: HTTP {error.code}\n"
            f"{details[:1000]}"
        )

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
        GRAY + f"Thinking [{effort.upper()}]..." + RESET
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
        GRAY + f"Completed in {elapsed:.1f}s" + RESET
    )

    print()
    print(
        GREEN + selected_model + " > " + RESET + answer
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
    print("AI connection: Cloudflare Worker")
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
        GREEN + "Initializing VOIDCORE AI... [OK]" + RESET
    )

    time.sleep(0.3)
    print(
        GREEN + "Loading AI profiles... [OK]" + RESET
    )

    time.sleep(0.3)
    print(
        GREEN + "Loading terminal... [OK]" + RESET
    )

    print()
    print(
        GREEN + f"[OK] {selected_model} selected." + RESET
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

        if command in ("api", "/api"):
            generate_api_key()

        elif command in ("/models", "models"):
            show_models()

        elif command in ("/model", "model"):
            change_model(value)

        elif command in ("/effort", "effort"):
            change_effort(value)

        elif command in ("/about", "about"):
            show_about()

        elif command in ("/help", "help"):
            show_help()

        elif command in ("/clear", "clear"):
            os.system(
                "cls" if os.name == "nt" else "clear"
            )

        elif command in ("/reset", "reset"):
            history = []
            print(
                GREEN + "[OK] Conversation reset." + RESET
            )

        elif command in ("/exit", "exit", "quit"):
            print("\nExiting VOIDCORE AI...")
            break

        else:
            generate_response(message)


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
