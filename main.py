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
import sys
from urllib.parse import urlparse
from simple_term_menu import TerminalMenu

creds = [
    {"server": "http://sport-birutv.my.id/c/", "mac": "00:1A:79:2D:9F:F5"},
    {"server": "http://185.243.7.151:80/c/", "mac": "00:1A:79:2D:9F:F5"},
    {"server": "http://185.243.7.151:80/c/", "mac": "00:1A:79:6D:1B:14"}
]


terminal_menu_for_creds = TerminalMenu(
    list(map(lambda x: f"{x['server']}: {x['mac']}", creds)) + ["[q] Quitter"],
    show_search_hint="Press / to search",
    title="Affichage des creds",
)

cred_index = terminal_menu_for_creds.show()

if len(creds) <= cred_index:
    cred_index = "q"

cred_index = handleChoice(str(cred_index))

if cred_index == Consts.toBreak:
    print("Exiting...")
    sys.exit()

print(cred_index)
server = creds[cred_index]["server"]
mac = creds[cred_index]["mac"]

if not server or not mac:
    print("Creds invalides...exiting")
    sys.exit()

host = "".join(server.split("/c/"))

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

        terminal_menu_for_tv = TerminalMenu(
            list(map(lambda x: str(x).replace("|", ":"), genres.values()))
            + ["[q] Quitter"],
            show_search_hint="Press / to search",
            title="Affichage des genres",
        )
        genreChoice = terminal_menu_for_tv.show()

        if len(genres) <= genreChoice:
            genreChoice = "q"

        genreChoice = str(genreChoice)

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

        genreSelectedId = list(genres.keys())[genreChoice]
        genreSelected = genres[list(genres.keys())[genreChoice]]

        channels = list(
            filter(lambda x: x["tv_genre_id"] == genreSelectedId, allChannels)
        )

        while True:
            clear()
            print(f"Affichage des canaux de {genreSelected}\r")

            terminal_menu_for_channel = TerminalMenu(
                list(map(lambda x: str(x["name"]).replace("|", ":"), channels))
                + ["[q] Quitter"],
                show_search_hint="Press / to search",
                title="Affichage des canaux",
            )
            channelChoice = terminal_menu_for_channel.show()
            if len(channels) <= channelChoice:
                channelChoice = "q"
            channelChoice = str(channelChoice)

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

            channelSelected = channels[channelChoice]

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

        terminal_menu_for_vodgenre = TerminalMenu(
            list(map(lambda x: str(x["title"]).replace("|", ":"), vodgenres))
            + ["[q] Quitter"],
            show_search_hint="Press / to search",
            title="Affichage des genres",
        )
        choixGenre = terminal_menu_for_vodgenre.show()
        if len(vodgenres) <= choixGenre:
            choixGenre = "q"

        choixGenre = str(choixGenre)

        if not choixGenre:
            continue

        if choixGenre.lower() == "q" or choixGenre.lower() == "0":
            break

        try:
            choixGenre = int(choixGenre)
        except Exception:
            choixGenre = 1

        genre = vodgenres[choixGenre]

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

        # for i, genre in enumerate(seriesgenres):
        #     print(f"{i+1}. {genre['title']}")

        # choixGenre = input("Choix du genre de la serie: ")

        terminal_menu_for_series = TerminalMenu(
            list(map(lambda x: str(x["title"]).replace("|", ":"), seriesgenres))
            + ["[q] Quitter"],
            show_search_hint="Press / to search",
            title="Affichage des genres",
        )
        choixGenre = terminal_menu_for_series.show()
        if len(seriesgenres) <= choixGenre:
            choixGenre = "q"

        if not choixGenre:
            continue

        choixGenre = str(choixGenre)

        if choixGenre.lower() == "q" or choixGenre.lower() == "0":
            break

        try:
            choixGenre = int(choixGenre)
        except Exception:
            choixGenre = 1

        genre = seriesgenres[choixGenre]

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
                # print(f"Has files: {serie['has_files']=='1'}")

                seasons = getVodDetails(token, serie["id"], host, "series", headers_g)

                if not seasons or not len(seasons):
                    break

                print("Seasons:")
                # for i, season in enumerate(seasons):
                #     print(f"{i+1}. {season['name']}")

                # choice = input("Choix: ")

                terminal_menu_for_seasons = TerminalMenu(
                    list(map(lambda x: str(x["name"]).replace("|", ":"), seasons))
                    + ["[q] Quitter"],
                    show_search_hint="Press / to search",
                    title="Affichage des saisons",
                )
                choice = terminal_menu_for_seasons.show()
                if len(seasons) <= choice:
                    choice = "q"

                choice = str(choice)
                choice = handleChoice(choice)

                if choice == Consts.toBreak:
                    break

                selectedSeason = seasons[choice]

                if not (selectedSeason and len(selectedSeason["series"])):
                    print("Pas d'episodes")
                    wait()
                    break

                while True:
                    clear()
                    # print("Episodes:")
                    # for i, episode in enumerate(selectedSeason["series"]):
                    #     print(f"{i+1}. Episode{episode}")

                    # choice = input("Choix: ")

                    terminal_menu_for_seasons = TerminalMenu(
                        list(map(lambda x: f"Episode {x}", selectedSeason["series"]))
                        + ["[q] Quitter"],
                        show_search_hint="Press / to search",
                        title="Affichage des episodes",
                    )
                    choice = terminal_menu_for_seasons.show()

                    if len(selectedSeason["series"]) <= choice:
                        choice = "q"
                    choice = str(choice)

                    choice = handleChoice(choice)

                    if choice == Consts.toBreak:
                        break

                    try:
                        choice = int(choice) + 1
                    except:
                        choice = 1

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
