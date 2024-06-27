from utils import (
    Consts,
    getLiveLink,
    getToken,
    getVodDetails,
    handleChoice,
    headers_g,
    headers_token,
    getAllStreams,
    wait,
    getAllGenres,
    clear,
    playWithMPV,
    getAllVodGenres,
    getAllVodbyGenres,
    getVodLink,
)
from urllib.parse import urlparse

#server = "http://line.rs6ott.com/c/"
#server = "http://600600.org:8080/c/"
#server = "http://mag.greatott.me:80/c/"
server = "http://185.243.7.151:80/c/"
server = "http://ott4k.me:80/c/"
server = "http://fuego-iptv.net:8080/c"

host = "".join(server.split("/c/"))
#mac = "00:1A:79:34:3F:F1"
#mac = "00:1A:79:B0:B0:B2"
#mac="00:1A:79:3D:49:64"
mac="00:1A:79:B5:10:B5"
mac="00:1A:79:00:00:22"
mac="00:1A:79:00:20:AF"

headers_token["Referer"] = server
headers_token["Host"] = urlparse(server).netloc
headers_token["Cookie"] = f"mac={mac.strip()}; stb_lang=en; timezone=GMT;"
headers_g["Referer"] = server
headers_g["Host"] = urlparse(server).netloc
headers_g["Cookie"] = f"mac={mac.strip()}; stb_lang=en; timezone=GMT;"


def tvChoice(token: str):
    if not token:
        print("Token non généré...exiting...\n")
        return
    genres = getAllGenres(host, headers_g, token)
    allChannels = getAllStreams(token, host, headers_g)
    allChannels = allChannels if allChannels else []

    while True:
        clear()
        if not genres or len(genres) == 0:
            print("Echec lors de la recup des groupes de chaines\n")
            break

        print("Affichage des canaux")
        for i, el in enumerate(genres):
            print(f"{i+1}. {genres[el]}")

        print("Choix : ")
        genreChoice = input()
        if genreChoice == "0" or genreChoice.lower() == "q":
            break
        try:
            genreChoice = int(genreChoice)
        except ValueError:
            print("Choix invalide\n")
            continue

        if genreChoice < 1 or genreChoice > len(genres):
            print("Choix invalide\n")
            continue

        clear()

        genreSelectedId = list(genres.keys())[genreChoice - 1]
        genreSelected = genres[list(genres.keys())[genreChoice - 1]]

        channels = list(
            filter(lambda x: x["tv_genre_id"] == genreSelectedId, allChannels)
        )

        while True:
            clear()
            print(f"Affichage des canaux de {genreSelected}\r")
            for i, el in enumerate(channels):
                print(f"{i+1}. {el['name']}")

            print("Choisis une chaine : ")
            channelChoice = input()
            if channelChoice == "0" or channelChoice.lower() == "q":
                break
            try:
                channelChoice = int(channelChoice)
            except ValueError:
                print("Choix invalide\n")
                continue

            if channelChoice < 1 or channelChoice > len(channels):
                print("Choix invalide\n")
                continue

            channelSelected = channels[channelChoice - 1]

            # print(channelSelected)
            print("Playing...")
            chanelUrl = channelSelected["cmd"].replace("ffmpeg ", "")
            if "localhost" in chanelUrl:
                chanelUrl = getLiveLink(mac, token, channelSelected["cmd"], host)
            playWithMPV(chanelUrl, channelSelected["name"])

            wait()
            clear()


