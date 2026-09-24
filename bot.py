import os
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def fetch_dexscreener_tokens():
    """جلب أحدث العملات والبروفايلات من DexScreener"""
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get("pairs", [])
    except Exception as e:
        print(f"Error fetching from DexScreener: {e}")
        return []

def evaluate_and_find_queen(pairs):
    """نظام التقييم الخارق من 10 نقاط + استبعاد العملات الكبرى"""
    best_token = None
    max_score = -1

    for pair in pairs:
        # التأكد أن الشبكة هي Solana
        if pair.get("chainId") != "solana":
            continue

        symbol = pair.get("baseToken", {}).get("symbol", "").upper()
        
        # 🛑 استبعاد العملات الرئيسية مثل سولانا وغيرها للتركيز على الميمز فقط
        if symbol in ["SOL", "ETH", "USDC", "USDT", "BTC", "WSOL"]:
            continue

        liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
        volume_24h = pair.get("volume", {}).get("h24", 0) or 0
        price_change_24h = pair.get("priceChange", {}).get("h24", 0) or 0

        score = 0

        # 1. معيار السيولة (بحد أقصى 5 نقاط)
        if liquidity > 20000:
            score += 5
        elif liquidity > 5000:
            score += 3
        elif liquidity > 1000:
            score += 1

        # 2. معيار حجم التداول (بحد أقصى 5 نقاط)
        if volume_24h > 50000:
            score += 5
        elif volume_24h > 10000:
            score += 3
        elif volume_24h > 2000:
            score += 1

        # اختيار الملكة بناءً على الأعلى نقاطاً
        if score > max_score:
            max_score = score
            best_token = {
                "name": pair.get("baseToken", {}).get("name", "Unknown"),
                "symbol": symbol,
                "address": pair.get("baseToken", {}).get("address", ""),
                "liquidity": liquidity,
                "volume_24h": volume_24h,
                "price_change": price_change_24h,
                "score": score,
                "url": pair.get("url", "https://dexscreener.com/solana")
            }

    return best_token, max_score

def send_discord_alert(token):
    """إرسال تقرير استثماري خارق ومفصل إلى ديسكورد مع نصيحة استثمارية"""
    if not token:
        return

    score = token["score"]
    
    # تحديد الحالة، المخاطر، والنصيحة الاستثمارية بناءً على الخوارزمية
    if score >= 8:
        status_emoji = "🔥 عملة واعدة جداً (صاروخ محتمل)"
        risk_level = "🟢 منخفضة إلى متوسطة"
        investment_advice = "✅ **نعم للاستثمار (فرصة قوية بمبلغ تجريبي ودراسة)**"
    elif score >= 4:
        status_emoji = "⚡ حركة مقبولة (تستحق المراقبة)"
        risk_level = "🟡 متوسطة"
        investment_advice = "⚠️ **استثمار بحذر شديد (مضاربة سريعة وبرأس مال صغير جداً)**"
    else:
        status_emoji = "⚠️ ناشئة جداً (عالية المخاطر)"
        risk_level = "🔴 عالية جداً"
        investment_advice = "❌ **لا تقم بالاستثمار (غير مستوفية للشروط الأساسية)**"

    payload = {
        "embeds": [
            {
                "title": f"🚀 Alpha Sniper: ملكة الدفعة المكتشفة!",
                "description": f"**{token['name']} ({token['symbol']})**\nتم رصدها وتحليلها بنجاح بواسطة نظام الذكاء الاصطناعي.",
                "color": 65280 if score >= 8 else 16776960,
                "fields": [
                    {"name": "📊 التقييم النهائي", "value": f"**{score}/10** - {status_emoji}", "inline": False},
                    {"name": "💡 النصيحة الاستثمارية", "value": investment_advice, "inline": False},
                    {"name": "💧 السيولة", "value": f"${token['liquidity']:,.2f}", "inline": True},
                    {"name": "📈 حجم التداول (24س)", "value": f"${token['volume_24h']:,.2f}", "inline": True},
                    {"name": "📉 التغير في السعر", "value": f"{token['price_change']}%", "inline": True},
                    {"name": "🛡️ تقييم المخاطر", "value": risk_level, "inline": False},
                    {"name": "📋 عقد العملة (Contract Address)", "value": f"`{token['address']}`", "inline": False},
                    {
                        "name": "🔗 روابط الشراكة السريعة والشارت", 
                        "value": f"[DexScreener الشارت]({token['url']}) | [Photon صيد سريع](https://photon-sol.today/meme/{token['address']}) | [BullX](https://bullx.io/terminal?address={token['address']})", 
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Solana Meme Bot - Autonomous Alpha Scanner 🛡️ | Not Financial Advice"
                }
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print(f"Discord response: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Discord: {e}")

if __name__ == "__main__":
    print("Starting Advanced Solana Meme Bot Scan...")
    pairs = fetch_dexscreener_tokens()
    if pairs:
        queen, score = evaluate_and_find_queen(pairs)
        if queen and score >= 3: # خفضناها إلى 3 لضمان ظهور فرص جيدة للمتابعة والنصيحة
            send_discord_alert(queen)
            print(f"Alert sent for queen: {queen['symbol']} with score {score}")
        else:
            print("No high-quality tokens found in this batch. Skipping alert.")
    else:
        print("No pairs fetched from API.")
