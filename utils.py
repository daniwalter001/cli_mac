import json

# import math
import os

# import random
import requests

# import mpv
from enum import Enum
import math

headers_g = {
    "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
    "X-User-Agent": "Model: MAG250; Link: WiFi",
    # "Referer": portal_url,
    # "Cookie": f"mac={mac}; stb_lang=en; timezone=Europe/Amsterdam;",
    # "Host": urlparse(portal_url).netloc,
    "Accept": "*/*",
}

headers_token = {
    "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
    "X-User-Agent": "Model: MAG250; Link: WiFi",
    "Accept": "*/*",
}


def getToken(server_host: str, headers: dict):
    global proxies
    global lastRefresh
    params = "/server/load.php?type=stb&action=handshake&token=&JsHttpRequest=1-xml"
    h_eader = requests.utils.default_headers()
    h_eader.update(headers)

    try:
        res = None
        try:
            res = requests.get(
                f"{server_host}{params}",
                headers=h_eader,
                timeout=15,
            )

        except (
            # or requests.exceptions.ConnectTimeout
            requests.exceptions.ReadTimeout
            # or ReadTimeoutError
        ) as e:
            print(e)
            return None
        except requests.exceptions.ConnectionError as e:
            print(e)
            return None

        resjson = {}

        if res.status_code == 200:
            if not res.content.decode():
                return None
            resjson = json.loads(res.content.decode())
            try:
                if "js" not in resjson:
                    return None
                assert resjson["js"]
                assert resjson["js"]["token"]

                return resjson["js"]["token"]

            except AssertionError as e:
                print(e)
                print("[*] Failed Token")
        elif res.status_code == 403:
            print("BLOCKED")

        return None

    except TimeoutError or requests.exceptions.ConnectTimeout as e:
        print(e)
    except Exception as e:
        print(e)

    return None


def getAllStreams(token: str, server_host: str, headers: dict):

    if token:
        params = "/server/load.php?type=itv&action=get_all_channels&JsHttpRequest=1-xml"

        headers["Authorization"] = f"Bearer {token}"

        res = None
        try:

            res = requests.get(
                f"{server_host}{params}",
                headers=headers,
                timeout=20,
            )

        except TimeoutError or requests.exceptions.ConnectTimeout:
            return None
        except requests.exceptions.ConnectionError as e:
            print(e)
            return None
        except requests.exceptions.ChunkedEncodingError as e:
            print(e)
            return None

        if res.status_code >= 400:
            print(f"[*]{res.reason} even with {token}")
            return []

        if len(res.content) < 100:
            print(f"RES: {res.text}")
            print("[x]Too less data to parse")
            return []

        # print(f"[*] OK: <{res.content.decode()[0:30]}>")

        try:
            assert res.content.decode() != ""
            data = json.loads(res.content.decode())
            assert data["js"]["data"]
            channnels = data["js"]["data"]
            return list(channnels)

        except AssertionError:
            return []
        except TimeoutError or requests.exceptions.ConnectTimeout as e:
            print(e)
            return []
        except json.decoder.JSONDecodeError as e:
            print(e)
            print(res.content.decode())
            return []

    else:
        print("[*]ERROR: Token Invalid")


def wait(label=""):
    if not label:
        label = "Entrer pour continuer"
    return input(f"{label}...")


def getAllGenres(host, headers, token):

    if token:
        params = "/server/load.php?type=itv&action=get_genres&JsHttpRequest=1-xml"

        headers["Authorization"] = f"Bearer {token}"
        res = requests.get(f"{host}{params}", headers=headers)
        try:
            assert res.content.decode() != ""
            data = json.loads(res.content.decode())
            assert data["js"]
            genres = {}

            for i in data["js"]:
                genres[i["id"]] = i["title"]
            return genres
        except AssertionError:
            return {}
    else:
        print("Error: Token Invalid")
        return None


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def playWithMPV(url, title=""):
    print(f"Playing: {title}")
    if not url:
        return
    try:
        # os.system(f"vlc --meta-title='{title}' '{url}' 2> /dev/null")
        os.system(
            "mpv --title=\"{title_}\" '{url}' 2> /dev/null".format(
                title_=title.replace("(", "").replace(")", ""), url=url
            )
        )
        # player = mpv.MPV(ytdl=True)
        # player.play(url)
        # player.wait_for_playback(timeout=10)
    except Exception as e:
        print(f"Error playing {title or url}: {str(e)}")
        pass


