import os
import requests

def get_real_solana_meme():
    try:
        # البحث المباشر في أحدث الأزواج المضافة أو منصة pump
        url = "https://api.dexscreener.com/latest/dex/search?q=pump"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            
            # تصفية دقيقة: شبكة سولانا، ومنصة pump أو raydium، واستبعاد عملة SOL نفسها
            meme_pairs = [
                p for p in pairs 
                if p.get("chainId") == "solana" 
                and p.get("baseToken", {}).get("symbol", "").upper() not in ["SOL", "USDC", "USDT", "WBTC"]
            ]
            
            if meme_pairs:
                # نأخذ أول عملة ميم حقيقية نشطة
                top = meme_pairs[0]
                symbol = top.get("baseToken", {}).get("symbol", "UNKNOWN")
                name = top.get("baseToken", {}).get("name", "Unknown")
                dex = top.get("dexId", "unknown")
                price = top.get("priceUsd", "0")
                pair_address = top.get("pairAddress", "")
                
                # استخراج البيانات للدرس العميق
                liquidity = top.get("liquidity", {}).get("usd", 0) or 0
                volume_24h = top.get("volume", {}).get("h24", 0) or 0
                price_change = top.get("priceChange", {}).get("h24", 0) or 0
                
                link = top.get("url", f"https://dexscreener.com/solana/{pair_address}")
                
                # تقييم الدرس العميق لميم كوين
                if liquidity > 5000 and volume_24h > 10000:
                    verdict = "🔥 ميم كوين ناشط بحركة تداول ممتازة"
                else:
                    verdict = "⚠️ ميم كوين جديد جداً (مخاطر عالية جداً - دير بالك)"

                analysis_report = (
                    f"🐸 **ميم كوين صواريخ على سولانا!**\n"
                    f"🏷️ **الاسم والرمز:** {name} (${symbol})\n"
                    f"🏦 **المنصة:** {dex.upper()}\n"
                    f"💵 **السعر:** ${price}\n"
                    f"💧 **السيولة:** ${liquidity:,.0f}\n"
                    f"📈 **حجم التداول (24h):** ${volume_24h:,.0f}\n"
                    f"📊 **تغير السعر:** {price_change}%\n\n"
                    f"🧠 **الدرس العميق:** {verdict}\n"
                    f"🔗 **رابط الفحص المباشر:** {link}"
                )
                
                return symbol, analysis_report
        return None, None
    except Exception as e:
        print(f"خطأ في جلب الميم كوين: {e}")
        return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("رابط ديسكورد غير موجود!")
        return

    message = {
        "content": f"🚀 **رصد ميم كوين حقيقي (Pump/Solana)!**\n\n- **الرمز:** ${coin}\n\n{analysis}"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم الإرسال لديسكورد بنجاح!")
    else:
        print(f"فشل الإرسال، الكود: {response.status_code}")

if __name__ == "__main__":
    coin, analysis = get_real_solana_meme()
    if coin:
        send_to_discord(coin, analysis)
    else:
        print("لم يتم العثور على عملات ميم حالياً.")
