import json
import os
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
import re

RSS_URL = "https://news.google.com/rss/search?q=Hawaii+travel+tourism+when:7d&hl=en-US&gl=US&ceid=US:en"

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile(r'<.*?>')
    return re.sub(cleanr, '', str(raw_html))

def fetch_hawaii_news():
    req = urllib.request.Request(
        RSS_URL,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    news_items = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            items = root.findall('.//item')[:10]
            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')

                title = title_elem.text if (title_elem is not None and title_elem.text) else "ハワイ現地最新ニュース"
                link = link_elem.text if (link_elem is not None and link_elem.text) else "#"
                desc = desc_elem.text if (desc_elem is not None and desc_elem.text) else ""
                
                clean_desc = clean_html(desc)
                if len(clean_desc) > 120:
                    clean_desc = clean_desc[:120] + "..."
                if not clean_desc.strip():
                    clean_desc = "最新のハワイ現地旅行ニュースです。詳細は元記事をご確認ください。"

                # カテゴリ判定
                category = "現地最新情報"
                lower_title = title.lower()
                if any(w in lower_title for w in ["flight", "airline", "airport", "ana", "jal"]):
                    category = "フライト・空港"
                elif any(w in lower_title for w in ["beach", "park", "diamond head", "hotel", "resort"]):
                    category = "観光・ホテル"
                elif any(w in lower_title for w in ["food", "restaurant", "dining", "market"]):
                    category = "グルメ・店舗"
                elif any(w in lower_title for w in ["rule", "warning", "police", "safe", "law"]):
                    category = "注意・ルール"

                formatted_date = datetime.now().strftime("%Y年%m月%d日 更新")

                news_items.append({
                    "title": title,
                    "summary": clean_desc,
                    "category": category,
                    "link": link,
                    "date": formatted_date
                })

    except Exception as e:
        print(f"Fetch warning: {e}")

    # 万が一ニュースが0件だった場合の初期表示
    if not news_items:
        news_items = [
            {
                "title": "ダイヤモンドヘッド登山・ハナウマ湾の事前予約制が継続中",
                "summary": "環境保全および混雑緩和のため、主要観光地ではオンライン予約が必須となっています。渡航前に公式サイトから手続きをお済ませください。",
                "category": "注意・ルール",
                "link": "https://gohawaii.com",
                "date": datetime.now().strftime("%Y年%m月%d日 更新")
            },
            {
                "title": "ホノルル市内の歩きスマホ取締りに注意",
                "summary": "道路横断中の電子機器注視には反則金が科される場合があります。移動中の安全確保にご留意ください。",
                "category": "注意・ルール",
                "link": "https://gohawaii.com",
                "date": datetime.now().strftime("%Y年%m月%d日 更新")
            }
        ]

    # news.json として書き出し
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_items, f, ensure_ascii=False, indent=2)
    print("Successfully generated news.json")

if __name__ == "__main__":
    fetch_hawaii_news()
