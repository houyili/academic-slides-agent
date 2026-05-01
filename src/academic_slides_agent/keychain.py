"""macOS Keychain integration for API key management.

On macOS, keys are stored in the system Keychain via the `keyring` library.
On other platforms, keyring uses the platform's native credential store
(e.g., Windows Credential Locker, GNOME Keyring / KDE Wallet on Linux).
Falls back to .env file if keyring is unavailable.
"""

import os
import sys

SERVICE_NAME = "academic-slides-agent"

try:
    import keyring
    _HAS_KEYRING = True
except ImportError:
    _HAS_KEYRING = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def store_api_key(provider: str, key: str) -> None:
    """Store an API key in the system keychain.

    Args:
        provider: Key identifier, e.g. 'openai', 'anthropic'.
        key: The API key value.
    """
    if not _HAS_KEYRING:
        print("⚠️  keyring not installed. Run: pip install keyring")
        print(f"   Falling back to env var: export {_env_var(provider)}=<key>")
        return
    keyring.set_password(SERVICE_NAME, provider, key)
    print(f"✅ API key for '{provider}' stored in system keychain.")


def get_api_key(provider, default=None):
    """Retrieve an API key. Priority: keychain → env var → None.

    Args:
        provider: Key identifier, e.g. 'openai', 'anthropic'.

    Returns:
        The API key string, or None if not found.
    """
    # 1. Try keychain
    if _HAS_KEYRING:
        key = keyring.get_password(SERVICE_NAME, provider)
        if key:
            return key

    # 2. Try environment variable
    env_key = os.environ.get(_env_var(provider))
    if env_key:
        return env_key

    return None


def delete_api_key(provider: str) -> None:
    """Remove an API key from the system keychain."""
    if _HAS_KEYRING:
        try:
            keyring.delete_password(SERVICE_NAME, provider)
            print(f"✅ API key for '{provider}' removed from keychain.")
        except keyring.errors.PasswordDeleteError:
            print(f"⚠️  No key found for '{provider}' in keychain.")


def _env_var(provider: str) -> str:
    """Map provider name to environment variable name."""
    return f"{provider.upper()}_API_KEY"


def interactive_setup() -> None:
    """Interactive prompt to store API keys in the keychain."""
    import getpass

    print("\n🔑 Academic Slides Agent — API Key Setup")
    print("=" * 50)
    print("Keys will be stored in your system's secure credential store.")
    print("(macOS: Keychain, Linux: Secret Service, Windows: Credential Locker)\n")

    providers = [
        ("openai", "OpenAI API Key (for GPT-4o)"),
        ("anthropic", "Anthropic API Key (for Claude)"),
    ]

    for provider, desc in providers:
        existing = get_api_key(provider)
        status = "✅ configured" if existing else "❌ not set"
        print(f"  {desc}: {status}")

        if existing:
            overwrite = input(f"  Overwrite {provider} key? [y/N]: ").strip().lower()
            if overwrite != "y":
                continue

        key = getpass.getpass(f"  Enter {provider} API key (or press Enter to skip): ")
        if key.strip():
            store_api_key(provider, key.strip())

    print("\n✅ Setup complete. Keys are stored securely.\n")
