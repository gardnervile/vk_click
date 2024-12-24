import os
import requests
import argparse
from dotenv import load_dotenv
from urllib.parse import urlparse


def is_shorten_link(token, url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == "vk.cc" and parsed_url.path.strip("/"):
        return True

    api_url = "https://api.vk.com/method/utils.checkLink"
    params = {"url": url, "v": "5.131"}
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()

    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(f"Ошибка API: {decoded_response['error']}")

    if "response" in decoded_response and decoded_response["response"].get("status") == "not_banned":
        return False

    raise ValueError("Ссылка заблокирована или API вернул ошибку.")


def shorten_link(token, url):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    params = {"url": url, "v": "5.131"}
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()

    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(f"Ошибка API: {decoded_response['error']}")

    return decoded_response["response"]["short_url"]


def count_clicks(token, short_url):
    short_key = urlparse(short_url).path.strip("/")

    api_url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "key": short_key,
        "interval": "forever",
        "v": "5.131",
    }
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()

    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(f"Ошибка API: {decoded_response['error']}")

    stats_data = decoded_response["response"].get("stats", [])
    return stats_data[0]["views"] if stats_data else 0


def main():
    load_dotenv()
    try:
        token = os.environ["VK_API_TOKEN"]
    except KeyError:
        raise KeyError("Обязательная переменная окружения 'VK_API_TOKEN' не установлена.")

    parser = argparse.ArgumentParser(description="Сокращение и статистика по ссылкам VK")
    parser.add_argument("url", help="URL для обработки")
    args = parser.parse_args()

    url = args.url

    try:
        if is_shorten_link(token, url):
            click_count = count_clicks(token, url)
            print(f"Сумма кликов по ссылке: {click_count}")
        else:
            short_url = shorten_link(token, url)
            print("Сокращенная ссылка: ", short_url)
    except requests.exceptions.HTTPError as http_err:
        print(f"Ошибка HTTP запроса: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Ошибка при запросе: {req_err}")
    except ValueError as e:
        print(f"Ошибка данных: {e}")
    except KeyError as e:
        print(f"Ошибка конфигурации: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
