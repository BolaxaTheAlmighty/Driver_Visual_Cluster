import requests

s = requests.Session()
s.headers["User-Agent"] = "VisualClusterProject-Scraper/0.1 https://github.com/BolaxaTheAlmighty"

r = s.get("https://loudspeakerdatabase.com/next_page_api/offset=0", timeout=20)
html = r.text

print("Estado:", r.status_code)
print("Tamanho:", len(html))
print("Cartões:", html.count('<article class="woofer_card ribbon-container"'))
print("Cookies:", s.cookies.get_dict())
print(html[:800])

with open("debug_offset0.html", "w", encoding="utf-8") as f:
    f.write(html)
