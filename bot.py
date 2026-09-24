import os
import requests

def get_solana_meme_coin():
    try:
        # البحث في DexScreener مع استهداف العملات والمنصات المرتبطة بالميم على سولانا
        url = "https://api.dexscreener.com/latest/dex/search?q=solana"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            
            # تصفية النتائج لتكون حصرياً على شبكة سولانا وتفضيل منصات مثل pump أو raydium
            solana_memes = [
                p for p in pairs 
                if p.get("chainId") == "solana" and p.get("dexId") in ["raydium", "pump", "orca", "meteora"]
            ]
            
            # إذا لم نجد في المنصات المحددة بدقة، نأخذ أي زوج نشط على سولانا
            if not solana_memes:
                solana_memes = [p for p in pairs if p.get("chainId") == "solana"]
            
            if solana_memes:
                # نأخذ العملة الأولى ونقوم بفحصها
                top = solana_memes[0]
                symbol = top.get("baseToken", {}).get("symbol", "UNKNOWN")
                name = top.get("baseToken", {}).get("name", "Unknown")
                dex = top.get("dexId", "unknown")
                price = top.get("priceUsd", "0")
                pair_address = top.get("pairAddress", "")
                
                # استخراج بيانات السيولة وحجم التداول للدرس العميق
                liquidity = top.get("liquidity", {}).get("usd", 0) or 0
                volume_24h = top.get("volume", {}).get("h24", 0) or 0
                
                # فحص تغير السعر إن وجد (Price Change)
                price_change = top.get("priceChange", {}).get("h24", 0) or 0
                
                link = top.get("url", f"https://dexscreener.com/solana/{pair_address}")
                
                # درس عميق خاص بخصائص عملات الميم (المخاطر والفرص)
                if liquidity > 10000 and volume_24h > 20000:
                    verdict = "🔥 ميم كوين بحجم تداول مشتعل وفرصة واعدة"
                elif liquidity > 2000:
                    verdict = "⚡ ميم كوين في مرحلة البداية (تتطلب حذر وتدقيق العقد)"
                else:
                    verdict = "⚠️ ميم كوين ذات سيولة ضعيفة جداً (خطورة عالية للسحب)"

                analysis_report = (
                    f"🐸 **نوع الأصول:** ميم كوين جديدة على سولانا\n"
                    f"🏷️ **الاسم والرمز:** {name} (${symbol})\n"
                    f"🏦 **المنصة (DEX):** {dex.upper()}\n"
                    f"💵 **السعر الحالي:** ${price}\n"
                    f"💧 **السيولة:** ${liquidity:,.0f}\n"
                    f"📈 **حجم التداول (24h):** ${volume_24h:,.0f}\n"
                    f"📊 **تغير السعر:** {price_change}%\n\n"
                    f"🧠 **تقرير الدرس العميق:** {verdict}\n"
                    f"🔗 **رابط الفحص المباشر:** {link}"
                )
                
                return symbol, analysis_report
        return None, None
    except Exception as e:
        print(f"خطأ أثناء جلب عملات الميم: {e}")
        return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("خطأ: رابط ديسكورد ويب هوك غير موجود!")
        return

    message = {
        "content": f"🚨 **رصد صواريخ ميم كوين على سولانا!**\n\n- **الرمز:** ${coin}\n\n{analysis}"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم إرسال تنبيه ميم كوين إلى ديسكورد بنجاح!")
    else:
        print(f"فشل في الإرسال، كود الخطأ: {response.status_code}")

if __name__ == "__main__":
    print("جاري البحث عن أحدث عملات الميم على سولانا وإجراء الدرس العميق...")
    coin, analysis = get_solana_meme_coin()
    
    if coin:
        send_to_discord(coin, analysis)
    else:
        print("تعذر العثور على عملات ميم حالياً.")
