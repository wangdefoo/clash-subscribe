import requests, yaml, json

def fetch(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        print(f"✓ fetched {url}")
        return r.text
    except Exception as e:
        print(f"✗ failed {url}: {e}")
        return None

def parse(content):
    try:
        data = yaml.safe_load(content)
        if "proxies" in data:
            return data["proxies"]
    except:
        pass
    try:
        data = json.loads(content)
        if "outbounds" in data:
            proxies = []
            for o in data["outbounds"]:
                if o.get("protocol") == "vless":
                    v = o["settings"]["vnext"][0]
                    u = v["users"][0]
                    proxies.append({
                        "name": v["address"],
                        "type": "vless",
                        "server": v["address"],
                        "port": v["port"],
                        "uuid": u["id"],
                        "tls": True,
                    })
            return proxies
    except:
        pass
    return []

all_proxies = []
for line in open("sources.txt"):
    url = line.strip()
    if not url: continue
    content = fetch(url)
    if content:
        all_proxies += parse(content)

# 去重
unique = {f"{p['server']}:{p['port']}": p for p in all_proxies}.values()

# 输出 clash.yaml 到仓库根目录
config = {
    "mixed-port": 7890,
    "allow-lan": True,
    "mode": "Rule",
    "log-level": "info",
    "proxies": list(unique),
    "proxy-groups": [
        {"name": "🚀 节点选择", "type": "select",
         "proxies": [p["name"] for p in unique]},
    ],
    "rules": ["MATCH,🚀 节点选择"]
}

with open("clash.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(config, f, allow_unicode=True)
print("✅ clash.yaml 生成完成")
