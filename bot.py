import os
import requests

def get_latest_solana_meme():
    try:
        # استخدام نقطة النهاية الرسمية للبروفايلات والعملات المضافة حديثاً
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            profiles = response.json()
            
            # البحث عن أول عملة تنتمي لشبكة سولانا
            for profile in profiles:
                if profile.get("chainId") == "solana":
                    token_address = profile.get("tokenAddress")
                    description = profile.get("description", "لا توجد تفاصيل إضافية")
                    
                    if token_address:
                        # جلب تفاصيل السعر والسيولة الفعلية للعملة عبر عنوان العقد مباشرة
                        pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
                        pair_res = requests.get(pair_url, timeout=10)
                        
                        if pair_res.status_code == 200:
                            pair_data = pair_res.json()
                            pairs = pair_data.get("pairs", [])
                            
                            if pairs:
                                top = pairs[0]
                                symbol = top.get("baseToken", {}).get("symbol", "UNKNOWN")
                                name = top.get("baseToken", {}).get("name", "Unknown")
                                price = top.get("priceUsd", "0")
                                dex = top.get("dexId", "unknown")
                                
                                liquidity = top.get("liquidity", {}).get("usd", 0) or 0
                                volume_24h = top.get("volume", {}).get("h24", 0) or 0
                                link = top.get("url", f"https://dexscreener.com/solana/{token_address}")
                                
                                # الدرس العميق وتقييم العملة
                                if liquidity > 2000:
                                    verdict = "🔥 ميم كوين ناشط بسيولة مقبولة"
                                else:
                                    verdict = "⚠️ ميم كوين جديد جداً (مخاطر عالية جداً - دير بالك)"

                                report = (
                                    f"🐸 **تم رصد ميم كوين جديد على سولانا!**\n"
                                    f"🏷️ **الاسم والرمز:** {name} (${symbol})\n"
                                    f"🏦 **المنصة:** {dex.upper()}\n"
                                    f"💵 **السعر:** ${price}\n"
                                    f"💧 **السيولة:** ${liquidity:,.0f}\n"
                                    f"📈 **حجم التداول (24h):** ${volume_24h:,.0f}\n\n"
                                    f"🧠 **الدرس العميق:** {verdict}\n"
                                    f"📝 **الوصف:** {description[:120]}...\n"
                                    f"🔗 **رابط العقد المباشر:** {link}"
                                )
                                return symbol, report
                                
        return None, None
    except Exception as e:
        print(f"خطأ تقني: {e}")
        return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("رابط ديسكورد غير موجود!")
        return

    message = {
        "content": f"🚀 **صيد آلي (ميم كوين سولانا):** ${coin}\n\n{analysis}"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم إرسال العملة بنجاح إلى ديسكورد!")
    else:
        print(f"فشل الإرسال، كود الخطأ: {response.status_code}")

if __name__ == "__main__":
    print("جاري جلب أحدث عملات سولانا وتحليلها...")
    coin, analysis = get_latest_solana_meme()
    if coin:
        send_to_discord(coin, analysis)
    else:
        print("تعذر جلب العملة في هذه المحاولة، جاري إعادة المحاولة في الجولة القادمة.")
