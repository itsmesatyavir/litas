import requests
import uuid
import random
import string
import time

# User input for base URL and invite code
base_url = input("> Input base URL: ").strip()
invite_by = input("> Enter invite code: ").strip()

# Extended list of mobile User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.199 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.143 Mobile Safari/537.36"
]

def load_proxies():
    """Load proxies from proxies.txt."""
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except FileNotFoundError:
        print("proxies.txt not found. Please create the file and add proxies.")
        return []

def get_random_proxy(proxies):
    """Select a random proxy from the list."""
    if proxies:
        proxy = random.choice(proxies)
        return {"http": proxy, "https": proxy}
    return None

def generate_random_username(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def generate_random_email():
    return f"{generate_random_username()}@gmail.com"

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def get_captcha():
    """Retrieve a CAPTCHA token from the given base URL."""
    global base_url
    while True:
        token = requests.get(f"{base_url}/get").text
        if token != "No tokens available":
            return token
        time.sleep(0.3)

def get_antiforgery_token(invite_by, proxies):
    url = f'https://wallet.litas.io/api/v1/antiforgery/token'
    headers = {
        'Accept': 'application/json',
        'Referer': f'https://wallet.litas.io/invite/{invite_by}',
        'User-Agent': random.choice(USER_AGENTS)
    }
    
    proxy = get_random_proxy(proxies)
    
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('token'), response.cookies
        else:
            print(f"Error fetching CSRF token. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("Error fetching CSRF token:", e)
    return None, None

def register_user(invite_by, csrf_token, cookies, idempotency_key, user_name, email, password, proxies):
    url = 'https://wallet.litas.io/api/v1/auth/register'
    headers = {
        'X-CSRF-TOKEN': csrf_token,
        'IDEMPOTENCY-KEY': idempotency_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Referer': f'https://wallet.litas.io/invite/{invite_by}',
        'User-Agent': random.choice(USER_AGENTS)
    }
    
    payload = {
        "userName": user_name,
        "email": email,
        "password": password,
        "repeatedPassword": password,
        "invitedBy": invite_by,
        "reCaptchaResponse": get_captcha()
    }
    
    proxy = get_random_proxy(proxies)
    
    try:
        response = requests.post(url, headers=headers, json=payload, cookies=cookies, proxies=proxy, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Registration Error: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print("Error during registration:", e)
    return None

# Load proxies
proxies = load_proxies()

# Infinite loop for continuous registration
while True:
    print("\n[+] Registering a new user...")
    
    csrf_token, cookies = get_antiforgery_token(invite_by, proxies)
    
    if not csrf_token:
        print("[-] Failed to fetch CSRF token. Retrying in 2 seconds...")
        time.sleep(2)
        continue

    idempotency_key = str(uuid.uuid4())
    user_name = generate_random_username()
    email = generate_random_email()
    password = generate_random_password()

    print(f"[*] Generated User - Username: {user_name}, Email: {email}, Password: {password}")

    registration_response = register_user(invite_by, csrf_token, cookies, idempotency_key, user_name, email, password, proxies)

    if registration_response:
        print("[+] Registration Successful:", registration_response)
    else:
        print("[-] Registration Failed. Retrying in 2 seconds...")

    time.sleep(2)  # Wait before the next registration attempt