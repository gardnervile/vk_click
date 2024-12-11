import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()


def get_token():
    token = os.getenv("VK_API_TOKEN")
    if not token:
        raise ValueError("Токен VK API не найден. Проверьте файл .env.")
    return token


def is_shorten_link(token, url):
    parsed_url = urlparse(url)

    if parsed_url.netloc == "vk.cc":
        return True

    api_url = "https://api.vk.com/method/utils.checkLink"
    params = {"url": url, "v": "5.131"}
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    if "response" in data and data["response"].get("status") == "not_banned":
        return False

    raise ValueError("Ссылка заблокирована или API вернул ошибку.")


def shorten_link(token, url):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    params = {"url": url, "v": "5.131"}
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(api_url, headers=headers, params=params)
    data = response.json()

    if "error" in data:
        error_msg = data["error"].get("error_msg", "Неизвестная ошибка API")
        raise ValueError(f"Ошибка API: {error_msg}")

    return data["response"]["short_url"]


def count_clicks(token, short_url):
    key = urlparse(short_url).path.strip("/")  # Извлекаем последний сегмент пути

    api_url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "key": key,
        "interval": "forever",
        "v": "5.131",
    }
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(api_url, headers=headers, params=params)
    data = response.json()

    if "error" in data:
        error_msg = data["error"].get("error_msg", "Неизвестная ошибка API")
        raise ValueError(f"Ошибка API: {error_msg}")

    stats = data["response"].get("stats", [])
    return stats[0]["views"] if stats else 0


def main():
    token = get_token()
    url = input("Введите ссылку: ")

    try:
        if is_shorten_link(token, url):
            clicks = count_clicks(token, url)
            print(f"Сумма кликов по ссылке: {clicks}")
        else:
            short_url = shorten_link(token, url)
            print("Сокращенная ссылка: ", short_url)
    except ValueError as e:
        print(e)
    except requests.exceptions.HTTPError as http_err:
        print(f"Ошибка HTTP запроса: {http_err}")
    except Exception as e:
        print("Произошла непредвиденная ошибка:", e)


if __name__ == "__main__":
    main()