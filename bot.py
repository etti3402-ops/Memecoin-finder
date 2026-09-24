import os
import requests
import json

def get_best_solana_meme():
    try:
        # 1. سحب أحدث البروفايلات والعملات المضافة حديثاً
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            profiles = response.json()
            
            best_score = -1
            best_token_data = None
            
            # 2. المرور على جميع العملات الجديدة وفلترة شبكة سولانا
            for profile in profiles:
                if profile.get("chainId") == "solana":
                    token_address = profile.get("tokenAddress")
                    description = profile.get("description", "لا توجد تفاصيل إضافية")
                    
                    if token_address:
                        # جلب تفاصيل السوق الحية لكل عملة على حدة
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
                                
                                # 3. نظام النقاط الذكي (حساب قوة العملة مقارنة بالأخرى)
                                current_score = 0
                                
                                # تقييم السيولة
                                if liquidity > 20000:
                                    current_score += 5
                                elif liquidity > 5000:
                                    current_score += 3
                                elif liquidity > 1000:
                                    current_score += 1
                                    
                                # تقييم حجم التداول
                                if volume_24h > 50000:
                                    current_score += 5
                                elif volume_24h > 10000:
                                    current_score += 3
                                elif volume_24h > 2000:
                                    current_score += 1

                                # 4. الاحتفاظ بالعملة الحاصلة على أعلى نقاط في هذه الجولة
                                if current_score > best_score:
                                    best_score = current_score
                                    
                                    if best_score >= 8:
                                        verdict = "🔥 عملة واعدة جداً (سيولة وحجم تداول قوي)"
                                    elif best_score >= 4:
                                        verdict = "⚡ عملة بحركة مقبولة (تستحق المراقبة)"
                                    else:
                                        verdict = "⚠️ عملة ناشئة جداً (مخاطر عالية)"

                                    best_token_data = (
                                        symbol,
                                        (
                                            f"🐸 **أفضل عملة تم اختيارها في هذه الجولة!**\n"
                                            f"🏷️ **الاسم والرمز:** {name} (${symbol})\n"
                                            f"🏦 **المنصة:** {dex.upper()}\n"
                                            f"💵 **السعر:** ${price}\n"
                                            f"💧 **السيولة:** ${liquidity:,.0f}\n"
                                            f"📈 **حجم التداول (24h):** ${volume_24h:,.0f}\n"
                                            f"⭐ **نقاط التقييم:** {best_score}/10\n\n"
                                            f"🧠 **الدرس العميق:** {verdict}\n"
                                            f"📝 **الوصف:** {description[:100]}...\n"
                                            f"🔗 **رابط العقد المباشر:** {link}"
                                        )
                                    )
            
            # إرجاع أفضل عملة وُجدت بعد فحص القائمة كلها
            if best_token_data:
                return best_token_data
                
        return None, None
    except Exception as e:
        print(f"خطأ تقني أثناء الفحص والمقارنة: {e}")
        return None, None

def send_to_discord(coin, analysis):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("رابط ديسكورد غير موجود!")
        return

    message = {
        "content": f"🏆 **ملكة الدفعة (أفضل ميم كوين):** ${coin}\n\n{analysis}"
    }
    
    response = requests.post(webhook_url, data=json.dumps(message), headers={"Content-Type": "application/json"})
    if response.status_code == 204:
        print("تم إرسال العملة الأفضل بنجاح إلى ديسكورد!")
    else:
        print(f"فشل الإرسال، كود الخطأ: {response.status_code}")

if __name__ == "__main__":
    print("جاري فحص جميع العملات الجديدة، مقارنتها، واستخراج الأفضل...")
    coin, analysis = get_best_solana_meme()
    if coin:
        send_to_discord(coin, analysis)
    else:
        print("لم يتم العثور على عملات مناسبة في هذه الجولة.")
