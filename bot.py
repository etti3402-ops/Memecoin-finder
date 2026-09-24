import os
import requests
from datetime import datetime, timezone

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_token_age_hours(pair):
    """حساب عمر الميم كوين بالساعات"""
    pair_created_at = pair.get("pairCreatedAt")
    if not pair_created_at:
        return "غير معروف"
    
    try:
        created_time = datetime.fromtimestamp(pair_created_at / 1000, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - created_time
        
        hours = int(diff.total_seconds() // 3600)
        days = hours // 24
        
        if days > 0:
            return f"منذ {days} يوم ({hours} ساعة)"
        elif hours > 0:
            return f"منذ {hours} ساعة"
        else:
            return "جديدة جداً (أقل من ساعة)"
    except Exception:
        return "غير معروف"

def get_solana_meme_token():
    """البحث عن عملة ميمز بمتطلبات مخففة ومرنة"""
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        pairs = data.get("pairs", [])
        
        if not pairs:
            return None

        best_token = None
        max_score = -1

        for pair in pairs:
            if pair.get("chainId") != "solana":
                continue

            symbol = pair.get("baseToken", {}).get("symbol", "").upper()
            
            # استبعاد العملات الكبرى فقط
            if symbol in ["SOL", "ETH", "USDC", "USDT", "BTC", "WSOL"]:
                continue

            liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
            volume_24h = pair.get("volume", {}).get("h24", 0) or 0
            price_change = pair.get("priceChange", {}).get("h24", 0) or 0

            # نظام نقاط مخفف ومرن (أسهل في القبول)
            score = 1 # نبدأ بنقطة أساسية لأي عملة نشطة
            
            if liquidity >= 2000:
                score += 4
            elif liquidity >= 500:
                score += 2

            if volume_24h >= 5000:
                score += 4
            elif volume_24h >= 1000:
                score += 2

            # خفضنا الحد الأدنى للقبول إلى 3 نقاط لتسهيل ظهور الفرص المقبولة
            if score > max_score and score >= 3:
                max_score = score
                age_str = get_token_age_hours(pair)

                if score >= 7:
                    investment_advice = "🟢 **نعم للاستثمار (فرصة جيدة ومدروسة)**"
                else:
                    investment_advice = "🟡 **استثمار بحذر شديد (مضاربة سريعة)**"

                best_token = {
                    "name": pair.get("baseToken", {}).get("name", "Unknown Token"),
                    "symbol": symbol,
                    "address": pair.get("baseToken", {}).get("address", "N/A"),
                    "liquidity": liquidity,
                    "volume_24h": volume_24h,
                    "price_change": price_change,
                    "score": score,
                    "age": age_str,
                    "advice": investment_advice,
                    "url": pair.get("url", "https://dexscreener.com/solana")
                }

        return best_token

    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب البيانات: {e}")
        return None

def send_to_discord(token):
    """إرسال التقرير إلى ديسكورد"""
    if not token or not DISCORD_WEBHOOK_URL:
        return

    payload = {
        "embeds": [
            {
                "title": f"🚀 فرصة ميمز مرصودة: {token['name']} ({token['symbol']})",
                "description": "تم اجتياز شروط الفلترة المخففة والذكية بنجاح.",
                "color": 3447003,
                "fields": [
                    {"name": "📊 التقييم النهائي (Score)", "value": f"**{token['score']} / 10** ⭐", "inline": False},
                    {"name": "💡 النصيحة الاستثمارية", "value": token['advice'], "inline": False},
                    {"name": "⏳ عمر الميم كوين", "value": token['age'], "inline": True},
                    {"name": "💧 السيولة", "value": f"${token['liquidity']:,.2f}", "inline": True},
                    {"name": "📈 حجم التداول (24س)", "value": f"${token['volume_24h']:,.2f}", "inline": True},
                    {"name": "📉 التغير في السعر", "value": f"{token['price_change']}%", "inline": True},
                    {"name": "📋 عقد العملة (Contract Address)", "value": f"`{token['address']}`", "inline": False},
                    {
                        "name": "🔗 روابط سريعة", 
                        "value": f"[DexScreener]({token['url']}) | [Photon](https://photon-sol.today/meme/{token['address']}) | [BullX](https://bullx.io/terminal?address={token['address']})", 
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Solana Alpha Sniper Bot 🛡️ | Flexible Filter Mode"
                }
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            print("✅ تم إرسال التقرير إلى ديسكورد بنجاح تام!")
        else:
            print(f"❌ فشل الإرسال، كود الرد: {response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

if __name__ == "__main__":
    print("🤖 جاري فحص السوق بمعايير مرنة...")
    token = get_solana_meme_token()
    if token:
        print(f"🎯 تم العثور على فرصة مطابقة: {token['symbol']} برصيد {token['score']}/10")
        send_to_discord(token)
    else:
        print("🛡️ السوق هادئ جداً حالياً ولم تتجاوز أي عملة الحد الأدنى المخفف.")
