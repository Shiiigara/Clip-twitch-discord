# --- KEEP ALIVE POUR UPTIMEROBOT ---
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is alive.')

def run_ping_server():
    server = HTTPServer(('0.0.0.0', 8080), PingHandler)
    server.serve_forever()

threading.Thread(target=run_ping_server, daemon=True).start()


import requests
import time
import datetime

# === CONFIGURATION ===
TWITCH_CLIENT_ID = 'f22khnm9fxqaeiwwyjo5corih5jofw'
TWITCH_CLIENT_SECRET = 'ciqlwgv5qil3gd7orqlbcosaz3igze'
TWITCH_USERNAME = 'ugo_dlf'  # sans le lien
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1388110713687511040/px_kyBMcSbgBNOuOiKWcy2qtXAAe0QbYk9iQGfvKMuqd-Jz6XQfnZ2agxrlNoJTJ5bRB'

CHECK_INTERVAL = 60 * 2  # toutes les 2 minutes

# === AUTHENTIFICATION TWITCH ===
def get_twitch_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    return response.json()['access_token']

# === OBTENIR ID CHAINE TWITCH ===
def get_user_id(token):
    url = f'https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data'][0]['id']

# === RÉCUPÉRER LES CLIPS RÉCENTS ===
def get_recent_clips(token, user_id):
    url = 'https://api.twitch.tv/helix/clips'
    now = datetime.datetime.utcnow()
    started_at = (now - datetime.timedelta(minutes=10)).isoformat("T") + "Z"

    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    params = {
        'broadcaster_id': user_id,
        'started_at': started_at
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json().get('data', [])

# === ENVOYER SUR DISCORD ===
def send_to_discord(clip):
    message = f"🎬 **Nouveau clip Twitch !**\n**{clip['title']}** par {clip['creator_name']}\n{clip['url']}"
    data = {'content': message}
    requests.post(DISCORD_WEBHOOK_URL, json=data)

# === MAIN LOOP ===
def main():
    token = get_twitch_token()
    user_id = get_user_id(token)
    posted_clips = set()

    while True:
        print("🔄 Vérification des nouveaux clips...")
        clips = get_recent_clips(token, user_id)

        for clip in clips:
            if clip['id'] not in posted_clips:
                send_to_discord(clip)
                posted_clips.add(clip['id'])

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
