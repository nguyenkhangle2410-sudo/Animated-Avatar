from datetime import datetime
import requests
import base64


def get_season():
    m = datetime.now().month
    return "spring" if m in [3, 4, 5] else "summer" if m in [6, 7, 8] else "autumn" if m in [9, 10, 11] else "winter"


def get_weather(city, api_key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        data = requests.get(url, timeout=5,).json()
        cond = data["weather"][0]["main"].lower()
        return "rain" if any(w in cond for w in ["rain", "drizzle", "thunderstorm"]) else "clear"
    except:
        return "clear"


def update_discord_avt(gif_path, token):
    with open(gif_path, "rb") as f:
        b64_gif = base64.b64encode(f.read()).decode("utf-8")
    url = "https://discord.com/api/v10/users/@me"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"avatar": f"data:image/gif;base64,{b64_gif}"}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Avatar updated successfully!")
    else:
        print(f"Failed to update avatar: {response.status_code} - {response.text}")