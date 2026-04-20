"""
Seed v2 — full DB-driven product catalog with FR/AR/EN i18n.
Replaces the legacy seed.py. Run: python -m backend.services.seed_v2

WARNING: This wipes product_variants + products tables (preserves orders/users/etc).
Only run when you want a fresh import from this catalog.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import aiosqlite
from backend.database import init_db, DB_PATH


# ══════════════════════════════════════════════════════════════════════
# FULL CATALOG (51 products, grouped by carousel_slot)
# ══════════════════════════════════════════════════════════════════════
PRODUCTS = [
    # ── ORIENT · LAMYSK AURA SELECTION (house) ───────────────
    {
        "slug": "ibraq", "carousel_slot": "signature", "category": "orient",
        "price_mad": 490, "image_url": "images/hero_lamysk.jpg", "badge": "Orient",
        "fr": {"brand": "Lamysk Aura Selection", "name": "Ibraq",        "notes": "Oud · Ambre · Rose de Taïf"},
        "ar": {"brand": "لاميسك أورا",              "name": "إبراق",       "notes": "عود · عنبر · وردة الطائف"},
        "en": {"brand": "Lamysk Aura Selection", "name": "Ibraq",        "notes": "Oud · Amber · Taif Rose"},
    },

    # ── ORIENT · MATCH — Paris (8) ───────────────────────────
    {"slug":"match-mateir","carousel_slot":"match","category":"orient","price_mad":750,"image_url":"images/match_mateir.png","badge":"Orient",
        "fr":{"brand":"MATCH — Paris","name":"Mateir","notes":"Bois ambré · Épices · Musc"},
        "ar":{"brand":"MATCH — باريس","name":"مطير","notes":"خشب عنبري · توابل · مسك"},
        "en":{"brand":"MATCH — Paris","name":"Mateir","notes":"Amber Wood · Spices · Musk"}},
    {"slug":"match-mineral-oud","carousel_slot":"match","category":"orient","price_mad":780,"image_url":"images/match_mineral_oud.png",
        "fr":{"brand":"MATCH — Paris","name":"Mineral Oud","notes":"Oud · Minéral · Vétiver"},
        "ar":{"brand":"MATCH — باريس","name":"عود معدني","notes":"عود · معدني · فيتيفر"},
        "en":{"brand":"MATCH — Paris","name":"Mineral Oud","notes":"Oud · Mineral · Vetiver"}},
    {"slug":"match-lun-felyn","carousel_slot":"match","category":"orient","price_mad":720,"image_url":"images/match_lun_felyn.png",
        "fr":{"brand":"MATCH — Paris","name":"Lun Felyn","notes":"Floral poudré · Iris · Musc"},
        "ar":{"brand":"MATCH — باريس","name":"لون فيلين","notes":"زهري بودرة · سوسن · مسك"},
        "en":{"brand":"MATCH — Paris","name":"Lun Felyn","notes":"Powdery Floral · Iris · Musk"}},
    {"slug":"match-falkon-matir","carousel_slot":"match","category":"orient","price_mad":780,"image_url":"images/match_falkon_matir.png",
        "fr":{"brand":"MATCH — Paris","name":"Falkon Matir","notes":"Cuir · Safran · Oud"},
        "ar":{"brand":"MATCH — باريس","name":"فالكون ماطر","notes":"جلد · زعفران · عود"},
        "en":{"brand":"MATCH — Paris","name":"Falkon Matir","notes":"Leather · Saffron · Oud"}},
    {"slug":"match-komitt","carousel_slot":"match","category":"orient","price_mad":720,"image_url":"images/match_komitt.png",
        "fr":{"brand":"MATCH — Paris","name":"Komitt","notes":"Fruits noirs · Rose · Patchouli"},
        "ar":{"brand":"MATCH — باريس","name":"كوميت","notes":"فواكه سوداء · وردة · باتشولي"},
        "en":{"brand":"MATCH — Paris","name":"Komitt","notes":"Dark Fruits · Rose · Patchouli"}},
    {"slug":"match-boud-safron","carousel_slot":"match","category":"orient","price_mad":780,"image_url":"images/match_boud_safron.png",
        "fr":{"brand":"MATCH — Paris","name":"B'Oud Safron","notes":"Oud · Safran · Ambre"},
        "ar":{"brand":"MATCH — باريس","name":"بعود وزعفران","notes":"عود · زعفران · عنبر"},
        "en":{"brand":"MATCH — Paris","name":"B'Oud Safron","notes":"Oud · Saffron · Amber"}},
    {"slug":"match-silq-quin","carousel_slot":"match","category":"orient","price_mad":720,"image_url":"images/match_silq_quin.png",
        "fr":{"brand":"MATCH — Paris","name":"Silq Quin","notes":"Oud · Soie · Musc"},
        "ar":{"brand":"MATCH — باريس","name":"سلك كوين","notes":"عود · حرير · مسك"},
        "en":{"brand":"MATCH — Paris","name":"Silq Quin","notes":"Oud · Silk · Musk"}},
    {"slug":"match-leather","carousel_slot":"match","category":"orient","price_mad":780,"image_url":"images/match_leather.png",
        "fr":{"brand":"MATCH — Paris","name":"Leather","notes":"Cuir · Tabac · Bois fumés"},
        "ar":{"brand":"MATCH — باريس","name":"جلد","notes":"جلد · تبغ · أخشاب مدخّنة"},
        "en":{"brand":"MATCH — Paris","name":"Leather","notes":"Leather · Tobacco · Smoked Woods"}},

    # ── ORIENT · MATCH Musks — Paris (4) ──────────────────────
    {"slug":"musk-bridal","carousel_slot":"match_musks","category":"orient","price_mad":650,"image_url":"images/match_musk_bridal.png",
        "fr":{"brand":"MATCH Musks — Paris","name":"Bridal Musk","notes":"Musc blanc · Fleur d'oranger · Poudré"},
        "ar":{"brand":"MATCH Musks — باريس","name":"مسك العروس","notes":"مسك أبيض · زهر البرتقال · بودرة"},
        "en":{"brand":"MATCH Musks — Paris","name":"Bridal Musk","notes":"White Musk · Orange Blossom · Powdery"}},
    {"slug":"musk-lina","carousel_slot":"match_musks","category":"orient","price_mad":650,"image_url":"images/match_musk_lina.png",
        "fr":{"brand":"MATCH Musks — Paris","name":"Musk Lina","notes":"Musc · Rose · Pêche"},
        "ar":{"brand":"MATCH Musks — باريس","name":"مسك لينا","notes":"مسك · وردة · خوخ"},
        "en":{"brand":"MATCH Musks — Paris","name":"Musk Lina","notes":"Musk · Rose · Peach"}},
    {"slug":"musk-dvine","carousel_slot":"match_musks","category":"orient","price_mad":650,"image_url":"images/match_musk_dvine.png",
        "fr":{"brand":"MATCH Musks — Paris","name":"Musk Dvine","notes":"Musc · Oud · Safran"},
        "ar":{"brand":"MATCH Musks — باريس","name":"مسك ديفاين","notes":"مسك · عود · زعفران"},
        "en":{"brand":"MATCH Musks — Paris","name":"Musk Dvine","notes":"Musk · Oud · Saffron"}},
    {"slug":"musk-opiume","carousel_slot":"match_musks","category":"orient","price_mad":650,"image_url":"images/match_musk_opiume.png",
        "fr":{"brand":"MATCH Musks — Paris","name":"Musk Opiume","notes":"Musc · Opium · Ambre oriental"},
        "ar":{"brand":"MATCH Musks — باريس","name":"مسك أفيون","notes":"مسك · أفيون · عنبر شرقي"},
        "en":{"brand":"MATCH Musks — Paris","name":"Musk Opiume","notes":"Musk · Opium · Oriental Amber"}},

    # ── ORIENT · Lattafa — Dubaï (1) ──────────────────────────
    {"slug":"lattafa-sehr-alkalimat","carousel_slot":"lattafa","category":"orient","price_mad":550,"image_url":"images/lattafa_sehr_alkalimat.png",
        "fr":{"brand":"Lattafa — Dubaï","name":"Sehr Al Kalimat","notes":"Musc · Santal · Vanille"},
        "ar":{"brand":"لطافة — دبي","name":"سحر الكلمات","notes":"مسك · خشب الصندل · فانيليا"},
        "en":{"brand":"Lattafa — Dubai","name":"Sehr Al Kalimat","notes":"Musk · Sandalwood · Vanilla"}},

    # ── ORIENT · Arabian Oud — Riyad (6) ──────────────────────
    {"slug":"ao-woody-style","carousel_slot":"arabian_oud","category":"orient","price_mad":650,"image_url":"images/woody_style.png",
        "fr":{"brand":"Arabian Oud — Riyad","name":"Woody Style","notes":"Bois · Agrumes · Musc"},
        "ar":{"brand":"العربية للعود — الرياض","name":"وودي ستايل","notes":"خشب · حمضيات · مسك"},
        "en":{"brand":"Arabian Oud — Riyadh","name":"Woody Style","notes":"Wood · Citrus · Musk"}},
    {"slug":"ao-woody-intense","carousel_slot":"arabian_oud","category":"orient","price_mad":750,"image_url":"images/woody_intense.png",
        "fr":{"brand":"Arabian Oud — Riyad","name":"Woody Intense","notes":"Oud · Vétiver · Patchouli"},
        "ar":{"brand":"العربية للعود — الرياض","name":"وودي إنتنس","notes":"عود · فيتيفر · باتشولي"},
        "en":{"brand":"Arabian Oud — Riyadh","name":"Woody Intense","notes":"Oud · Vetiver · Patchouli"}},
    {"slug":"ao-rosewood","carousel_slot":"arabian_oud","category":"orient","price_mad":1100,"image_url":"images/arabian_oud_rosewood.png",
        "fr":{"brand":"Arabian Oud — Riyad","name":"Rosewood","notes":"Bois de rose · Oud · Ambre"},
        "ar":{"brand":"العربية للعود — الرياض","name":"خشب الورد","notes":"خشب الورد · عود · عنبر"},
        "en":{"brand":"Arabian Oud — Riyadh","name":"Rosewood","notes":"Rosewood · Oud · Amber"}},
    {"slug":"ao-saffron","carousel_slot":"arabian_oud","category":"orient","price_mad":950,"image_url":"images/arabian_oud_saffron.png",
        "fr":{"brand":"Arabian Oud — Riyad","name":"Saffron Oud","notes":"Safran · Oud · Rose"},
        "ar":{"brand":"العربية للعود — الرياض","name":"عود الزعفران","notes":"زعفران · عود · وردة"},
        "en":{"brand":"Arabian Oud — Riyadh","name":"Saffron Oud","notes":"Saffron · Oud · Rose"}},
    {"slug":"ao-musk-mubakhar","carousel_slot":"arabian_oud","category":"orient","price_mad":850,"image_url":"images/arabian_oud_musk_mubakhar.png",
        "fr":{"brand":"Arabian Oud — Riyad","name":"Musk Mubakhar","notes":"Musc · Bakhour · Poudré"},
        "ar":{"brand":"العربية للعود — الرياض","name":"مسك مبخّر","notes":"مسك · بخور · بودرة"},
        "en":{"brand":"Arabian Oud — Riyadh","name":"Musk Mubakhar","notes":"Musk · Bakhoor · Powdery"}},
    {"slug":"ao-vanilla-rose","carousel_slot":"arabian_oud","category":"orient","price_mad":950,"image_url":"images/arabian_oud_vanilla_rose.png",
        "fr":{"brand":"Arabian Oud — Riyad","name":"Vanilla Rose","notes":"Vanille · Rose · Ambre"},
        "ar":{"brand":"العربية للعود — الرياض","name":"وردة الفانيليا","notes":"فانيليا · وردة · عنبر"},
        "en":{"brand":"Arabian Oud — Riyadh","name":"Vanilla Rose","notes":"Vanilla · Rose · Amber"}},

    # ── ORIENT · Ghawali — by Ajmal (6) ───────────────────────
    {"slug":"gh-kin-musk","carousel_slot":"ghawali","category":"orient","price_mad":650,"image_url":"images/ghawali_kin_musk.png",
        "fr":{"brand":"Ghawali — by Ajmal","name":"Kin Musk","notes":"Musc · Cachemire · Blanc"},
        "ar":{"brand":"غوالي — من أجمل","name":"مسك العائلة","notes":"مسك · كشمير · أبيض"},
        "en":{"brand":"Ghawali — by Ajmal","name":"Kin Musk","notes":"Musk · Cashmere · White"}},
    {"slug":"gh-untold","carousel_slot":"ghawali","category":"orient","price_mad":700,"image_url":"images/ghawali_untold.png",
        "fr":{"brand":"Ghawali — by Ajmal","name":"Untold","notes":"Oud · Safran · Patchouli"},
        "ar":{"brand":"غوالي — من أجمل","name":"أنتولد","notes":"عود · زعفران · باتشولي"},
        "en":{"brand":"Ghawali — by Ajmal","name":"Untold","notes":"Oud · Saffron · Patchouli"}},
    {"slug":"gh-dusk","carousel_slot":"ghawali","category":"orient","price_mad":720,"image_url":"images/ghawali_dusk_outro.png",
        "fr":{"brand":"Ghawali — by Ajmal","name":"Dusk Outro","notes":"Ambre · Vanille · Bois"},
        "ar":{"brand":"غوالي — من أجمل","name":"دسك أوترو","notes":"عنبر · فانيليا · خشب"},
        "en":{"brand":"Ghawali — by Ajmal","name":"Dusk Outro","notes":"Amber · Vanilla · Woods"}},
    {"slug":"gh-love-note","carousel_slot":"ghawali","category":"orient","price_mad":650,"image_url":"images/ghawali_love_note.png",
        "fr":{"brand":"Ghawali — by Ajmal","name":"Love Note","notes":"Rose · Musc · Poudré"},
        "ar":{"brand":"غوالي — من أجمل","name":"نغمة حب","notes":"وردة · مسك · بودرة"},
        "en":{"brand":"Ghawali — by Ajmal","name":"Love Note","notes":"Rose · Musk · Powdery"}},
    {"slug":"gh-last-date","carousel_slot":"ghawali","category":"orient","price_mad":700,"image_url":"images/ghawali_last_date.png",
        "fr":{"brand":"Ghawali — by Ajmal","name":"Last Date","notes":"Dattes · Miel · Oud"},
        "ar":{"brand":"غوالي — من أجمل","name":"آخر تمر","notes":"تمر · عسل · عود"},
        "en":{"brand":"Ghawali — by Ajmal","name":"Last Date","notes":"Dates · Honey · Oud"}},
    {"slug":"gh-9pm","carousel_slot":"ghawali","category":"orient","price_mad":780,"image_url":"images/ghawali_9pm_saudi.png",
        "fr":{"brand":"Ghawali — by Ajmal","name":"9 P.M. Saudi","notes":"Oud · Ambre · Safran"},
        "ar":{"brand":"غوالي — من أجمل","name":"٩ مساءً — سعودي","notes":"عود · عنبر · زعفران"},
        "en":{"brand":"Ghawali — by Ajmal","name":"9 P.M. Saudi","notes":"Oud · Amber · Saffron"}},

    # ── OCCIDENT · Rosendo Mateu — Barcelone (3) ─────────────
    {"slug":"rm-n5-parfum","carousel_slot":"niche","category":"occident","price_mad":1700,"image_url":"images/rosendo_n5_parfum.png",
        "fr":{"brand":"Rosendo Mateu — Barcelone","name":"N°5 Parfum","notes":"Floral · Ambré · Musc sensuel"},
        "ar":{"brand":"روسيندو ماتيو — برشلونة","name":"رقم ٥ — عطر","notes":"زهري · عنبري · مسك حسي"},
        "en":{"brand":"Rosendo Mateu — Barcelona","name":"N°5 Parfum","notes":"Floral · Amber · Sensual Musk"}},
    {"slug":"rm-n5-hair","carousel_slot":"niche","category":"occident","price_mad":1400,"image_url":"images/Rosendo_Mateu.jpg","badge":"Occident",
        "fr":{"brand":"Rosendo Mateu — Barcelone","name":"N°5 Hair Perfume","notes":"Floral · Ambré · Musc sensuel"},
        "ar":{"brand":"روسيندو ماتيو — برشلونة","name":"رقم ٥ — عطر الشعر","notes":"زهري · عنبري · مسك حسي"},
        "en":{"brand":"Rosendo Mateu — Barcelona","name":"N°5 Hair Perfume","notes":"Floral · Amber · Sensual Musk"}},
    {"slug":"rm-n7-pov","carousel_slot":"niche","category":"occident","price_mad":1800,"image_url":"images/Rosendo_Mateu.jpg",
        "fr":{"brand":"Rosendo Mateu — Barcelone","name":"N°7 Patchouli Oud Vanilla","notes":"Oud · Patchouli · Vanille"},
        "ar":{"brand":"روسيندو ماتيو — برشلونة","name":"رقم ٧ — باتشولي عود فانيليا","notes":"عود · باتشولي · فانيليا"},
        "en":{"brand":"Rosendo Mateu — Barcelona","name":"N°7 Patchouli Oud Vanilla","notes":"Oud · Patchouli · Vanilla"}},

    # ── OCCIDENT · Niche (7) ─────────────────────────────────
    {"slug":"lelabo-santal-33","carousel_slot":"niche","category":"occident","price_mad":950,"image_url":"images/Santal_33_large.jpg",
        "fr":{"brand":"Le Labo — New York","name":"Santal 33","notes":"Santal · Cèdre · Cuir"},
        "ar":{"brand":"لي لابو — نيويورك","name":"صندل ٣٣","notes":"خشب الصندل · أرز · جلد"},
        "en":{"brand":"Le Labo — New York","name":"Santal 33","notes":"Sandalwood · Cedar · Leather"}},
    {"slug":"byredo-gypsy-water","carousel_slot":"niche","category":"occident","price_mad":880,"image_url":"images/Gypsy_Water.jpg",
        "fr":{"brand":"Byredo — Stockholm","name":"Gypsy Water","notes":"Pin · Bergamote · Ambre"},
        "ar":{"brand":"بيريدو — ستوكهولم","name":"جيبسي ووتر","notes":"صنوبر · برغموت · عنبر"},
        "en":{"brand":"Byredo — Stockholm","name":"Gypsy Water","notes":"Pine · Bergamot · Amber"}},
    {"slug":"tf-tobacco-vanille","carousel_slot":"niche","category":"occident","price_mad":1100,"image_url":"images/Tobacco_Vanille.jpg",
        "fr":{"brand":"Tom Ford — New York","name":"Tobacco Vanille","notes":"Tabac · Vanille · Épices"},
        "ar":{"brand":"توم فورد — نيويورك","name":"تبغ وفانيليا","notes":"تبغ · فانيليا · توابل"},
        "en":{"brand":"Tom Ford — New York","name":"Tobacco Vanille","notes":"Tobacco · Vanilla · Spices"}},
    {"slug":"jomalone-halfeti","carousel_slot":"niche","category":"occident","price_mad":820,"image_url":"images/Halfeti.jpg",
        "fr":{"brand":"Jo Malone — Londres","name":"Halfeti","notes":"Rose noire · Cèdre · Ambre"},
        "ar":{"brand":"جو مالون — لندن","name":"حلفتي","notes":"وردة سوداء · أرز · عنبر"},
        "en":{"brand":"Jo Malone — London","name":"Halfeti","notes":"Black Rose · Cedar · Amber"}},
    {"slug":"diptyque-tam-dao","carousel_slot":"niche","category":"occident","price_mad":780,"image_url":"images/Tam_Dao.jpg",
        "fr":{"brand":"Diptyque — Paris","name":"Tam Dao","notes":"Santal · Cyprès · Cèdre"},
        "ar":{"brand":"ديبتيك — باريس","name":"تام داو","notes":"خشب الصندل · سرو · أرز"},
        "en":{"brand":"Diptyque — Paris","name":"Tam Dao","notes":"Sandalwood · Cypress · Cedar"}},
    {"slug":"diptyque-do-son","carousel_slot":"niche","category":"occident","price_mad":720,"image_url":"images/Do_Son.jpg",
        "fr":{"brand":"Diptyque — Paris","name":"Do Son","notes":"Tubéreuse · Jasmin · Musc"},
        "ar":{"brand":"ديبتيك — باريس","name":"دو سون","notes":"توبيروز · ياسمين · مسك"},
        "en":{"brand":"Diptyque — Paris","name":"Do Son","notes":"Tuberose · Jasmine · Musk"}},
    {"slug":"molecule-01","carousel_slot":"niche","category":"occident","price_mad":690,"image_url":"images/Molecule_01.jpg",
        "fr":{"brand":"Escentric Molecules — Berlin","name":"Molecule 01","notes":"Iso E Super · Boisé · Sensuel"},
        "ar":{"brand":"إسنتريك موليكيولز — برلين","name":"موليكيول ٠١","notes":"إيزو إي سوبر · خشبي · حسي"},
        "en":{"brand":"Escentric Molecules — Berlin","name":"Molecule 01","notes":"Iso E Super · Woody · Sensual"}},

    # ── ABSOLUS · Thomas Kosmala & haute-niche (8) ───────────
    {"slug":"tk-n4","carousel_slot":"absolus","category":"absolus","price_mad":1450,"image_url":"images/thomas_kosmala_n4.png","badge":"Absolu",
        "fr":{"brand":"Thomas Kosmala — Paris","name":"N°4 Après l'Amour","notes":"Néroli · Musc · Ambre"},
        "ar":{"brand":"توماس كوسمالا — باريس","name":"رقم ٤ — ما بعد الحب","notes":"نيرولي · مسك · عنبر"},
        "en":{"brand":"Thomas Kosmala — Paris","name":"N°4 After Love","notes":"Neroli · Musk · Amber"}},
    {"slug":"tk-n9","carousel_slot":"absolus","category":"absolus","price_mad":1650,"image_url":"images/thomas_kosmala_n9_bukhoor.png","badge":"Absolu",
        "fr":{"brand":"Thomas Kosmala — Paris","name":"N°9 Bukhoor Elixir","notes":"Bakhoor · Oud · Ambre"},
        "ar":{"brand":"توماس كوسمالا — باريس","name":"رقم ٩ — إكسير البخور","notes":"بخور · عود · عنبر"},
        "en":{"brand":"Thomas Kosmala — Paris","name":"N°9 Bukhoor Elixir","notes":"Bakhoor · Oud · Amber"}},
    {"slug":"fm-portrait-lady","carousel_slot":"absolus","category":"absolus","price_mad":2200,"image_url":None,"badge":"Absolu",
        "fr":{"brand":"Frédéric Malle — Paris","name":"Portrait of a Lady","notes":"Rose · Patchouli · Encens"},
        "ar":{"brand":"فريدريك مال — باريس","name":"بورتريه ليدي","notes":"وردة · باتشولي · بخور"},
        "en":{"brand":"Frédéric Malle — Paris","name":"Portrait of a Lady","notes":"Rose · Patchouli · Incense"}},
    {"slug":"mfk-oud-satin-mood","carousel_slot":"absolus","category":"absolus","price_mad":1950,"image_url":None,
        "fr":{"brand":"Maison Francis Kurkdjian — Paris","name":"Oud Satin Mood","notes":"Oud · Rose · Vanille"},
        "ar":{"brand":"ميزون فرانسيس كوركدجان — باريس","name":"عود ساتان مود","notes":"عود · وردة · فانيليا"},
        "en":{"brand":"Maison Francis Kurkdjian — Paris","name":"Oud Satin Mood","notes":"Oud · Rose · Vanilla"}},
    {"slug":"kilian-beyond-love","carousel_slot":"absolus","category":"absolus","price_mad":1800,"image_url":None,
        "fr":{"brand":"By Kilian — Paris","name":"Beyond Love","notes":"Tubéreuse · Jasmin · Santal"},
        "ar":{"brand":"باي كيليان — باريس","name":"بيوند لوف","notes":"توبيروز · ياسمين · خشب الصندل"},
        "en":{"brand":"By Kilian — Paris","name":"Beyond Love","notes":"Tuberose · Jasmine · Sandalwood"}},
    {"slug":"fm-carnal-flower","carousel_slot":"absolus","category":"absolus","price_mad":2100,"image_url":"images/Coffret_Noblesse.jpg",
        "fr":{"brand":"Frédéric Malle — Paris","name":"Carnal Flower","notes":"Tubéreuse · Jasmin · Santal"},
        "ar":{"brand":"فريدريك مال — باريس","name":"كارنال فلاور","notes":"توبيروز · ياسمين · خشب الصندل"},
        "en":{"brand":"Frédéric Malle — Paris","name":"Carnal Flower","notes":"Tuberose · Jasmine · Sandalwood"}},
    {"slug":"lutens-ambre-sultan","carousel_slot":"absolus","category":"absolus","price_mad":1650,"image_url":"images/Coffret_Noblesse.jpg",
        "fr":{"brand":"Serge Lutens — Paris","name":"Ambre Sultan","notes":"Ambre · Résine · Santal"},
        "ar":{"brand":"سيرج لوتنس — باريس","name":"عنبر السلطان","notes":"عنبر · راتنج · خشب الصندل"},
        "en":{"brand":"Serge Lutens — Paris","name":"Ambre Sultan","notes":"Amber · Resin · Sandalwood"}},
    {"slug":"fm-musc-ravageur","carousel_slot":"absolus","category":"absolus","price_mad":2000,"image_url":"images/Coffret_Noblesse.jpg",
        "fr":{"brand":"Frédéric Malle — Paris","name":"Musc Ravageur","notes":"Musc · Ambre · Vanille"},
        "ar":{"brand":"فريدريك مال — باريس","name":"مسك رافاجور","notes":"مسك · عنبر · فانيليا"},
        "en":{"brand":"Frédéric Malle — Paris","name":"Musc Ravageur","notes":"Musk · Amber · Vanilla"}},

    # ── ESSENTIELS · layering bases (6) ──────────────────────
    {"slug":"ess-musk","carousel_slot":"essentiels","category":"essentiels","price_mad":180,"image_url":None,
        "fr":{"brand":"Essential","name":"Musk","notes":"Base de layering musc blanc"},
        "ar":{"brand":"إسنشال","name":"مسك","notes":"قاعدة تركيب مسك أبيض"},
        "en":{"brand":"Essential","name":"Musk","notes":"White musk layering base"}},
    {"slug":"ess-oud","carousel_slot":"essentiels","category":"essentiels","price_mad":220,"image_url":None,
        "fr":{"brand":"Essential","name":"Oud","notes":"Base de layering oud pur"},
        "ar":{"brand":"إسنشال","name":"عود","notes":"قاعدة تركيب عود خالص"},
        "en":{"brand":"Essential","name":"Oud","notes":"Pure oud layering base"}},
    {"slug":"ess-body-powder","carousel_slot":"essentiels","category":"essentiels","price_mad":150,"image_url":None,
        "fr":{"brand":"Essential","name":"Body Powder","notes":"Talc parfumé pour la peau"},
        "ar":{"brand":"إسنشال","name":"بودرة الجسم","notes":"بودرة معطرة للجسم"},
        "en":{"brand":"Essential","name":"Body Powder","notes":"Scented body talc"}},
    {"slug":"ess-dehn","carousel_slot":"essentiels","category":"essentiels","price_mad":250,"image_url":None,
        "fr":{"brand":"Essential","name":"Dehn","notes":"Huile parfumée concentrée"},
        "ar":{"brand":"إسنشال","name":"دهن","notes":"زيت عطري مركّز"},
        "en":{"brand":"Essential","name":"Dehn","notes":"Concentrated perfume oil"}},
    {"slug":"ess-hair-mist","carousel_slot":"essentiels","category":"essentiels","price_mad":160,"image_url":None,
        "fr":{"brand":"Essential","name":"Hair Mist","notes":"Voile parfumé pour les cheveux"},
        "ar":{"brand":"إسنشال","name":"معطر الشعر","notes":"رذاذ معطر للشعر"},
        "en":{"brand":"Essential","name":"Hair Mist","notes":"Scented hair veil"}},
    {"slug":"ess-body-lotion","carousel_slot":"essentiels","category":"essentiels","price_mad":170,"image_url":None,
        "fr":{"brand":"Essential","name":"Body Lotion","notes":"Soin corporel parfumé"},
        "ar":{"brand":"إسنشال","name":"مرطب الجسم","notes":"مرطب معطر للجسم"},
        "en":{"brand":"Essential","name":"Body Lotion","notes":"Scented body lotion"}},
]


# ══════════════════════════════════════════════════════════════════════
# UI STRINGS — seed from index.html LANG dict (essential keys only)
# Full migration to DB happens in a separate step (ui_strings table).
# ══════════════════════════════════════════════════════════════════════
UI_STRINGS_MINIMAL = [
    # Only a few placeholder keys — the real LANG dict remains in index.html
    # until the frontend fetch migration is done.
    ("quiz_parfums_title", "hero",
        "Parfums qui vous correspondent",
        "عطور تناسب ملفكِ",
        "Fragrances that match your profile"),
]


async def wipe_and_seed():
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys=ON")

        # ── Detach order_items from products/variants ───────
        # (orders retain denormalized name/brand/unit_price, so FKs are disposable)
        await db.execute("UPDATE order_items SET product_id = NULL, variant_id = NULL")
        await db.execute("UPDATE user_wishlists SET product_name = product_name")  # noop, no-op

        # ── Wipe products + variants (orders preserved) ──────
        await db.execute("DELETE FROM product_variants")
        await db.execute("DELETE FROM products")
        await db.execute("DELETE FROM sqlite_sequence WHERE name IN ('products','product_variants')")

        # ── Insert products ──────────────────────────────────
        for i, p in enumerate(PRODUCTS):
            await db.execute("""
                INSERT INTO products (
                    slug, name, brand, category, carousel_slot,
                    notes, image_url, badge, price_mad, sort_order,
                    brand_fr, brand_ar, brand_en,
                    name_fr,  name_ar,  name_en,
                    notes_fr, notes_ar, notes_en,
                    active
                ) VALUES (
                    :slug, :name, :brand, :category, :carousel_slot,
                    :notes, :image_url, :badge, :price_mad, :sort_order,
                    :brand_fr, :brand_ar, :brand_en,
                    :name_fr,  :name_ar,  :name_en,
                    :notes_fr, :notes_ar, :notes_en,
                    1
                )
            """, {
                "slug": p["slug"],
                "name": p["fr"]["name"],                    # legacy field = FR
                "brand": p["fr"]["brand"],                  # legacy field = FR
                "category": p["category"],
                "carousel_slot": p["carousel_slot"],
                "notes": p["fr"]["notes"],                  # legacy field = FR
                "image_url": p.get("image_url"),
                "badge": p.get("badge"),
                "price_mad": p["price_mad"],
                "sort_order": i,
                "brand_fr": p["fr"]["brand"], "brand_ar": p["ar"]["brand"], "brand_en": p["en"]["brand"],
                "name_fr":  p["fr"]["name"],  "name_ar":  p["ar"]["name"],  "name_en":  p["en"]["name"],
                "notes_fr": p["fr"]["notes"], "notes_ar": p["ar"]["notes"], "notes_en": p["en"]["notes"],
            })

        # ── Upsert UI strings ────────────────────────────────
        for key, group, fr, ar, en in UI_STRINGS_MINIMAL:
            await db.execute("""
                INSERT INTO ui_strings (key, fr, ar, en, group_name)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    fr=excluded.fr, ar=excluded.ar, en=excluded.en,
                    group_name=excluded.group_name,
                    updated_at=datetime('now')
            """, (key, fr, ar, en, group))

        await db.commit()
        print(f"✅ Seeded {len(PRODUCTS)} products + {len(UI_STRINGS_MINIMAL)} UI strings")


if __name__ == "__main__":
    asyncio.run(wipe_and_seed())
