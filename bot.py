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
    """البحث عن العملة مع نظام الطوارئ (ضمان الحصول على نتيجة دائماً)"""
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        pairs = data.get("pairs", [])
        
        if not pairs:
            return None

        best_token = None
        absolute_best_token = None
        max_score = -1
        absolute_max_score = -999

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

            # حساب النقاط
            score = 1
            if liquidity >= 2000:
                score += 4
            elif liquidity >= 500:
                score += 2

            if volume_24h >= 5000:
                score += 4
            elif volume_24h >= 1000:
                score += 2

            # الاحتفاظ بأفضل عملة مطلقة في السوق حالياً (حتى لو كانت بنقاط قليلة)
            if score > absolute_max_score:
                absolute_max_score = score
                absolute_best_token = pair

            # البحث عن العملة التي تتجاوز الشرط الطبيعي (3 نقاط فأكثر)
            if score > max_score and score >= 3:
                max_score = score
                best_token = pair

        # إذا وجدنا عملة تطابق الشروط الجيدة، نختارها
        chosen_pair = best_token if best_token else absolute_best_token

        if not chosen_pair:
            return None

        # تجهيز بيانات العملة المختارة
        symbol = chosen_pair.get("baseToken", {}).get("symbol", "").upper()
        liquidity = chosen_pair.get("liquidity", {}).get("usd", 0) or 0
        volume_24h = chosen_pair.get("volume", {}).get("h24", 0) or 0
        price_change = chosen_pair.get("priceChange", {}).get("h24", 0) or 0
        
        final_score = max(max_score if best_token else absolute_max_score, 1)

        if final_score >= 7:
            investment_advice = "🟢 **نعم للاستثمار (فرصة جيدة ومدروسة)**"
        elif final_score >= 3:
            investment_advice = "🟡 **استثمار بحذر شديد (مضاربة سريعة)**"
        else:
            investment_advice = "🔴 **سوق هادئ - مخاطرة عالية (للمراقبة فقط)**"

        age_str = get_token_age_hours(chosen_pair)

        return {
            "name": chosen_pair.get("baseToken", {}).get("name", "Unknown Token"),
            "symbol": symbol,
            "address": chosen_pair.get("baseToken", {}).get("address", "N/A"),
            "liquidity": liquidity,
            "volume_24h": volume_24h,
            "price_change": price_change,
            "score": final_score,
            "age": age_str,
            "advice": investment_advice,
            "url": chosen_pair.get("url", "https://dexscreener.com/solana")
        }

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
                "title": f"🚀 تقرير السوق: {token['name']} ({token['symbol']})",
                "description": "تم فحص السوق (حتى في أوقات الهدوء) وإحضار أفضل خيار متاح حالياً.",
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
                    "text": "Solana Alpha Sniper Bot 🛡️ | Quiet Market Fallback Mode"
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
    print("🤖 جاري فحص السوق (مع تفعيل وضع الطوارئ للسوق الهادئ)...")
    token = get_solana_meme_token()
    if token:
        print(f"🎯 تم اختيار العملة بنجاح: {token['symbol']} برصيد {token['score']}/10")
        send_to_discord(token)
    else:
        print("🛡️ لم يتم العثور على أي بيانات إطلاقاً.")
