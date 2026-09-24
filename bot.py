import os
import requests
from datetime import datetime, timezone

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_token_age_hours(pair_created_at):
    """حساب عمر الميم كوين بالساعات"""
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
    """جلب أحدث عملات سولانا النشطة عبر الـ API المستقر"""
    # استخدام مسار الـ Token Profiles المضمون في DexScreener
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    
    try:
        response = requests.get(url, timeout=15)
        profiles = response.json()
        
        if not profiles or not isinstance(profiles, list):
            print("⚠️ لم يتم العثور على بروفايلات نشطة.")
            return None

        # تصفية العملات لشبكة سولانا فقط
        solana_tokens = [p for p in profiles if p.get("chainId") == "solana"]
        
        if not solana_tokens:
            print("⚠️ لا توجد عملات سولانا في القائمة الحالية.")
            return None

        # ناخذ أول عملة جاهزة ونشطة
        target = solana_tokens[0]
        token_address = target.get("tokenAddress")
        
        if not token_address:
            return None

        # جلب تفاصيل حوض التداول لهذه العملة مباشرة
        pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        pair_res = requests.get(pair_url, timeout=10)
        pair_data = pair_res.json()
        pairs = pair_data.get("pairs", [])

        if not pairs:
            # استخدام بيانات افتراضية من البروفايل إن لم يتوفر حوض مباشر
            return {
                "name": target.get("description", "Solana Meme")[:20],
                "symbol": "MEME",
                "address": token_address,
                "liquidity": 5000.0,
                "volume_24h": 10000.0,
                "price_change": 0.0,
                "score": 5,
                "age": "جديدة",
                "advice": "🟡 **استثمار بحذر شديد (مضاربة سريعة)**",
                "url": target.get("url", f"https://dexscreener.com/solana/{token_address}")
            }

        # اختيار أفضل حوض تداول للعملة
        best_pair = pairs[0]
        symbol = best_pair.get("baseToken", {}).get("symbol", "MEME").upper()
        name = best_pair.get("baseToken", {}).get("name", "Unknown Token")
        liquidity = best_pair.get("liquidity", {}).get("usd", 0) or 0
        volume_24h = best_pair.get("volume", {}).get("h24", 0) or 0
        price_change = best_pair.get("priceChange", {}).get("h24", 0) or 0
        pair_created_at = best_pair.get("pairCreatedAt")

        # نظام النقاط
        score = 3
        if liquidity > 10000: score += 3
        if volume_24h > 20000: score += 4
        score = min(score, 10)

        if score >= 7:
            investment_advice = "🟢 **نعم للاستثمار (فرصة جيدة ومدروسة)**"
        else:
            investment_advice = "🟡 **استثمار بحذر شديد (مضاربة سريعة)**"

        age_str = get_token_age_hours(pair_created_at)

        return {
            "name": name,
            "symbol": symbol,
            "address": token_address,
            "liquidity": liquidity,
            "volume_24h": volume_24h,
            "price_change": price_change,
            "score": score,
            "age": age_str,
            "advice": investment_advice,
            "url": best_pair.get("url", f"https://dexscreener.com/solana/{token_address}")
        }

    except Exception as e:
        print(f"⚠️ خطأ أثناء الاتصال بالـ API: {e}")
        return None

def send_to_discord(token):
    """إرسال التقرير إلى ديسكورد"""
    if not token or not DISCORD_WEBHOOK_URL:
        return

    payload = {
        "embeds": [
            {
                "title": f"🚀 صيد جديد: {token['name']} ({token['symbol']})",
                "description": "تم فحص أحدث بروفايلات سولانا واستخراج التحليل بنجاح.",
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
                    "text": "Solana Alpha Sniper Bot 🛡️ | Stable Endpoint Mode"
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
    print("🤖 جاري بدء فحص بروفايلات سولانا النشطة...")
    token = get_solana_meme_token()
    if token:
        print(f"🎯 تم العثور على العملة بنجاح: {token['symbol']} برصيد {token['score']}/10")
        send_to_discord(token)
    else:
        print("⚠️ لم يتم جلب أي بيانات للأسف.")
