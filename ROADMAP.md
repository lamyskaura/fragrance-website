# LAMYSK AURA — Roadmap & Competitive Analysis

## Inspiration: JOVOY Paris (jovoyparis.com)

---

## 🔴 Critical — Must fix before scaling

1. **Real product photography** — placeholder gradients look amateur; even phone flat-lays are better
2. **Olfactory pyramid (Head / Heart / Base)** on every product card — the signature luxury perfumery visual code
3. **Product detail modal/page** — click a product → full description, pyramid, pairings, story
4. **Persist cart in `localStorage`** — users lose their cart on page refresh right now
5. **Search bar** — even a simple name/notes text search across products
6. **Order tracking page (frontend)** — wire existing `/api/v1/orders/track` endpoint to a UI

---

## 🟡 High Impact — Next sprint

7. **TRY ME / Décantation** — sample option at 30–50 MAD, cost deducted from full purchase within 30 days
8. **Free delivery threshold** — "Livraison offerte dès 500 MAD" — big conversion booster
9. **Wishlist** — localStorage-based heart icon on each product (no login needed)
10. **Stock indicators** — "Plus que 3 en stock" creates urgency; backend already tracks stock
11. **Payment logos in footer** — CMI, Visa, Mastercard, COD, Virement logos
12. **Hero carousel** — rotate 3–4 campaign banners (new arrivals, coffrets, seasonal)
13. **"New In" / "Bestseller" / "Sold Out" dynamic badges** fed from FastAPI backend

---

## 🟢 Differentiators to build on (LAMYSK AURA advantages over JOVOY)

14. **Arabic + RTL support** — JOVOY is FR/EN only; ~70% of Moroccan users prefer Arabic (keep building on this)
15. **WhatsApp-first ordering** — JOVOY has nothing like this; wire deeper (order status via WA)
16. **Virtual consultation booking** — WhatsApp appointment for personalized fragrance advice
17. **Loyalty / Aura Points** — points per purchase, redeemable against next order
18. **TikTok / Reels integration** — embed social feed; perfume content performs extremely well
19. **Blog / editorial articles** — expand the Chronicle section into full SEO articles
20. **Coffret builder** — let customers build their own layering coffret

---

## JOVOY vs. LAMYSK AURA — Feature Gap Summary

| Feature | JOVOY | LAMYSK AURA |
|---|---|---|
| Languages | FR / EN | FR / AR / EN + RTL ✅ |
| WhatsApp ordering | ❌ | ✅ |
| Cash on Delivery | ❌ | ✅ |
| Olfactory quiz | ❌ | ✅ |
| Layering protocol | ❌ | ✅ |
| Coffret bundles | ❌ | ✅ |
| Fragrance education | Filters only | Full Chronique ✅ |
| Founder story | Institutional | Human / intimate ✅ |
| Product photos | High-res | Placeholders ❌ |
| Olfactory pyramid cards | ✅ | ❌ |
| Search | ✅ | ❌ |
| Filters (family, notes, price) | ✅ (500+ notes) | ❌ |
| TRY ME sampling | ✅ | ❌ |
| Wishlist | ✅ | ❌ |
| Customer accounts | ✅ | ❌ |
| Cart persistence | ✅ | ❌ (lost on refresh) |
| Loyalty program | ✅ | Promo codes only |
| Product detail page | ✅ | ❌ |
| Order tracking UI | ✅ | API only |
| Gift wrapping | ✅ | ❌ |
| Stock indicators | ✅ | ❌ |
| Payment logos | ✅ | ❌ |
| Free shipping threshold | ✅ | ❌ |
| Hero carousel | ✅ | Static |
| Blog | ✅ | Static Chronicle |

---

## Tech Stack

- **Frontend**: Single-file HTML (`index.html`) — Vanilla JS, CSS variables, trilingual i18n
- **Backend**: Python FastAPI + SQLite (aiosqlite)
- **Hosting target**: VPS / Railway / Render — `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- **Run**: `uvicorn backend.main:app --reload --port 8000`
- **Docs**: `http://localhost:8000/docs`
- **Admin key**: set `ADMIN_KEY` in `.env`
