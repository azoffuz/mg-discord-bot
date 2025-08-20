# 🤖 MG Discord Bot

MG Discord Bot — bu sizning Discord serveringiz uchun yozilgan oddiy va qulay bot.  
U slash komandalar orqali ishlaydi va Render’da tekin joylashtirilsa, **doimiy onlayn** turadi.  

---

## ✨ Xususiyatlari
- `/ping` → bot ishlayotganini tekshiradi  
- `/channels` → serverdagi barcha text va voice kanallarni chiqaradi  

---

## ⚙️ O‘rnatish (Lokal ishga tushirish)

### 1. Repositoryni klon qilish
```bash
git clone https://github.com/azoffuz/mg-discord-bot.git
cd mg-discord-bot
````

### 2. Kerakli kutubxonalarni o‘rnatish

```bash
pip install -r requirements.txt
```

### 3. Token olish

1. [Discord Developer Portal](https://discord.com/developers/applications) saytiga kiring
2. `New Application` tugmasini bosing va nom qo‘ying
3. Chap tomondan **Bot** bo‘limiga o‘ting → `Add Bot`
4. Tokenni nusxa oling

⚠️ Tokenni hech kimga bermang! Tarqalib ketsa — yangilab qo‘ying.

### 4. `.env` fayl yaratish

Loyihangiz papkasida `.env` nomli fayl ochib, quyidagicha yozing:

```
DISCORD_TOKEN=your-bot-token-here
```

### 5. Botni ishga tushirish

```bash
python bot.py
```

---

## 🚀 Render’da deploy qilish (doimiy onlayn, bepul)

### 1. Render’ga ro‘yxatdan o‘tish

* [Render](https://render.com) saytiga kiring va **GitHub hisobingizni ulang**

### 2. Yangi servis yaratish

* `New +` → **Web Service** tugmasini bosing

### 3. Repositoryni tanlash

* `mg-discord-bot` reposini belgilang

### 4. Sozlamalar

* Environment → **Add Environment Variable** bosib, qo‘shing:

  ```
  DISCORD_TOKEN=your-bot-token-here
  ```
* Start Command qatoriga yozing:

  ```
  python bot.py
  ```
* Free rejasini tanlang (tekindek ishlaydi)

### 5. Deploy

* Deploy tugmasini bosing va bot onlayn ishlay boshlaydi 🚀

---

## 📌 Slash komandalar

* `/ping` → Pong! (botning ishlayotganini tekshiradi)
* `/channels` → serverdagi barcha kanallarni chiqaradi

---

## 📜 Litsenziya
MIT License asosida.


