import requests
import yaml
from pathlib import Path

OUTPUT_FILE = Path("clash.yaml")

# 读取节点 URL
with open("sources.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

all_proxies = []

def fetch_yaml(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = yaml.safe_load(r.text)
        if "proxies" in data:
            return data["proxies"]
    except Exception as e:
        print(f"✗ 获取 {url} 失败: {e}")
    return []

for url in urls:
    proxies = fetch_yaml(url)
    if proxies:
        all_proxies.extend(proxies)
        print(f"✓ 成功抓取 {len(proxies)} 个节点: {url}")
    else:
        print(f"⚠️ 未抓取到节点: {url}")

# 去重
unique = {f"{p['server']}:{p['port']}": p for p in all_proxies}.values()
unique = list(unique)

# 生成 clash.yaml
config = {
    "mixed-port": 7890,
    "allow-lan": True,
    "mode": "Rule",
    "log-level": "info",
    "proxies": unique,
    "proxy-groups": [
        {
            "name": "🚀 节点选择",
            "type": "select",
            "proxies": [p["name"] for p in unique]
        }
    ],
    "rules": ["MATCH,🚀 节点选择"]
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    yaml.safe_dump(config, f, allow_unicode=True)

print(f"\n✅ clash.yaml 已生成，共 {len(unique)} 个节点")