def vodchoice(token=""):
    if not token:
        return []
    vodgenres = getAllVodGenres(host, token, headers_g)

    while True:
        clear()
        print("Vod: Genres")

        for i, genre in enumerate(vodgenres):
            print(f"{i+1}. {genre['title']}")

        choixGenre = input("Choix du genre de vod: ")

        if not choixGenre:
            continue

        if choixGenre.lower() == "q" or choixGenre.lower() == "0":
            break

        try:
            choixGenre = int(choixGenre)
        except Exception:
            choixGenre = 1

        genre = vodgenres[choixGenre - 1]

        page = 1
        while True:
            clear()
            print(f"{genre['title']} - Page: {page}")
            if "id" not in genre or not genre["id"]:
                break
            vodByGenre = getAllVodbyGenres(
                host, token, headers_g, "vod", genre["id"], str(page)
            )

            for i, vod in enumerate(vodByGenre):
                print(f"{i+1}. {vod['name']}")

            print(
                """
s: Suivant
p: Precendent
page x: to go to page x
1-max element: to choose what vod to show
            """
            )

            choice = input("Choix: ")

            if choice.lower() == "s":
                page = page + 1
                continue
            if choice.lower() == "p":
                if page > 1:
                    page = page - 1
                continue
            if "page " in choice:
                try:
                    page = int(choice.split(" ").pop())
                except Exception:
                    pass
                continue
            if choice.lower() == "q" or choice.lower() == "0":
                break

            try:
                choice = int(choice)
            except Exception:
                choice = 1

            vod = vodByGenre[choice - 1]

            vod["url"] = getVodLink(token, vod["cmd"], host, "vod", headers_g)
            if not vod["url"]:
                print("Url invalide...Exiting")
                continue
            print(vod["name"])
            print(vod["description"])

            playWithMPV(vod["url"], vod["name"])

            wait()

        wait()


def seriesChoice(token=""):
    if not token:
        return []
    seriesgenres = getAllVodGenres(host, token, headers_g, type="series")

    while True:
        clear()
        print("Series: Genres")

        for i, genre in enumerate(seriesgenres):
            print(f"{i+1}. {genre['title']}")

        choixGenre = input("Choix du genre de la serie: ")

        if not choixGenre:
            continue

        if choixGenre.lower() == "q" or choixGenre.lower() == "0":
            break

        try:
            choixGenre = int(choixGenre)
        except Exception:
            choixGenre = 1

        genre = seriesgenres[choixGenre - 1]

        page = 1
        while True:
            clear()
            print(f"{genre['title']} - Page: {page}")
            if "id" not in genre or not genre["id"]:
                break
            vodByGenre = getAllVodbyGenres(
                host, token, headers_g, "series", genre["id"], str(page)
            )

            for i, serie in enumerate(vodByGenre):
                print(f"{i+1}. {serie['name']}")

            print(
                """
s: Suivant
p: Precendent
page x: to go to page x
1-max element: to choose what vod to show
            """
            )

            choice = input("Choix: ")

            if choice.lower() == "s":
                page = page + 1
                continue
            if choice.lower() == "p":
                if page > 1:
                    page = page - 1
                continue
            if "page " in choice:
                try:
                    page = int(choice.split(" ").pop())
                except Exception:
                    continue

            if choice.lower() == "q" or choice.lower() == "0":
                break

            try:
                choice = int(choice)
            except Exception:
                choice = 1

            serie = vodByGenre[choice - 1]

            while True:
                clear()
                print(f"{serie['name']}")
                print(f"{serie['description']}")
                print(f"Has files: {serie['has_files']=='1'}")

                seasons = getVodDetails(token, serie["id"], host, "series", headers_g)

                if not seasons or not len(seasons):
                    break

                print("Seasons:")
                for i, season in enumerate(seasons):
                    print(f"{i+1}. {season['name']}")

                choice = input("Choix: ")

                choice = handleChoice(choice)

                if choice == Consts.toBreak:
                    break

                selectedSeason = seasons[choice - 1]

                if not (selectedSeason and len(selectedSeason["series"])):
                    print("Pas d'episodes")
                    wait()
                    break

                while True:
                    clear()
                    print("Episodes:")
                    for i, episode in enumerate(selectedSeason["series"]):
                        print(f"{i+1}. Episode{episode}")

                    choice = input("Choix: ")

                    choice = handleChoice(choice)

                    if choice == Consts.toBreak:
                        break

                    url = getVodLink(
                        token,
                        selectedSeason["cmd"],
                        host,
                        "vod",
                        headers_g,
                        str(choice),
                    )

                    playWithMPV(url, serie["name"])

                    wait()

            wait()


while True:
    clear()
    token = getToken(host, headers_token)
    if not token:
        print("Token non généré\n")
        wait()
        continue
    print(f"Token generé :{token}\r")

    print(
        """
Choix:
1. Afficher les canaux
2. Afficher les VOD
3. Afficher les series
4. Quitter (q ou 0 aussi pour quitter)
          """
    )

    choix = input("Votre choix : ")

    if choix == "0" or choix.lower() == "q" or choix == "4":
        break

    if choix == "1":
        tvChoice(token)
    if choix == "2":
        vodchoice(token)
    if choix == "3":
        seriesChoice(token)
    wait()
