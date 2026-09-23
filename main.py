
import os
import time
import requests

GREEN = "\033[92m"
WHITE = "\033[97m"
GRAY = "\033[90m"
RED = "\033[91m"
RESET = "\033[0m"

# Replace this with your Cloudflare Worker URL.
API_URL = "https://YOUR-WORKER.workers.dev"

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
                "history": history[-20:]
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
/clear   - Clear terminal
/exit    - Exit VOIDCORE AI
""")

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
            print(
                GRAY + "\nGenerating response...\n" + RESET
            )

            answer = ask_ai(message)

            print(
                GREEN
                + f"{selected_model} > "
                + WHITE
                + answer
                + RESET
            )


if __name__ == "__main__":
    main()
