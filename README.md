# Admin Panel Kaise Milega — Firebase Remote Config

## Kyun Firebase, aur seedha "admin dashboard" kyun nahi?

Yah app **bina backend/server ke** design ki gayi hai (poora kaam phone
par local hi hota hai) — isliye ek "classic" web-dashboard (jahan aap
login karke edit karein) banane ke liye ek pura backend server chahiye
hoga, jiska matlab hoga: server hosting ka kharcha + zyada complexity.

Iski jagah **Firebase Remote Config** (Google ki mufte service) istemal
karna industry-standard tarika hai — isi se solo developers aur choti
companiyan apni app control karti hain, bina apna server banaye.

## Firebase Remote Config Se Aap Kya Control Kar Payenge

- Ads ON/OFF karna (bina naya APK banaye)
- Kitne posters ke baad interstitial ad dikhe (abhi 3 set hai)
- App ke upar ek "Update available" jaisa message dikhana
- "Maintenance mode" — agar kabhi app band karni ho kuch der ke liye

## Setup Karne Ka Tarika (Ek Baar Karna Hai)

1. **console.firebase.google.com** par jaayein, Google account se login karein
2. "Add Project" — naam dein jaise `poster-maker-pro`
3. Project ke andar "Remote Config" section me jaayein
4. Yahan key-value pairs banayein, jaise:
   - `ads_enabled` = `true`
   - `min_posters_between_interstitial` = `3`
   - `app_update_message` = (khali)
   - `maintenance_mode` = `false`
5. Firebase apne aap ek `google-services.json` file degi — use project
   ke root folder me daal dein
6. `requirements.txt` me `firebase-admin` ya `plyer` ke through Remote
   Config fetch karne wala thoda extra code chahiye hoga (yah agla step
   hai — jab aap yahan tak pahunch jaayein, mujhe bataiye, main wahi
   integration code de dunga)

**Abhi ke liye:** app `DEFAULT_REMOTE_CONFIG` (jo `main.py` me hai) ke
values use karti hai — yani app bina Firebase ke bhi poori tarah chalti
hai, bas remote se control karne ki suvidha baad me judegi.

---

# AdMob Setup — Asli ID Kaise Lein

1. **apps.admob.google.com** par jaayein, Google account se login karein
2. "Apps" me jaakar "Add App" — Android chunein
3. App ka naam dein, Play Store par abhi published nahi hai to "No" chunein
4. Yahan se 3 cheezein milengi:
   - **App ID** (jaise `ca-app-pub-XXXXXXXXXX~YYYYYYYYYY`)
   - **Banner Ad Unit ID**
   - **Interstitial Ad Unit ID** (naya ad unit banana padega "Interstitial" type ka)
5. `main.py` ke sabse upar teen lines hain:
   ```python
   ADMOB_APP_ID = "..."
   ADMOB_BANNER_ID = "..."
   ADMOB_INTERSTITIAL_ID = "..."
   ```
   Inhe apni asli IDs se badal dein
6. `buildozer.spec` me bhi yah line update karein:
   ```
   android.meta_data = com.google.android.gms.ads.APPLICATION_ID=AAPKI_ASLI_APP_ID
   ```

## Zaroori Chetavani (Warning)

- Jab tak launch nahi kar rahe, **TEST ID** (jo abhi code me hai) hi
  rakhein — yah Google ki apni official test ID hai
- **Khud apni asli ads par click na karein** — na testing ke liye, na
  galti se. AdMob policy ismein bahut sakht hai, account permanently
  ban ho sakta hai. Testing hamesha TEST ID se hi karein.

---

# Play Store Par Daalne Se Pehle — Poori Checklist

| # | Kaam | Status |
|---|---|---|
| 1 | AdMob ki asli App ID + Ad Unit IDs code me daalna | Aapko karna hai |
| 2 | **Signed Release APK** banana (abhi jo bantі hai woh "debug" hai) | Neeche tarika hai |
| 3 | **Privacy Policy** — ek webpage/document jisme likha ho app kaunsa data leti hai | Zaroori — bina iske AdMob/Play Store dono reject kar denge |
| 4 | App Icon + Feature Graphic + Screenshots | Icon ban chuka hai, screenshots app chalakar khud lene honge |
| 5 | App ka Play Store listing (title, description, category) | Aap likhenge |
| 6 | Content Rating Questionnaire (Play Console ke andar) | Play Console khud poochega |
| 7 | Data Safety Form (Play Console) — batana hoga app kaunsa data collect karti hai | Is app me sirf photo access hai, koi personal data server par nahi jaata |

## Signed Release APK Kaise Banayein (Play Store Ke Liye Zaroori)

Debug APK sirf testing ke liye hoti hai — Play Store sirf "signed
release" APK/AAB accept karta hai. Iske liye ek **keystore** (ek tarah
ki digital chaabi) banani padti hai. Yah thoda technical step hai —
jab aap yahan tak pahunch jaayein (yani baaki sab test ho chuka ho),
mujhe bataiye, main GitHub Actions ke andar hi yah signing process
add kar dunga (keystore banane se lekar GitHub Secrets me surakshit
rakhne tak) — abhi isse pehle app ka core kaam sahi se chalna zaroori
hai.