def getLiveLink(mac, token, cmd, host):
    if not token:
        return None
    cookies = {"mac": mac, "stb_lang": "fr", "timezone": "GMT"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            host
            + "/server/load.php?type=itv&action=create_link&cmd="
            + cmd
            + "&series=0&forced_storage=false&disable_ad=false&download=false&force_ch_link_check=false&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
        )

        data = response.json()
        link_ = data["js"]["cmd"].split()[-1]
        if link_:
            return link_
    except Exception as e:
        print(e)
        return None


def getAllVod(host: str, token: str, headers: dict, type="vod"):

    if type not in ["vod", "series"]:
        return []

    if not token:
        return []

    if token:
        headers["Authorization"] = f"Bearer {token}"
        page = 1
        pages = 1
        total_items = 1
        max_page_items = 1

        contents = []

        while True:
            print(f"Page: {page}/{pages}")
            params = f"/server/load.php?type={type}&action=get_ordered_list&p={page}&sortby=added&JsHttpRequest=1-xml"

            res = requests.get(f"{host}/{params}", headers=headers)
            try:
                assert res.content.decode() != ""
                data = json.loads(res.content.decode())
                # print(data)
                assert data["js"]["data"]
                total_items = data["js"]["total_items"]
                max_page_items = data["js"]["max_page_items"]
                pages = math.ceil(total_items / max_page_items)
                pages = 10

                contents.extend(data["js"]["data"])
                page = page + 1
                if page > pages:
                    break
            except AssertionError:
                print("Nothing")
                continue
            except Exception:
                print("Nothing")
                continue

        return contents
    else:
        return []


def getAllVodGenres(host: str, token: str, headers: dict, type="vod"):

    if type not in ["vod", "series"]:
        return []

    if not token:
        return []

    if token:
        headers["Authorization"] = f"Bearer {token}"
        params = f"/server/load.php?type={type}&action=get_categories"
        res = requests.get(f"{host}/{params}", headers=headers)

        try:
            assert res.content.decode() != ""
            data = json.loads(res.content.decode())
            assert data["js"]
            return data["js"]
        except Exception:
            print("Nothing")

        return []
    else:
        return []


def getAllVodbyGenres(
    host: str, token: str, headers: dict, type="vod", categoryId="0", page="1"
):

    if type not in ["vod", "series"]:
        return []

    if not token:
        return []

    if token:
        headers["Authorization"] = f"Bearer {token}"

        params = f"/server/load.php?type={type}&action=get_ordered_list&category={categoryId}&genre=0&sortby=&p={page}"
        res = requests.get(f"{host}/{params}", headers=headers)

        try:
            assert res.content.decode() != ""
            data = json.loads(res.content.decode())
            assert data["js"]
            assert data["js"]["data"]
            return data["js"]["data"]
        except Exception:
            print("Nothing")

        return []
    else:
        return []


def getVodLink(token, cmd, host, type="vod", headers={}, ep=""):
    if not token:
        return None
    headers["User-Agent"] = (
        "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3"
    )
    headers["Authorization"] = f"Bearer {token}"
    try:
        api = f"{host}/server/load.php?type={type}&action=create_link&cmd={cmd}{f'&series={ep}' if ep !='' else ''}&force_ch_link_check=0"
        response = requests.get(
            api,
            headers=headers,
        )

        if response.status_code >= 400:
            return None

        data = response.json()

        return (
            data["js"]["cmd"].split()[-1]
            if "js" in data and "cmd" in data["js"]
            else None
        )
    except Exception as e:
        print(e)
        return None


def getVodDetails(token, movie_id, host, type="vod", headers={}):
    if not token:
        return None
    headers["User-Agent"] = (
        "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3"
    )
    headers["Authorization"] = f"Bearer {token}"
    try:
        api = f"{host}/server/load.php?type={type}&action=get_ordered_list&movie_id={movie_id}&p=1"
        response = requests.get(
            api,
            headers=headers,
        )

        if response.status_code >= 400:
            return []

        data = response.json()

        return data["js"]["data"] if "js" in data and "data" in data["js"] else []
    except Exception as e:
        print(e)
        return []


class Consts(Enum):
    toBreak = "BREAK"


def handleChoice(choice):
    if choice.lower() == "q":
        # if choice.lower() == "q" or choice.lower() == "0":
        return Consts.toBreak
    try:
        choice = int(choice)
    except Exception:
        choice = 1
    return choice
