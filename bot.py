import os
import requests
from datetime import datetime, timezone

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_token_age_hours(pair):
    """حساب عمر الميم كوين بالساعات بناءً على وقت إنشائها"""
    pair_created_at = pair.get("pairCreatedAt")
    if not pair_created_at:
        return "غير معروف"
    
    try:
        # تحويل وقت الإنشاء من Unix timestamp (الميللي ثانية) إلى وقت حقيقي
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
    """جلب وتحليل أحدث عملات سولانا مع حساب العمر والنصيحة الاستثمارية"""
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        pairs = data.get("pairs", [])
        
        if not pairs:
            print("❌ لم يتم العثور على أي أزواج تداول من الـ API.")
            return None

        best_token = None
        max_score = -1

        for pair in pairs:
            # فلترة شبكة سولانا فقط
            if pair.get("chainId") != "solana":
                continue

            symbol = pair.get("baseToken", {}).get("symbol", "").upper()
            
            # استبعاد العملات الكبرى لتجنب السبام
            if symbol in ["SOL", "ETH", "USDC", "USDT", "BTC", "WSOL"]:
                continue

            liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
            volume_24h = pair.get("volume", {}).get("h24", 0) or 0
            price_change = pair.get("priceChange", {}).get("h24", 0) or 0

            # نظام النقاط (السكور من 10)
            score = 0
            if liquidity > 20000:
                score += 5
            elif liquidity > 5000:
                score += 3
            elif liquidity > 1000:
                score += 1

            if volume_24h > 50000:
                score += 5
            elif volume_24h > 10000:
                score += 3
            elif volume_24h > 2000:
                score += 1

            # اختيار العملة ذات السكور الأعلى
            if score > max_score:
                max_score = score
                
                # حساب العمر
                age_str = get_token_age_hours(pair)

                # تحديد النصيحة الاستثمارية بناءً على السكور
                if score >= 8:
                    investment_advice = "🟢 **نعم للاستثمار (فرصة قوية بمبلغ تجريبي ودراسة)**"
                elif score >= 4:
                    investment_advice = "🟡 **استثمار بحذر شديد (مضاربة سريعة وبرأس مال صغير)**"
                else:
                    investment_advice = "🔴 **لا تقم بالاستثمار (عالية المخاطر وغير مستوفية)**"

                best_token = {
                    "name": pair.get("baseToken", {}).get("name", "Unknown Token"),
                    "symbol": symbol,
                    "address": pair.get("baseToken", {}).get("address", "N/A"),
                    "liquidity": liquidity,
                    "volume_24h": volume_24h,
                    "price_change": price_change,
                    "score": max(score, 1),
                    "age": age_str,
                    "advice": investment_advice,
                    "url": pair.get("url", "https://dexscreener.com/solana")
                }

        return best_token

    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب البيانات: {e}")
        return None

def send_to_discord(token):
    """إرسال التقرير الاحترافي مع العمر والنصيحة إلى ديسكورد"""
    if not token:
        print("⚠️ لا توجد عملة لإرسالها.")
        return

    if not DISCORD_WEBHOOK_URL:
        print("❌ خطأ: متغير DISCORD_WEBHOOK_URL غير مُعرّف في الـ Secrets!")
        return

    payload = {
        "embeds": [
            {
                "title": f"🚀 صيد جديد: {token['name']} ({token['symbol']})",
                "description": "تم فحص السوق بنجاح واستخراج التحليل الشامل.",
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
                    "text": "Solana Alpha Sniper Bot 🛡️ | Not Financial Advice"
                }
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            print("✅ تم إرسال التقرير إلى ديسكورد بنجاح تام!")
        else:
            print(f"❌ فشل الإرسال، كود الرد: {response.status_code}, الرد: {response.text}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء إرسال الطلب لـ ديسكورد: {e}")

if __name__ == "__main__":
    print("🤖 بدء تشغيل بوت صيد ميمز سولانا...")
    token = get_solana_meme_token()
    if token:
        print(f"🎯 تم العثور على العملة: {token['symbol']} برصيد نقاط: {token['score']}")
        send_to_discord(token)
    else:
        print("⚠️ لم يتم العثور على أي عملة مطابقة.")
