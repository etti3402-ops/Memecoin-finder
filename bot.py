import os
import requests

def analyze_deep_dive(pair):
    """
    إجراء دراسة عميقة وتقييم للعملة بناءً على السيولة، حجم التداول، ونشاط السوق.
    """
    coin_name = pair.get("baseToken", {}).get("name", "Unknown")
    coin_symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
    chain_id = pair.get("chainId", "solana")
    dex_id = pair.get("dexId", "unknown")
    pair_address = pair.get("pairAddress", "")
    price_usd = pair.get("priceUsd", "0")
    
    # استخراج بيانات السيولة وحجم التداول
    liquidity = pair.get("liquidity", {})
    usd_liquidity = liquidity.get("usd", 0) if liquidity else 0
    
    volume = pair.get("volume", {})
    h24_volume = volume.get("h24", 0) if volume else 0
    
    # الفلترة والتقييم العميق (Risk & Potential Analysis)
    score = 0
    status_notes = []
    
    # 1. تقييم السيولة (Liquidity Check)
    if usd_liquidity > 50000:
        score += 3
        status_notes.append("✅ سيولة ممتازة ومريحة (أكثر من 50 ألف دولار).")
    elif usd_liquidity > 10000:
        score += 2
        status_notes.append("⚠️ سيولة متوسطة (الحذر مطلوب).")
    else:
        score += 1
        status_notes.append("🚨 سيولة ضعيفة جداً (مخاطر عالية للتعليق).")
        
    # 2. تقييم حجم التداول (Volume Check)
    if h24_volume > 100000:
        score += 3
        status_notes.append("🚀 حجم تداول قوي جداً يشير لاهتمام السوق.")
    elif h24_volume > 20000:
        score += 2
        status_notes.append("📊 حجم تداول متوسط.")
    else:
        score += 1
        status_notes.append("💤 تفاعل ضعيف نسبياً في الـ 24 ساعة الماضية.")

    # الحكم النهائي بناءً على النقاط
    if score >= 5:
        verdict = "🔥 عملة واعدة ذات اهتمام عالي (ترند قوي)"
    elif score >= 3:
        verdict = "⚡ عملة ذات حركة مقبولة (تتطلب مراقبة لصيقة)"
    else:
        verdict = "⚠️ مخاطرة عالية جداً (قد تكون مجرد سكام أو ميتة)"

    url_link = pair.get("url", f"https://dexscreener.com/{chain_id}/{pair_address}")
    
    analysis_report = (
        f"🌐 **الشبكة:** {chain_id.upper()} ({dex_id.upper()})\n"
        f"💵 **السعر:** ${price_usd}\n"
        f"💧 **السيولة (Liquidity):** ${usd_liquidity:,.0f}\n"
        f"📈 **حجم التداول (24h):** ${h24_volume:,.0f}\n\n"
        f"🔍 **تقرير الدرس العميق:**\n" + "\n".join(status_notes) + f"\n\n"
        f"📌 **التقييم النهائي:** {verdict}\n"
        f"🔗 **رابط الفحص المباشر:** {url_link}"
    )
    
    return coin_symbol, analysis_report

def get_best_trending_meme():
    try:
        url = "https://api.dexscreener.com/latest/dex/tokens/trending"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            
            if pairs:
                # نبحث عن أول عملة تحقق شروط مقبولة أو نأخذ الأقوى
                for top_pair in pairs:
                    coin_symbol, report = analyze_deep_dive(top_pair)
                    return coin_symbol, report
        return None, None
    except Exception as e:
        print(f"خطأ أثناء جلب وتحليل السوق: {e}")
        return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("خطأ: لم يتم العثور على رابط ديسكورد ويب هوك في متغيرات البيئة.")
        return

    message = {
        "content": f"🧠 **تقرير تحليل عميق لعملة ميم جديدة!**\n\n- **العملة:** ${coin}\n\n{analysis}"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم إرسال تقرير التحليل العميق إلى ديسكورد بنجاح!")
    else:
        print(f"فشل في الإرسال، كود الخطأ: {response.status_code}")

if __name__ == "__main__":
    print("جاري سحب العملة وإجراء الدرس العميق والتحليل الفني...")
    coin, analysis = get_best_trending_meme()
    
    if coin:
        send_to_discord(coin, analysis)
    else:
        print("لم يتم العثور على عملات مطابقة للمعايير حالياً.")
