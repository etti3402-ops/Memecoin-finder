import os
import requests

def get_latest_market_token():
    try:
        # استخدام نقطة نهاية البحث المباشر في DexScreener لضمان جلب بيانات حية وصحيحة
        url = "https://api.dexscreener.com/latest/dex/search?q=solana"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get("pairs", [])
            
            if pairs:
                # نأخذ أول عملة نشطة وقوية من نتائج البحث الحي
                top = pairs[0]
                symbol = top.get("baseToken", {}).get("symbol", "UNKNOWN")
                name = top.get("baseToken", {}).get("name", "Unknown")
                chain = top.get("chainId", "solana")
                dex = top.get("dexId", "unknown")
                price = top.get("priceUsd", "0")
                pair_address = top.get("pairAddress", "")
                
                # استخراج بيانات السيولة والحجم لعمل "الدرس العميق"
                liquidity = top.get("liquidity", {}).get("usd", 0) or 0
                volume_24h = top.get("volume", {}).get("h24", 0) or 0
                
                link = top.get("url", f"https://dexscreener.com/{chain}/{pair_address}")
                
                # فحص التحليل العميق وتقييم المخاطر
                if liquidity > 20000 and volume_24h > 50000:
                    verdict = "🔥 عملة ذات سيولة وحجم تداول قوي (مرشحة بقوة)"
                elif liquidity > 5000:
                    verdict = "⚡ عملة ذات سيولة مقبولة (تتطلب مراقبة الحذر)"
                else:
                    verdict = "⚠️ سيولة ضعيفة أو بيانات أولية (مخاطرة عالية)"

                analysis_report = (
                    f"🏷️ **اسم العملة:** {name} (${symbol})\n"
                    f"🌐 **الشبكة:** {chain.upper()} ({dex.upper()})\n"
                    f"💵 **السعر:** ${price}\n"
                    f"💧 **السيولة:** ${liquidity:,.0f}\n"
                    f"📈 **حجم التداول (24h):** ${volume_24h:,.0f}\n\n"
                    f"🧠 **التقرير والتقييم العميق:** {verdict}\n"
                    f"🔗 **رابط الفحص المباشر:** {link}"
                )
                
                return symbol, analysis_report
        return None, None
    except Exception as e:
        print(f"خطأ في الاتصال بالسوق: {e}")
        return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("خطأ: رابط ديسكورد ويب هوك غير موجود في متغيرات البيئة!")
        return

    message = {
        "content": f"🚀 **تقرير الدرس العميق لعملة جديدة من السوق!**\n\n- **الرمز:** ${coin}\n\n{analysis}"
    }
    
    response = requests.post(webhook_url, json=message)
    if response.status_code == 204:
        print("تم إرسال تقرير الدرس العميق إلى ديسكورد بنجاح تام!")
    else:
        print(f"فشل في الإرسال، كود الخطأ: {response.status_code}")

if __name__ == "__main__":
    print("جاري فحص السوق، سحب البيانات، وإجراء الدرس العميق...")
    coin, analysis = get_latest_market_token()
    
    if coin:
        send_to_discord(coin, analysis)
    else:
        print("تعذر جلب بيانات العملات في هذه المحاولة.")
