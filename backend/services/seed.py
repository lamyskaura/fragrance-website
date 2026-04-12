"""
Seed the database with the full LAMYSK AURA product catalogue.
Run once: python -m backend.services.seed
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import init_db, DB_PATH
import aiosqlite

PRODUCTS = [
    # ── ORIENT ────────────────────────────────────────────────────────────────
    {
        "slug": "ibraq", "name": "Ibraq", "brand": "Lamysk Aura Selection",
        "category": "orient", "notes": "Oud · Amber · Rose de Taïf",
        "image_url": "https://images.pexels.com/photos/4041392/pexels-photo-4041392.jpeg?auto=compress&cs=tinysrgb&w=600",
        "badge": "Orient",
        "variants": [("50ml", 490, 20), ("100ml", 820, 10)]
    },
    {
        "slug": "sehr-kalimat", "name": "Sehr Kalimat", "brand": "Lamysk Aura Selection",
        "category": "orient", "notes": "Musc Blanc · Santal · Vanille",
        "image_url": "https://images.pexels.com/photos/3910071/pexels-photo-3910071.jpeg?auto=compress&cs=tinysrgb&w=600",
        "variants": [("50ml", 420, 15), ("100ml", 720, 8)]
    },
    {
        "slug": "ghawali", "name": "Ghawali", "brand": "Lamysk Aura Selection",
        "category": "orient", "notes": "Bakhour · Safran · Ambre",
        "image_url": "https://images.pexels.com/photos/7445028/pexels-photo-7445028.jpeg?auto=compress&cs=tinysrgb&w=600",
        "variants": [("50ml", 380, 12), ("100ml", 650, 6)]
    },
    {
        "slug": "match", "name": "Match", "brand": "Lamysk Aura Selection",
        "category": "orient", "notes": "Oud · Musc · Cèdre",
        "image_url": "https://images.pexels.com/photos/3059609/pexels-photo-3059609.jpeg?auto=compress&cs=tinysrgb&w=600",
        "variants": [("50ml", 350, 18), ("100ml", 600, 9)]
    },
    {
        "slug": "woody-intense", "name": "Woody Intense", "brand": "Lamysk Aura Selection",
        "category": "orient", "notes": "Oud · Vétiver · Patchouli",
        "variants": [("50ml", 320, 20), ("100ml", 550, 10)]
    },
    {
        "slug": "woody-style", "name": "Woody Style", "brand": "Lamysk Aura Selection",
        "category": "orient", "notes": "Santal · Cèdre · Musc",
        "variants": [("50ml", 280, 25), ("100ml", 480, 12)]
    },
    # ── OCCIDENT ──────────────────────────────────────────────────────────────
    {
        "slug": "orto-parisi", "name": "Orto Parisi", "brand": "Italie",
        "category": "occident", "notes": "Audacieux · Avant-garde",
        "badge": "Occident",
        "variants": [("100ml", 850, 5)]
    },
    {
        "slug": "nosamato", "name": "Nōsamato", "brand": "Artisanal",
        "category": "occident", "notes": "Conceptuel · Narratif",
        "variants": [("100ml", 780, 4)]
    },
    {
        "slug": "rosendo-mateu", "name": "Rosendo Mateu", "brand": "Espagne",
        "category": "occident", "notes": "Méditerranéen · Élégant",
        "variants": [("100ml", 920, 6)]
    },
    {
        "slug": "essential-parfums", "name": "Essential Parfums", "brand": "France",
        "category": "occident", "notes": "Éco-responsable · Pur",
        "variants": [("100ml", 680, 8)]
    },
    {
        "slug": "teint-de-neige", "name": "Teint de Neige", "brand": "Italie",
        "category": "occident", "notes": "Poudré · Héliotrope · Iris",
        "variants": [("100ml", 750, 7)]
    },
    {
        "slug": "etat-libre-orange", "name": "État Libre d'Orange", "brand": "France",
        "category": "occident", "notes": "Rebelle · Audacieux · Libre",
        "variants": [("100ml", 820, 5)]
    },
    {
        "slug": "jorum-studio", "name": "Jorum Studio", "brand": "Écosse",
        "category": "occident", "notes": "Innovant · Artistique",
        "variants": [("100ml", 890, 4)]
    },
    # ── LES ABSOLUS ───────────────────────────────────────────────────────────
    {
        "slug": "amouage", "name": "Amouage", "brand": "Oman",
        "category": "absolus", "notes": "Opulent · Oriental · Intemporel",
        "badge": "Absolu",
        "variants": [("100ml", 1850, 3)]
    },
    {
        "slug": "frederic-malle", "name": "Frédéric Malle", "brand": "France",
        "category": "absolus", "notes": "Magistral · Éditorial · Iconique",
        "variants": [("100ml", 2200, 3)]
    },
    {
        "slug": "matiere-premiere", "name": "Matière Première", "brand": "France",
        "category": "absolus", "notes": "Pur · Brut · Essentiel",
        "variants": [("100ml", 1650, 4)]
    },
    {
        "slug": "roja-parfums", "name": "Roja Parfums", "brand": "UK",
        "category": "absolus", "notes": "Luxueux · Royal · Extraordinaire",
        "variants": [("100ml", 3200, 2)]
    },
    {
        "slug": "xerjoff", "name": "Xerjoff", "brand": "Italie",
        "category": "absolus", "notes": "Artistique · Couture · Majestueux",
        "variants": [("100ml", 2800, 2)]
    },
    {
        "slug": "clive-christian", "name": "Clive Christian", "brand": "UK",
        "category": "absolus", "notes": "Patrimoine · Noble · Intemporel",
        "variants": [("100ml", 3600, 2)]
    },
    # ── LES ÉCRINS ────────────────────────────────────────────────────────────
    {
        "slug": "coffret-noblesse", "name": "Coffret Noblesse", "brand": "Lamysk Aura",
        "category": "ecrins", "notes": "La femme élégante, pour les grandes occasions",
        "variants": [("Coffret", 980, 10)]
    },
    {
        "slug": "coffret-royal-woman", "name": "Coffret Royal Woman", "brand": "Lamysk Aura",
        "category": "ecrins", "notes": "La femme sophistiquée au quotidien",
        "variants": [("Coffret", 750, 12)]
    },
    {
        "slug": "coffret-royal-man", "name": "Coffret Royal Man", "brand": "Lamysk Aura",
        "category": "ecrins", "notes": "L'homme raffiné qui sait ce qu'il veut",
        "variants": [("Coffret", 750, 10)]
    },
    {
        "slug": "coffret-douceur", "name": "Coffret Douceur", "brand": "Lamysk Aura",
        "category": "ecrins", "notes": "Pour un sillage délicat et enveloppant",
        "variants": [("Coffret", 650, 15)]
    },
    {
        "slug": "coffret-mariee", "name": "Coffret Mariée", "brand": "Lamysk Aura",
        "category": "ecrins", "notes": "Le protocole complet pour le plus beau des jours",
        "variants": [("Coffret", 1200, 8)]
    },
    {
        "slug": "coffret-voyage", "name": "Coffret Voyage", "brand": "Lamysk Aura",
        "category": "ecrins", "notes": "L'essentiel du rituel en format nomade",
        "variants": [("Coffret", 550, 20)]
    },
    {
        "slug": "coffret-girly", "name": "Coffret Girly", "brand": "Lamysk Aura",
        "category": "ecrins", "notes": "Léger, pétillant, irrésistible",
        "variants": [("Coffret", 480, 18)]
    },
    # ── LES ESSENTIELS ────────────────────────────────────────────────────────
    {
        "slug": "musk", "name": "Musk", "brand": "Essential",
        "category": "essentiels", "notes": "Base de layering musc blanc",
        "variants": [("30ml", 180, 30)]
    },
    {
        "slug": "oud-base", "name": "Oud", "brand": "Essential",
        "category": "essentiels", "notes": "Base de layering oud pur",
        "variants": [("30ml", 220, 25)]
    },
    {
        "slug": "body-powder", "name": "Body Powder", "brand": "Essential",
        "category": "essentiels", "notes": "Talc parfumé pour la peau",
        "variants": [("150g", 150, 40)]
    },
    {
        "slug": "dehn", "name": "Dehn", "brand": "Essential",
        "category": "essentiels", "notes": "Huile parfumée concentrée",
        "variants": [("10ml", 250, 20)]
    },
    {
        "slug": "hair-mist", "name": "Hair Mist", "brand": "Essential",
        "category": "essentiels", "notes": "Voile parfumé pour les cheveux",
        "variants": [("100ml", 160, 35)]
    },
    {
        "slug": "body-lotion", "name": "Body Lotion", "brand": "Essential",
        "category": "essentiels", "notes": "Soin corporel parfumé",
        "variants": [("200ml", 170, 30)]
    },
]


async def seed():
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT COUNT(*) FROM products")
        count = (await cursor.fetchone())[0]
        if count > 0:
            print(f"⏭️  Database already has {count} products — skipping seed.")
            return

        for p in PRODUCTS:
            variants = p.pop("variants", [])
            cursor = await db.execute(
                """INSERT INTO products (slug, name, brand, category, notes, image_url, badge)
                   VALUES (:slug, :name, :brand, :category, :notes,
                           :image_url, :badge)""",
                {
                    "slug": p["slug"], "name": p["name"], "brand": p["brand"],
                    "category": p["category"], "notes": p.get("notes"),
                    "image_url": p.get("image_url"), "badge": p.get("badge")
                }
            )
            pid = cursor.lastrowid
            for size_label, price, stock in variants:
                await db.execute(
                    "INSERT INTO product_variants (product_id, size_label, price_mad, stock) VALUES (?,?,?,?)",
                    (pid, size_label, price, stock)
                )
        await db.commit()
        print(f"✅ Seeded {len(PRODUCTS)} products into the database.")


if __name__ == "__main__":
    asyncio.run(seed())
