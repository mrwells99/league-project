#!/usr/bin/env python3
"""
onetricks.gg Champion Stats Scraper
Pulls data directly from __NEXT_DATA__ JSON — no headless browser needed.

Usage:
    pip install requests beautifulsoup4
    python3 scrape_onetricks.py
"""

from curl_cffi import requests
import json
import re
import time
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

CHAMPIONS = [
    "Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Ambessa", "Amumu",
    "Anivia", "Annie", "Aphelios", "Ashe", "AurelionSol", "Aurora", "Azir",
    "Bard", "Belveth", "Blitzcrank", "Brand", "Braum", "Briar", "Caitlyn",
    "Camille", "Cassiopeia", "Chogath", "Corki", "Darius", "Diana", "Draven",
    "DrMundo", "Ekko", "Elise", "Evelynn", "Ezreal", "Fiddlesticks", "Fiora",
    "Fizz", "Galio", "Gangplank", "Garen", "Gnar", "Gragas", "Graves",
    "Gwen", "Hecarim", "Heimerdinger", "Hwei", "Illaoi", "Irelia", "Ivern",
    "Janna", "JarvanIV", "Jax", "Jayce", "Jhin", "Jinx", "Kaisa", "Kalista",
    "Karma", "Karthus", "Kassadin", "Katarina", "Kayle", "Kayn", "Kennen",
    "Khazix", "Kindred", "Kled", "KogMaw", "KSante", "Leblanc", "LeeSin",
    "Leona", "Lillia", "Lissandra", "Lucian", "Lulu", "Lux", "Malphite",
    "Malzahar", "Maokai", "MasterYi", "Mel", "Milio", "MissFortune", "Mordekaiser",
    "Morgana", "Naafiri", "Nami", "Nasus", "Nautilus", "Neeko", "Nidalee",
    "Nilah", "Nocturne", "Nunu", "Olaf", "Orianna", "Ornn", "Pantheon",
    "Poppy", "Pyke", "Qiyana", "Quinn", "Rakan", "Rammus", "RekSai",
    "Rell", "Renata", "Renekton", "Rengar", "Riven", "Rumble", "Ryze",
    "Samira", "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen",
    "Shyvana", "Singed", "Sion", "Sivir", "Skarner", "Smolder", "Sona",
    "Soraka", "Swain", "Sylas", "Syndra", "TahmKench", "Taliyah", "Talon",
    "Taric", "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere",
    "TwistedFate", "Twitch", "Udyr", "Urgot", "Varus", "Vayne", "Veigar",
    "Velkoz", "Vex", "Vi", "Viego", "Viktor", "Vladimir", "Volibear",
    "Warwick", "Wukong", "Xayah", "Xerath", "XinZhao", "Yasuo", "Yone",
    "Yorick", "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.onetricks.gg/",
}

SEASON_KEY = "S2026_1"


def scrape_champion(champion: str) -> dict:
    url = f"https://www.onetricks.gg/champions/ranking/{champion}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, impersonate="chrome")
        r.raise_for_status()

        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
        if not match:
            raise ValueError("__NEXT_DATA__ not found")

        data = json.loads(match.group(1))
        mains_all = data["props"]["pageProps"]["rankings"][SEASON_KEY]["mainsData"]
        MAJOR_REGIONS = {"KR", "EUW1", "NA1"}
        mains = [p for p in mains_all if p.get("region") in MAJOR_REGIONS and p.get("playrate", 0) >= 60]

        challenger  = sum(1 for p in mains if p.get("tier") == "Challenger")
        grandmaster = sum(1 for p in mains if p.get("tier") == "Grandmaster")
        master      = sum(1 for p in mains if p.get("tier") == "Master")
        total       = len(mains)

        print(f"  ✓ {champion:20s} | C:{challenger:4d} | GM:{grandmaster:4d} | M:{master:5d} | Total:{total:5d}")
        return {
            "champion": champion,
            "challenger": challenger,
            "grandmaster": grandmaster,
            "master": master,
            "total": total,
            "url": url,
        }

    except Exception as e:
        print(f"  ✗ {champion:20s} | ERROR: {e}")
        return {
            "champion": champion,
            "challenger": 0,
            "grandmaster": 0,
            "master": 0,
            "total": 0,
            "url": url,
            "error": str(e),
        }


def main():
    print(f"Scraping onetricks.gg for {len(CHAMPIONS)} champions...\n")
    results = []

    for champion in CHAMPIONS:
        results.append(scrape_champion(champion))
        time.sleep(3)

    results.sort(key=lambda x: x["total"], reverse=True)

    output = {
        "scraped_at": datetime.datetime.utcnow().isoformat() + "Z",
        "season": SEASON_KEY,
        "total_champions": len(results),
        "champions": results,
    }

    with open("champion_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Saved to champion_data.json")
    print(f"\nTop 10 by total OTPs:")
    for r in results[:10]:
        print(f"  {r['champion']:20s}  C:{r['challenger']:3d}  GM:{r['grandmaster']:3d}  M:{r['master']:4d}  Total:{r['total']}")


if __name__ == "__main__":
    main()
