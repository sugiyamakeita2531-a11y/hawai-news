import json
import os
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
import re

# ハワイ関連のGoogleニュースRSS
RSS_URL = "https://news.google.com/rss/search?q=Hawaii+travel+tourism+when:7d&hl=en-US&gl=US&ceid=US:en"

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

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
            
            # 最大10件の記事を抽出
            items = root.findall('.//item')[:10]
            for item in items:
                title = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else "#"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                desc = item.find('description').text if item.find('description') is not None else ""
                
                # クリーニング
                clean_desc = clean_html(desc)
                if len(clean_desc) > 120:
                    clean_desc = clean_desc[:120] + "..."

                # カテゴリ分類（キーワード判定）
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

                # 日付のフォーマット整形（簡易）
                formatted_date = datetime.now().strftime("%Y年%m月%d日 更新")

                news_items.append({
                    "title": title,
                    "summary": clean_desc if clean_desc else "最新のハワイ現地ニュースが届きました。詳細は元記事をご確認ください。",
                    "category": category,
                    "link": link,
                    "date": formatted_date
                })

    except Exception as e:
        print(f"Fetch error: {e}")
        # 取得失敗時のフォールバックニュース
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

    # JSONファイルとして出力
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_items, f, ensure_ascii=False, indent=2)
    print("Successfully generated news.json")

if __name__ == "__main__":
    fetch_hawaii_news()
