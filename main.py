
import os
import time
import requests
import secrets
import string

GREEN = "\033[92m"
WHITE = "\033[97m"
GRAY = "\033[90m"
RED = "\033[91m"
RESET = "\033[0m"

# Replace this with your Cloudflare Worker URL.
API_URL = "https://voidcore-ai.marexcartmsvc.workers.dev"

PROVIDERS = {
    "OpenAI - GPT": [
        "GPT-5.6 Sol", "GPT-5.6 Luna",
        "GPT-5.6 Terra", "GPT-5.6 Pro",
        "GPT-6", "GPT-6 Astra",
        "GPT-6 Reason", "GPT-6 Ultra"
    ],
    "Anthropic - Claude": [
        "Claude Opus 4.6", "Claude Sonnet 4.6",
        "Claude Haiku 4.5", "Claude Opus 5",
        "Claude Sonnet 5", "Claude Fable 5",
        "Claude Fable 5.1", "Claude Sunset 5"
    ],
    "Google - Gemini": [
        "Gemini 2.5 Pro", "Gemini 2.5 Flash",
        "Gemini 3 Pro", "Gemini 3 Flash Preview",
        "Gemini 3.1 Pro", "Gemini 3.5 Pro",
        "Gemini 3.8 Flash", "Gemini 4 Ultra"
    ],
    "xAI - Grok": [
        "Grok 3", "Grok 3 Mini", "Grok 4",
        "Grok 4 Heavy", "Grok 4.6", "Grok 5"
    ],
    "DeepSeek": [
        "DeepSeek V3", "DeepSeek R1",
        "DeepSeek V3.2", "DeepSeek V4",
        "DeepSeek V4 Pro"
    ],
    "Alibaba - Qwen": [
        "Qwen3 235B", "Qwen3 Coder",
        "Qwen3 Max", "Qwen3.5 Plus",
        "Qwen4 Ultra"
    ]
}

MODELS = [
    model
    for provider in PROVIDERS.values()
    for model in provider
]

selected_model = MODELS[0]
history = []
effort = "instant"
EFFORT_LEVELS = {"instant": 0, "medium": 2, "xhigh": 5, "max": 9, "ultra": 15}


def change_effort(command):
    global effort
    parts = command.split()
    if len(parts) == 1:
        print("Available levels: " + ", ".join(EFFORT_LEVELS))
        return
    if len(parts) != 2 or parts[1].lower() not in EFFORT_LEVELS:
        print(RED + "Usage: /effort instant|medium|xhigh|max|ultra" + RESET)
        return
    effort = parts[1].lower()
    print(GREEN + f"[OK] Effort: {effort.upper()}" + RESET)


def generate_local_key():
    """Generate a random local display identifier, not a service credential."""
    alphabet = string.ascii_letters + string.digits
    chars = "".join(secrets.choice(alphabet) for _ in range(32))
    return f"OU.{chars[:20]}-{chars[20:]}"


def show_local_key():
    print(GREEN + f"\nModel profile: {selected_model}" + RESET)
    print(WHITE + f"Local key: {generate_local_key()}" + RESET)
    print(GRAY + "Local identifier only; it cannot authenticate to any AI API." + RESET)


def loading(message):
    print(GREEN + message, end="", flush=True)

    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)

    print(" [OK]" + RESET)


def banner():
    os.system("cls" if os.name == "nt" else "clear")

    print(GREEN + r"""
 __     __  ___   ___  ____   ____ ___  ____  _____
 \ \   / / / _ \ |_ _||  _ \ / ___/ _ \|  _ \| ____|
  \ \ / / | | | | | | | | | | |  | | | | | |_) |  _|
   \ V /  | |_| | | | | |_| | |__| |_| |  _ <| |___
    \_/    \___/ |___||____/ \____\___/|_| \_\_____|

                 A I   T E R M I N A L
    """ + RESET)

    print(GRAY + "VOIDCORE AI v1.0")
    print("40 AI Profiles | 6 Providers")
    print("Type /help for available commands.\n" + RESET)


def show_models():
    number = 1

    for provider, models in PROVIDERS.items():
        print(GREEN + "\n" + provider + RESET)

        for model in models:
            print(f"  [{number}] {model}")
            number += 1


def change_model():
    global selected_model

    show_models()

    choice = input(
        GREEN + "\nSelect model number > " + RESET
    ).strip()

    if not choice.isdigit():
        print(RED + "Invalid selection." + RESET)
        return

    index = int(choice) - 1

    if not 0 <= index < len(MODELS):
        print(RED + "Model not found." + RESET)
        return

    selected_model = MODELS[index]

    loading("Initializing AI profile")

    print(
        GREEN
        + f"\n[OK] {selected_model} selected.\n"
        + RESET
    )


def ask_ai(message):
    global history

    if "YOUR-WORKER" in API_URL:
        return (
            "The AI server has not been configured yet. "
            "Set your Cloudflare Worker URL in main.py."
        )

    history.append({
        "role": "user",
        "content": message
    })

    try:
        response = requests.post(
            API_URL,
            json={
                "message": message,
                "profile": selected_model,
                "history": history[-20:],
                "effort": effort
            },
            timeout=90
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get("response", "")

        if not answer:
            raise ValueError("Empty AI response.")

        history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except (requests.RequestException, ValueError) as error:
        history.pop()
        return f"Connection error: {error}"


def main():
    global history

    os.system("")

    banner()

    loading("Initializing VOIDCORE AI")
    loading("Loading AI profiles")
    loading("Connecting to AI server")

    print(
        GREEN
        + f"\n[OK] {selected_model} selected."
        + RESET
    )

    while True:
        try:
            message = input(
                GREEN + "\nYou > " + RESET
            ).strip()

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not message:
            continue

        command = message.lower()

        if command == "/exit":
            print(GREEN + "Goodbye!" + RESET)
            break

        elif command == "/help":
            print("""
Available commands:

/help    - Show commands
/models  - Show AI profiles
/model   - Change AI profile
/effort  - Select response effort (instant, medium, xhigh, max, ultra)
/about   - Show actual backend and profile details
/api     - Generate a new local display key
/clear   - Clear terminal
/exit    - Exit VOIDCORE AI
""")

        elif command == "/effort" or command.startswith("/effort "):
            change_effort(command)

        elif command == "/api":
            show_local_key()

        elif command == "/about":
            print(f"Selected display profile: {selected_model}\nActual backend: Gemini via Cloudflare Worker\nEffort: {effort.upper()}")

        elif command == "/models":
            show_models()

        elif command == "/model":
            change_model()
            history = []

        elif command == "/clear":
            banner()

        elif command.startswith("/"):
            print(RED + "Unknown command." + RESET)

        else:
            start = time.perf_counter()
            print(GRAY + f"\nGenerating [{effort.upper()}]..." + RESET)
            answer = ask_ai(message)
            elapsed = time.perf_counter() - start
            if not answer.startswith("Connection error:"):
                time.sleep(max(0, EFFORT_LEVELS[effort] - elapsed))
            print(GRAY + f"Elapsed: {time.perf_counter() - start:.1f}s (includes optional display delay)\n" + RESET)

            print(
                GREEN
                + f"{selected_model} > "
                + WHITE
                + answer
                + RESET
            )


if __name__ == "__main__":
    main()
