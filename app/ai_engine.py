import os
import json
import re
from typing import Dict, Any, List, Optional

# Try loading Gemini SDK if available
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_gemini_client(api_key: Optional[str] = None):
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key and HAS_GENAI:
        try:
            return genai.Client(api_key=key)
        except Exception as e:
            print("Failed to initialize Gemini client:", e)
    return None

# ==========================================
# 1. CURATED RURAL MICRO-ENTERPRISE DATABASE
# ==========================================
RURAL_BUSINESS_CATALOG = [
    {
        "id": "country_poultry",
        "title": "Free-Range Country Chicken Rearing",
        "ta_title": "நாட்டுக்கோழி வளர்ப்பு",
        "category": "Livestock & Poultry",
        "ta_category": "கால்நடை & கோழி வளர்ப்பு",
        "min_budget": 15000,
        "max_budget": 50000,
        "typical_budget": 25000,
        "location_types": ["Village", "Panchayat", "Semi-Urban"],
        "skills_required": ["Livestock Care", "Basic Feeding & Vaccination", "Local Selling"],
        "materials": [
            {"item": "Night shelter fencing / wire mesh shed", "ta_item": "பாதுகாப்பான கம்பி வலை கொட்டகை அமைப்பு", "cost": 8000},
            {"item": "50 Day-old Country chicks (Asil / Giriraja / Kaveri)", "ta_item": "50 நாட்டுக்கோழி குஞ்சுகள் (அசில் / கிரிராஜா)", "cost": 3500},
            {"item": "Feed (Corn, Azolla, broken grains) for 3 months", "ta_item": "3 மாதங்களுக்கான மக்காச்சோளம், அசோலா தீவனம்", "cost": 7500},
            {"item": "Feeders, Drinkers & Basic medicines", "ta_item": "தீவன தட்டுகள், தண்ணீர் குடுவைகள் & மருந்துகள்", "cost": 3000},
            {"item": "Emergency contingency buffer", "ta_item": "அவசர கையிருப்பு நிதி", "cost": 3000}
        ],
        "timeline": "3 to 4 months for first cycle",
        "ta_timeline": "முதல் சுழற்சிக்கு 3 முதல் 4 மாதங்கள்",
        "monthly_potential_net": 12000,
        "description": "High demand in local weekly shandies (சந்தை) and urban fringes for organic country eggs and live meat with premium pricing over broiler chickens.",
        "steps": [
            "1. Erect a simple predator-proof coop (150 sq ft) with local bamboo and wire mesh.",
            "2. Procure vaccinated 1-day or 2-week-old chicks from government KVK or registered breeders.",
            "3. Establish Azolla green fodder pit to reduce feed costs by 35%.",
            "4. Follow Newcastle (Ranikhet) vaccination schedule at day 7 and day 28.",
            "5. Market live birds directly to local households and butcher shops at 90-120 days."
        ],
        "ta_description": "கிராமப்புற மற்றும் நகர பகுதிகளில் நாட்டுக்கோழி இறைச்சி மற்றும் முட்டைக்கு அதிக மவுசு உள்ளது. குறைந்த முதலீட்டில் சிறந்த லாபம் தரும் தொழில்.",
        "ta_steps": [
            "1. பனை ஓலை அல்லது கம்பி வலை கொண்டு பாதுகாப்பான எளிய கொட்டகை அமைத்தல்.",
            "2. தமிழ்நாடு கால்நடை பல்கலைக்கழகம் அல்லது KVK-யில் தரமான குஞ்சுகளை வாங்குதல்.",
            "3. தீவனச் செலவைக் குறைக்க அசோலா மற்றும் தானியங்களை உணவாக அளித்தல்.",
            "4. வெள்ளைக்கழிச்சல் (Ranikhet) போன்ற தடுப்பூசிகளை குறிப்பிட்ட காலத்தில் போடுதல்.",
            "5. உள்ளூர் வாரச் சந்தை மற்றும் நேரடி வாடிக்கையாளர்களுக்கு விற்பனை செய்தல்."
        ]
    },
    {
        "id": "millet_value_added",
        "title": "Millet Snacks & Flour Processing",
        "ta_title": "சிறுதானிய உணவு & மாவு தயாரிப்பு",
        "category": "Food & Snacks",
        "ta_category": "உணவு & தின்பண்டங்கள்",
        "min_budget": 20000,
        "max_budget": 80000,
        "typical_budget": 35000,
        "location_types": ["Village", "Panchayat", "Town"],
        "skills_required": ["Cooking / Food Prep", "Hygiene & Packaging", "Direct Marketing"],
        "materials": [
            {"item": "Tabletop commercial flour mill / pulverizer", "ta_item": "மேஜை அளவு வணிக மாவு அரைக்கும் இயந்திரம்", "cost": 16000},
            {"item": "Raw millets (Ragi, Kambu, Thinai, Samai) bulk stock", "ta_item": "முழு சிறுதானியங்கள் (கம்பு, ராகி, தினை, சாமை) இருப்பு", "cost": 9000},
            {"item": "Food-grade standup pouches & impulse heat sealer", "ta_item": "உணவுத் தர ஜிப் பாக்கெட்டுகள் & சீலிங் மெஷின்", "cost": 4000},
            {"item": "FSSAI registration & label printing", "ta_item": "FSSAI உணவு உரிமம் & லேபிள் அச்சிடுதல்", "cost": 3000},
            {"item": "Working capital for packaging & ingredients", "ta_item": "நடைமுறை மூலதனம் மற்றும் அவசர கையிருப்பு", "cost": 3000}
        ],
        "timeline": "2 weeks to launch",
        "ta_timeline": "2 வாரங்களில் தொடங்கலாம்",
        "monthly_potential_net": 18000,
        "description": "High-margin health products including sprouted ragi mix, multi-millet idli podi, kambu cookies, and diabetes-friendly ready-to-cook flours.",
        "steps": [
            "1. Obtain basic FSSAI micro-enterprise registration online (₹100/yr).",
            "2. Source cleaned whole millets directly from farmer producer organizations (FPOs).",
            "3. Sprout, dry, and mill nutritious grains under strict hygienic conditions.",
            "4. Package in moisture-proof zip pouches with nutrition and recipe labels.",
            "5. Supply to local grocery stores, teachers, self-help groups, and weekly markets."
        ],
        "ta_description": "சிறுதானிய சத்துணவு மற்றும் தின்பண்டங்களுக்கு தற்போது மக்களிடையே பெரும் வரவேற்பு உள்ளது. கிராமத்து தரமான தானியங்களைக் கொண்டு அதிக லாபம் ஈட்டலாம்.",
        "ta_steps": [
            "1. FSSAI உணவுப் பாதுகாப்பு இணையதளத்தில் அடிப்படை பதிவு பெறுதல்.",
            "2. உள்ளூர் உழவர்களிடம் இருந்து கம்பு, கேழ்வரகு, தினை தானியங்களை கொள்முதல் செய்தல்.",
            "3. தானியங்களை முளைக்கட்டி, உலர்த்தி சுகாதாரமான முறையில் மாவாக அரைத்தல்.",
            "4. கவர்ச்சிகரமான ஜிப்-லாக் பாக்கெட்டுகளில் பெயர் லேபிள் ஒட்டி பேக் செய்தல்.",
            "5. அருகில் உள்ள மளிகை கடைகள் மற்றும் சமூக வலைத்தளங்கள் வழியே விற்பனை செய்தல்."
        ]
    },
    {
        "id": "tailoring_aari_work",
        "title": "Village Boutique, Tailoring & Aari Embroidery",
        "ta_title": "தையல் & ஆரி எம்பிராய்டரி மையம்",
        "category": "Tailoring & Crafts",
        "ta_category": "தையல் & கைவினை கலை",
        "min_budget": 10000,
        "max_budget": 45000,
        "typical_budget": 22000,
        "location_types": ["Village", "Panchayat", "Town"],
        "skills_required": ["Sewing / Stitching", "Pattern Cutting", "Aari / Bead Work"],
        "materials": [
            {"item": "Semi-industrial motorized sewing machine", "ta_item": "மோட்டார் பொருத்தப்பட்ட நவீன தையல் இயந்திரம்", "cost": 11500},
            {"item": "Aari stand, needle set, beads, zardozi, silk threads", "ta_item": "ஆரி ஸ்டாண்ட், ஊசிகள், மணிகள் & பட்டு நூல்கள்", "cost": 3500},
            {"item": "Cutting table, specialized tailoring scissors, rulers", "ta_item": "துணி வெட்டும் மேசை, கத்தரிக்கோல் & அளவுகோல்", "cost": 2500},
            {"item": "Threads, canvas, zips, lining cloth inventory", "ta_item": "லைனிங் துணிகள், கேன்வாஸ் & ஜிப் இருப்பு", "cost": 2500},
            {"item": "Shop banner, display stand and iron box", "ta_item": "பெயர் பலகை, இஸ்திரி பெட்டி & டிஸ்ப்ளே ஸ்டாண்ட்", "cost": 2000}
        ],
        "timeline": "Immediate start",
        "ta_timeline": "உடனடியாக தொடங்கலாம்",
        "monthly_potential_net": 15000,
        "description": "High sustained demand for school uniforms, custom bridal blouse aari work, salwar suits, and alterations across all village communities.",
        "steps": [
            "1. Setup a dedicated well-lit workspace at home or village junction.",
            "2. Display catalogue samples of trending blouse neckline designs and Aari motifs.",
            "3. Offer guaranteed on-time delivery for local festivals and weddings.",
            "4. Partner with local cloth merchants to receive referral stitching orders.",
            "5. Train village girls as apprentices to scale output during peak wedding seasons."
        ],
        "ta_description": "திருமணங்கள் மற்றும் பண்டிகை காலங்களில் ஜாக்கெட், சுடிதார் மற்றும் ஆரி வேலைப்பாடுகளுக்கு எப்போதும் கிராக்கி உண்டு. பெண்கள் வீட்டில் இருந்தே செய்யலாம்.",
        "ta_steps": [
            "1. வீட்டில் அல்லது சந்தை பகுதியில் தையல் இயந்திரம் மற்றும் மேசையை அமைத்தல்.",
            "2. புதிய மாடல் கழுத்து டிசைன்கள் மற்றும் ஆரி வேலை மாதிரிகளை காட்சிப்படுத்துதல்.",
            "3. குறித்த நேரத்தில் துணிகளை தைத்து கொடுத்து வாடிக்கையாளர் நம்பிக்கையை பெறுதல்.",
            "4. உள்ளூர் துணிக்கடைகளுடன் இணைந்து தையல் ஆர்டர்களை பெறுதல்.",
            "5. முகூர்த்த மற்றும் தீபாவளி நாட்களில் கூடுதல் உதவியாளர்களுடன் உற்பத்தி பெருக்குதல்."
        ]
    },
    {
        "id": "areca_leaf_plates",
        "title": "Eco-Friendly Areca Nut Leaf Plate Making",
        "ta_title": "பாக்கு மட்டை தட்டு தயாரிப்பு",
        "category": "Green Manufacturing",
        "ta_category": "சுற்றுச்சூழல் உற்பத்தி தொழில்",
        "min_budget": 40000,
        "max_budget": 150000,
        "typical_budget": 75000,
        "location_types": ["Village", "Panchayat"],
        "skills_required": ["Machine Operation", "Leaf Sorting & Cleaning", "Packing"],
        "materials": [
            {"item": "Hydraulic or manual dual-die heated press machine", "ta_item": "இரட்டை டை சூடேற்றப்படும் பாக்கு மட்டை இயந்திரம்", "cost": 45000},
            {"item": "Raw areca sheath leaves stock (5,000 pieces)", "ta_item": "5,000 சுத்தமான பாக்கு மட்டைகள் இருப்பு", "cost": 15000},
            {"item": "Washing tubs, drying racks, pressure nozzle", "ta_item": "கழுவும் தொட்டிகள், உலர்த்தும் ரேக்குகள்", "cost": 4000},
            {"item": "Shrink wrap machine & packaging cartons", "ta_item": "ஷிரிங்க் பேக்கிங் மெஷின் & அட்டைப்பெட்டிகள்", "cost": 5000},
            {"item": "Single phase electrical wiring & backup buffer", "ta_item": "மின் இணைப்பு மற்றும் அவசர இருப்பு நிதி", "cost": 6000}
        ],
        "timeline": "3 to 4 weeks",
        "ta_timeline": "3 முதல் 4 வாரங்கள்",
        "monthly_potential_net": 28000,
        "description": "100% biodegradable plates, bowls and spoons in high demand across temple functions, catering events, marriage halls, and eco-cafes.",
        "steps": [
            "1. Procure collected areca sheaths from plantations in Salem, Coimbatore, or Shimoga.",
            "2. Clean sheaths in fresh water, scrub dirt, and sun-dry to optimal moisture level.",
            "3. Press into round plates (10\", 12\") and curry bowls using heated metal dies (150°C).",
            "4. Trim edges smoothly, UV-sanitize, and shrink-pack in packs of 25.",
            "5. Sell in bulk to local caterers, temple trusts, and party supply wholesalers."
        ],
        "ta_description": "பிளாஸ்டிக் தடைக்கு பின் பாக்கு மட்டை தட்டுகளுக்கு பெரும் வரவேற்பு உள்ளது. திருமண மண்டபங்கள் மற்றும் விழாக்களுக்கு மொத்தமாக விற்கலாம்.",
        "ta_steps": [
            "1. தோட்டங்களில் இருந்து தரமான உதிர்ந்த பாக்கு மட்டைகளை மொத்தமாக வாங்குதல்.",
            "2. மட்டைகளை தண்ணீரில் ஊறவைத்து, சுத்தம் செய்து நிழலில் உலர்த்துதல்.",
            "3. அச்சு இயந்திரத்தில் சூடான டை மூலம் தட்டுகள் மற்றும் கிண்ணங்களாக அழுத்துதல்.",
            "4. ஓரங்களை நேர்த்தியாக வெட்டி, 25 தட்டுகள் வீதம் பாலித்தீன் கவரில் பேக் செய்தல்.",
            "5. திருமண சமையல் ஒப்பந்ததாரர்கள் மற்றும் மொத்த வியாபாரிகளுக்கு சப்ளை செய்தல்."
        ]
    },
    {
        "id": "organic_vermicompost",
        "title": "Bio-Fertilizer & Vermicompost Unit",
        "ta_title": "மண்புழு உரம் & இயற்கை இடுபொருட்கள்",
        "category": "Agriculture & Organic Inputs",
        "ta_category": "இயற்கை விவசாய உரம்",
        "min_budget": 12000,
        "max_budget": 40000,
        "typical_budget": 18000,
        "location_types": ["Village", "Panchayat"],
        "skills_required": ["Organic Waste Handling", "Moisture Monitoring", "Packing"],
        "materials": [
            {"item": "HDPE Vermi-beds (2 portable units)", "ta_item": "2 கையடக்க HDPE மண்புழு உர படுக்கைகள்", "cost": 5000},
            {"item": "Eisenia Foetida / Eudrilus earthworm mother culture (5 kg)", "ta_item": "5 கிலோ தாய் மண்புழுக்கள் (Eisenia Foetida)", "cost": 2500},
            {"item": "Cow dung, agricultural crop residues, farm waste", "ta_item": "மாட்டுச் சாணம் மற்றும் விவசாய பண்ணை கழிவுகள்", "cost": 3500},
            {"item": "Water sprinkler pipe, shade net, and thermohygrometer", "ta_item": "நீர் தெளிப்பான், நிழல் வலை & ஈரப்பதமானி", "cost": 3000},
            {"item": "Sieving screen, 5kg/25kg bags & stitching machine", "ta_item": "உரம் சல்லடை, அச்சிட்ட பைகள் & தைக்கும் ஊசி", "cost": 4000}
        ],
        "timeline": "45 to 60 days per harvest",
        "ta_timeline": "45 முதல் 60 நாட்களில் உரம் தயார்",
        "monthly_potential_net": 14000,
        "description": "Low capital, high recurring return converting farm waste and cow dung into black gold vermicompost for organic farmers and rooftop gardeners.",
        "steps": [
            "1. Assemble portable HDPE vermibeds under tree canopy or 50% shade net.",
            "2. Layer dry biomass, semi-decomposed cow dung, and sprinkle water to 60% moisture.",
            "3. Introduce red wigglers (earthworms) and protect from ants with turmeric/water moat.",
            "4. Harvest granular black vermicompost every 45-60 days and separate worm cocoons.",
            "5. Pack in printed woven sacks and supply to organic farmers, nurseries, and plant stores."
        ],
        "ta_description": "மாட்டுச் சாணம் மற்றும் விவசாய கழிவுகளைக் கொண்டு அருமையான இயற்கை உரம் தயாரிக்கும் எளிய தொழில். இயற்கை விவசாயிகளிடையே நல்ல தேவை உள்ளது.",
        "ta_steps": [
            "1. நிழலான இடத்தில் HDPE மண்புழு உர படுக்கைகளை அமைத்தல்.",
            "2. சாணம், பண்ணை கழிவுகளை அடுக்கி 60% ஈரப்பதத்துடன் வைத்திருத்தல்.",
            "3. வீரியமிக்க ஆப்பிரிக்க மண்புழுக்களை படுக்கையில் விடுதல்.",
            "4. 45-60 நாட்களில் தயாராகும் பொடி போன்ற உரத்தை சலித்து எடுத்தல்.",
            "5. 5 கிலோ, 25 கிலோ பைகளில் அடைத்து நாற்றுப்பண்ணைகள் மற்றும் விவசாயிகளுக்கு விற்றல்."
        ]
    },
    {
        "id": "cold_pressed_oil",
        "title": "Micro Cold-Pressed Oil Mill",
        "ta_title": "மரச்செக்கு சமையல் எண்ணெய் தயாரிப்பு",
        "category": "Agro-Processing",
        "ta_category": "பாரம்பரிய உணவு ஆலை",
        "min_budget": 75000,
        "max_budget": 250000,
        "typical_budget": 120000,
        "location_types": ["Panchayat", "Town", "Semi-Urban"],
        "skills_required": ["Machine Operation", "Oil Filtration", "Food Safety"],
        "materials": [
            {"item": "Automated Mara Chekku / Cold-press oil expeller", "ta_item": "தானியங்கி மரச்செக்கு எண்ணெய் பிழியும் இயந்திரம்", "cost": 85000},
            {"item": "Groundnut, sesame (gingelly), coconut raw seeds", "ta_item": "நிலக்கடலை, எள் மற்றும் கொப்பரை தேங்காய் இருப்பு", "cost": 20000},
            {"item": "Sedimentation stainless steel tanks & gravity cotton filter", "ta_item": "துருப்பிடிக்காத ஸ்டீல் தொட்டிகள் & பருத்தி வடிகட்டி", "cost": 6000},
            {"item": "1-litre food-grade pet bottles, tin containers & labels", "ta_item": "உணவுத் தர பாட்டில்கள், டின்கள் மற்றும் லேபிள்கள்", "cost": 5000},
            {"item": "FSSAI license & initial marketing hoardings", "ta_item": "FSSAI உணவு உரிமம் & விளம்பர பலகைகள்", "cost": 4000}
        ],
        "timeline": "3 weeks to setup",
        "ta_timeline": "3 வாரங்களில் ஆலை அமைக்கலாம்",
        "monthly_potential_net": 35000,
        "description": "Premium demand for unrefined, sulfur-free traditional groundnut, sesame, and coconut oils. Oil cakes sold to cattle owners provides additional profit.",
        "steps": [
            "1. Install single-phase cold press machine in a visible street location to build trust.",
            "2. Source clean moisture-free groundnuts and sesame seeds from farmers.",
            "3. Extract pure virgin oil without chemical refining or heat above 45°C.",
            "4. Natural sedimentation for 48 hours followed by pure cloth gravity filtration.",
            "5. Sell oil directly to consumers and sell oil cake (புண்ணாக்கு) to local dairy farmers."
        ],
        "ta_description": "சுத்தமான மரச்செக்கு கடலை எண்ணெய், நல்லெண்ணெய், தேங்காய் எண்ணெய்க்கு மக்களிடம் அதிக வரவேற்பு உள்ளது. புண்ணாக்கு விற்பனை கூடுதல் வருமானம் தரும்.",
        "ta_steps": [
            "1. மக்கள் எளிதில் பார்க்கக்கூடிய இடத்தில் மரச்செக்கு இயந்திரத்தை நிறுவுதல்.",
            "2. விவசாயிகளிடம் இருந்து தரமான நிலக்கடலை, எள் விதைகளை நேரிடையாக வாங்குதல்.",
            "3. சூடுபடுத்தாமல் பாரம்பரிய முறையில் எண்ணெய் பிழிந்தெடுத்தல்.",
            "4. 48 மணி நேரம் இயற்கையாக படிய வைத்து தூய பருத்தி துணியில் வடிகட்டுதல்.",
            "5. சுத்தமான பாட்டில்களில் அடைத்து விற்பனை செய்தல்; புண்ணாக்கை மாட்டுத் தீவனமாக விற்றல்."
        ]
    },
    {
        "id": "rural_service_kiosk",
        "title": "Digital e-Sevai & Rural Banking Kiosk",
        "ta_title": "இ-சேவை & டிஜிட்டல் வங்கி மையம்",
        "category": "Tech & Services",
        "ta_category": "டிஜிட்டல் & வங்கி சேவை",
        "min_budget": 25000,
        "max_budget": 65000,
        "typical_budget": 38000,
        "location_types": ["Village", "Panchayat", "Town"],
        "skills_required": ["Computer Basics", "Internet Browsing", "Customer Service"],
        "materials": [
            {"item": "Refurbished Desktop/Laptop & High-speed 4G Wi-Fi Router", "ta_item": "கம்ப்யூட்டர் / லேப்டாப் & அதிவேக 4G வைஃபை ரூட்டர்", "cost": 18000},
            {"item": "All-in-one Color Tank Printer, Scanner & Copier", "ta_item": "ஆல்-இன்-ஒன் கலர் ஜெராக்ஸ் & ஸ்கேனர் பிரிண்டர்", "cost": 12000},
            {"item": "Biometric fingerprint scanner (Mantra/Morpho) for AePS", "ta_item": "AePS வங்கி பணம் எடுக்கும் பயோமெட்ரிக் கருவி", "cost": 2500},
            {"item": "Lamination machine & PVC Aadhaar card cutter", "ta_item": "லேமினேஷன் மெஷின் & பிவிசி கார்டு கட்டர்", "cost": 2500},
            {"item": "Paper reams, photo gloss sheets, lamination pouches", "ta_item": "ஜெராக்ஸ் தாள்கள், போட்டோ பேப்பர் & பவுச்கள்", "cost": 3000}
        ],
        "timeline": "1 week to start",
        "ta_timeline": "1 வாரத்தில் தொடங்கலாம்",
        "monthly_potential_net": 22000,
        "description": "Essential one-stop digital hub for Aadhaar AePS cash withdrawals, certificates (income, community, nativity), utility bill payments, and student online applications.",
        "steps": [
            "1. Register as a CSC Village Level Entrepreneur (VLE) or Spice Money/PayNearby agent.",
            "2. Set up biometric AePS cash deposit and withdrawal terminal for rural villagers.",
            "3. Provide online government services (TNeGA e-District certificates, Patta/Chitta).",
            "4. Offer photocopy, passport photos, exam hall ticket printing, and laminations.",
            "5. Assist farmers with PM-KISAN KYC updates and crop insurance claims."
        ],
        "ta_description": "கிராமங்களில் ஆதார் பணம் எடுத்தல், பட்டா சிட்டா, சாதி/வருமான சான்றிதழ், மின் கட்டணம் செலுத்த அத்தியாவசியமான இ-சேவை மையம்.",
        "ta_steps": [
            "1. CSC அல்லது டிஜிட்டல் வங்கி சேவை ஏஜென்சி (AePS) உரிமம் பெறுதல்.",
            "2. பயோமெட்ரிக் கைரேகை கருவி மூலம் வங்கி பணம் எடுக்கும் வசதி அமைத்தல்.",
            "3. அரசு இ-சேவை சான்றிதழ்கள், பட்டா சிட்டா மற்றும் அரசு நலத்திட்ட பதிவுகள் செய்தல்.",
            "4. ஜெராக்ஸ், பாஸ்போர்ட் போட்டோ, லேமினேஷன் சேவைகளை வழங்குதல்.",
            "5. விவசாயிகளுக்கு பி.எம் கிசான் கே.ஒய்.சி மற்றும் பயிர் காப்பீடு பதிவுகளை செய்து கொடுத்தல்."
        ]
    },
    {
        "id": "mushroom_farming",
        "title": "Oyster Mushroom Cultivation",
        "ta_title": "சிப்பி காளான் வளர்ப்பு",
        "category": "Agriculture & Horticulture",
        "ta_category": "வேளாண் தோட்டக்கலை",
        "min_budget": 8000,
        "max_budget": 30000,
        "typical_budget": 14000,
        "location_types": ["Village", "Panchayat", "Town"],
        "skills_required": ["Hygiene Maintenance", "Straw Sterilization", "Moisture Control"],
        "materials": [
            {"item": "Clean thatched shed / darkened room with gunny bags", "ta_item": "சுத்தமான கீற்று கொட்டகை & ஈர சாக்கு பைகள்", "cost": 3500},
            {"item": "Paddy straw (10 bundles) & boiling drum for sterilization", "ta_item": "10 கட்டு நெல் வைக்கோல் & அவிக்கும் உருளை", "cost": 2500},
            {"item": "Certified Oyster mushroom spawn (விதை) - 25 bottles", "ta_item": "25 பாட்டில் சான்றளிக்கப்பட்ட சிப்பி காளான் விதை", "cost": 1500},
            {"item": "PP cylinder bags, rubber bands & hand sprayer", "ta_item": "பாலித்தீன் சிலிண்டர் பைகள் & கை தெளிப்பான்", "cost": 1500},
            {"item": "Digital weighing scale & perforated packaging packets", "ta_item": "டிஜிட்டல் எடை தராசு & துளையிட்ட பேக்கிங் பைகள்", "cost": 2000},
            {"item": "Disinfectant solutions & lime powder", "ta_item": "கிருமிநாசினி திரவம் & சுண்ணாம்பு தூள்", "cost": 1000}
        ],
        "timeline": "21 days from spawning to harvest",
        "ta_timeline": "விதை இட்ட 21 நாட்களில் முதல் அறுவடை",
        "monthly_potential_net": 16000,
        "description": "Fast-growing high-protein crop requiring very minimal space. Ready harvest in 20-25 days using agricultural paddy straw waste.",
        "steps": [
            "1. Chop fresh clean paddy straw into 2-inch bits and boil in hot water for 45 mins to sterilize.",
            "2. Shade-dry straw to 65% moisture and prepare layered spawn cylinders in plastic bags.",
            "3. Hang bags in a ventilated, darkened room (25-30°C) with moist hanging gunny sacks.",
            "4. After 15 days of mycelium run, cut slits; oyster mushrooms sprout within 4 days.",
            "5. Harvest in clusters, weigh into 200g packets, and deliver fresh to local vegetable stalls."
        ],
        "ta_description": "குறைந்த இடத்திலும், வைக்கோல் கழிவுகளைக் கொண்டும் 20-25 நாட்களில் பலன் தரும் சத்தான சிப்பி காளான் வளர்ப்பு தொழில்.",
        "ta_steps": [
            "1. சுத்தமான நெல் வைக்கோலை 2 அங்குல துண்டுகளாக நறுக்கி கொதிக்கும் நீரில் தொற்று நீக்குதல்.",
            "2. வைக்கோலை நிழலில் உலர்த்தி, காளான் விதைகளுடன் பாலித்தீன் பைகளில் அடுக்கடுக்காக நிரப்புதல்.",
            "3. இருட்டான, ஈரப்பதமுள்ள கொட்டகையில் பைகளை தொங்கவிட்டு பராமரித்தல்.",
            "4. 15-18 நாட்களில் வெள்ளை நிறத்தில் பூஞ்சை பரவியதும் பைகளில் சிறு துளைகள் இடுதல்.",
            "5. காளான்களை பறித்து 200 கிராம் கவர்களில் பேக் செய்து உள்ளூர் காய்கறி கடைகளுக்கு வழங்குதல்."
        ]
    }
]

# ==========================================
# 2. BUSINESS IDEA GENERATOR ENGINE
# ==========================================
def generate_business_ideas(budget: float, skills: List[str], location: str, language: str = "en", custom_prompt: str = "") -> List[Dict[str, Any]]:
    """Match ideas based on budget, skills, location, and return enriched structure."""
    matched = []
    
    for biz in RURAL_BUSINESS_CATALOG:
        # Check budget feasibility with 25% flexibility
        min_allowed = biz["min_budget"] * 0.75
        is_budget_match = budget >= min_allowed
        
        # Check location
        is_location_match = location in biz["location_types"] or not location
        
        # Skill overlap
        skill_score = 0
        if skills:
            for s in skills:
                if any(s.lower() in req.lower() for req in biz["skills_required"]):
                    skill_score += 1
                if any(s.lower() in biz["category"].lower() for req in [1]):
                    skill_score += 1
        else:
            skill_score = 1  # default if no skills specified

        score = (1 if is_budget_match else 0) * 3 + (1 if is_location_match else 0) * 2 + skill_score
        
        if is_budget_match or budget == 0:
            item = dict(biz)
            item["match_score"] = score
            # Adjust financial estimates proportional to user budget
            scale = max(0.8, min(2.5, budget / biz["typical_budget"])) if budget > 0 else 1.0
            item["estimated_investment"] = round(biz["typical_budget"] * scale)
            item["estimated_monthly_profit"] = round(biz["monthly_potential_net"] * (scale ** 0.8))
            item["materials"] = [
                {
                    "item": m["item"],
                    "ta_item": m.get("ta_item", m["item"]),
                    "cost": round(m["cost"] * scale)
                } for m in biz.get("materials", [])
            ]
            matched.append(item)

    # Sort by match score
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    if not matched:
        # Fallback to catalog if budget was very low
        matched = []
        for b in RURAL_BUSINESS_CATALOG[:3]:
            item = dict(b)
            item["estimated_investment"] = item["typical_budget"]
            item["estimated_monthly_profit"] = item["monthly_potential_net"]
            item["materials"] = [
                {
                    "item": m["item"],
                    "ta_item": m.get("ta_item", m["item"]),
                    "cost": m["cost"]
                } for m in b.get("materials", [])
            ]
            matched.append(item)

    return matched[:5]

# ==========================================
# 3. FINANCIAL PLANNING & BREAK-EVEN ENGINE
# ==========================================
def calculate_financial_plan(daily_sales_units: float, selling_price_per_unit: float,
                             cost_per_unit: float, daily_operating_cost: float,
                             fixed_startup_cost: float, working_capital_days: int = 30) -> Dict[str, Any]:
    """
    Calculate daily/monthly financial metrics and break-even point.
    """
    daily_gross_revenue = daily_sales_units * selling_price_per_unit
    daily_cogs = daily_sales_units * cost_per_unit
    daily_total_expense = daily_cogs + daily_operating_cost
    daily_net_profit = daily_gross_revenue - daily_total_expense
    
    # 26 working days standard for rural micro business
    working_days = 26
    monthly_revenue = daily_gross_revenue * working_days
    monthly_cogs = daily_cogs * working_days
    monthly_operating_cost = daily_operating_cost * working_days
    monthly_total_expenses = monthly_cogs + monthly_operating_cost
    monthly_net_profit = monthly_revenue - monthly_total_expenses
    
    profit_margin_pct = (monthly_net_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
    
    # Break-even calculation
    contribution_margin_per_unit = selling_price_per_unit - cost_per_unit
    contribution_margin_ratio = (contribution_margin_per_unit / selling_price_per_unit) if selling_price_per_unit > 0 else 0
    
    monthly_fixed_costs = monthly_operating_cost
    if contribution_margin_per_unit > 0:
        break_even_units_monthly = monthly_fixed_costs / contribution_margin_per_unit
        break_even_revenue_monthly = break_even_units_monthly * selling_price_per_unit
        break_even_days_per_month = break_even_units_monthly / daily_sales_units if daily_sales_units > 0 else 0
    else:
        break_even_units_monthly = 0
        break_even_revenue_monthly = 0
        break_even_days_per_month = 0

    # Working capital calculation
    daily_working_capital_need = daily_cogs + daily_operating_cost
    total_working_capital = daily_working_capital_need * working_capital_days
    total_startup_fund_needed = fixed_startup_cost + total_working_capital

    # Payback period (months to recover initial capital)
    payback_months = (total_startup_fund_needed / monthly_net_profit) if monthly_net_profit > 0 else 0

    return {
        "daily": {
            "revenue": round(daily_gross_revenue, 2),
            "cogs": round(daily_cogs, 2),
            "operating_expense": round(daily_operating_cost, 2),
            "total_expense": round(daily_total_expense, 2),
            "net_profit": round(daily_net_profit, 2)
        },
        "monthly": {
            "working_days": working_days,
            "revenue": round(monthly_revenue, 2),
            "cogs": round(monthly_cogs, 2),
            "operating_cost": round(monthly_operating_cost, 2),
            "total_expenses": round(monthly_total_expenses, 2),
            "net_profit": round(monthly_net_profit, 2),
            "profit_margin_pct": round(profit_margin_pct, 1)
        },
        "break_even": {
            "contribution_margin_per_unit": round(contribution_margin_per_unit, 2),
            "contribution_margin_ratio_pct": round(contribution_margin_ratio * 100, 1),
            "units_needed_monthly": round(break_even_units_monthly, 1),
            "revenue_needed_monthly": round(break_even_revenue_monthly, 2),
            "days_to_break_even_each_month": round(break_even_days_per_month, 1)
        },
        "capital_structure": {
            "fixed_equipment_cost": round(fixed_startup_cost, 2),
            "working_capital_days": working_capital_days,
            "working_capital_required": round(total_working_capital, 2),
            "total_startup_capital_required": round(total_startup_fund_needed, 2),
            "payback_period_months": round(payback_months, 1)
        }
    }

# ==========================================
# 4. SMART PRICING ASSISTANT ENGINE
# ==========================================
def calculate_smart_pricing(
    raw_material_cost: float,
    direct_labor_cost: float,
    packaging_cost: float,
    utilities_and_fuel: float,
    other_overhead: float,
    target_margin_pct: float = 25.0,
    competitor_market_price: Optional[float] = None
) -> Dict[str, Any]:
    """Calculate production unit cost, markup, suggested price, and margin comparisons."""
    total_production_cost = (
        raw_material_cost + direct_labor_cost + packaging_cost + utilities_and_fuel + other_overhead
    )
    
    # Margin vs Markup
    # Selling Price = Cost / (1 - Margin%)
    safe_margin = min(target_margin_pct, 95.0) / 100.0
    suggested_selling_price = total_production_cost / (1.0 - safe_margin) if safe_margin < 1.0 else total_production_cost * 1.5
    
    profit_per_unit = suggested_selling_price - total_production_cost
    markup_pct = (profit_per_unit / total_production_cost * 100) if total_production_cost > 0 else 0
    actual_margin_pct = (profit_per_unit / suggested_selling_price * 100) if suggested_selling_price > 0 else 0

    # Pricing strategy tiers
    budget_price = total_production_cost * 1.15   # 15% markup (Fast market penetration)
    standard_price = suggested_selling_price      # Target margin
    premium_price = total_production_cost * 1.45  # 45% markup (Value added / festive season)

    analysis = {
        "cost_breakdown": {
            "raw_material": round(raw_material_cost, 2),
            "direct_labor": round(direct_labor_cost, 2),
            "packaging": round(packaging_cost, 2),
            "utilities_and_fuel": round(utilities_and_fuel, 2),
            "other_overhead": round(other_overhead, 2),
            "total_unit_cost": round(total_production_cost, 2)
        },
        "pricing_summary": {
            "suggested_price": round(suggested_selling_price, 2),
            "profit_per_unit": round(profit_per_unit, 2),
            "profit_margin_pct": round(actual_margin_pct, 1),
            "markup_pct": round(markup_pct, 1)
        },
        "price_tiers": {
            "penetration_price": round(budget_price, 2),
            "recommended_price": round(standard_price, 2),
            "premium_price": round(premium_price, 2)
        }
    }

    if competitor_market_price and competitor_market_price > 0:
        price_diff = suggested_selling_price - competitor_market_price
        diff_pct = (price_diff / competitor_market_price) * 100
        analysis["competitor_comparison"] = {
            "competitor_price": competitor_market_price,
            "difference_amount": round(price_diff, 2),
            "difference_pct": round(diff_pct, 1),
            "competitiveness": "Cheaper than market" if price_diff < -1 else ("Equal to market" if abs(price_diff) <= 1 else "More expensive than market"),
            "advice": "You have room to increase margin" if price_diff < -5 else ("Price is competitive and attractive to villagers" if abs(price_diff) <= 5 else "Highlight superior quality, freshness, or home-made purity to justify higher price.")
        }

    return analysis

# ==========================================
# 5. HYPER-LOCAL MARKET ANALYSIS & SURVEY
# ==========================================
def analyze_local_market(business_type: str, village_town: str, district: str, language: str = "en") -> Dict[str, Any]:
    """Generate hyper-local customer personas, seasonal demand curves, competitor analysis, and field survey."""
    is_tamil = (language == "ta")
    
    # Seasonal calendar for rural Tamil Nadu & South India
    seasonal_demand = [
        {
            "season": "Thai / Pongal & Harvest (Jan - Feb)" if not is_tamil else "தை / பொங்கல் மற்றும் அறுவடை காலம் (ஜனவரி - பிப்ரவரி)",
            "impact": "Peak Cashflow Period" if not is_tamil else "அதிக பணப்புழக்கம் உள்ள காலம்",
            "demand_level": "Very High (140%)",
            "recommendation": "Farmers have fresh harvest cash. Stock higher inventory, offer festival family gift packs." if not is_tamil else "விவசாயிகளிடம் அறுவடை வருமானம் இருக்கும். தின்பண்டங்கள், புத்தாடை, புதிய கருவிகள் அதிக விற்பனையாகும்."
        },
        {
            "season": "Panguni & Chithirai Temple Festivals (Mar - May)" if not is_tamil else "பங்குனி & சித்திரை திருவிழாக்கள் (மார்ச் - மே)",
            "impact": "High Crowd Influx" if not is_tamil else "திருவிழா மற்றும் திருமண காலம்",
            "demand_level": "High (125%)",
            "recommendation": "Set up pop-up stalls near village temple grounds, provide cold drinks, snacks, festive items." if not is_tamil else "கோவில் திருவிழாக்கள் மற்றும் கிராமத்து சந்தைகளில் தற்காலிக கடை அமைத்து வியாபாரம் செய்யலாம்."
        },
        {
            "season": "Aadi & School Reopening (Jun - Aug)" if not is_tamil else "ஆடி & பள்ளி திறப்பு காலம் (ஜூன் - ஆகஸ்ட்)",
            "impact": "Shifting Priorities" if not is_tamil else "கல்வி செலவு மற்றும் ஆடித்தள்ளுபடி",
            "demand_level": "Moderate (90%)",
            "recommendation": "School fees dominate family budgets. Offer micro-packs, budget alternatives, and discounts." if not is_tamil else "பள்ளிக் கட்டணச் செலவுகள் அதிகம் இருக்கும். குறைந்த விலையிலான சிறு பாக்கெட்டுகள் விற்பனைக்கு ஏற்றது."
        },
        {
            "season": "Deepavali & Karthigai (Oct - Nov)" if not is_tamil else "தீபாவளி & கார்த்திகை தீபம் (அக்டோபர் - நவம்பர்)",
            "impact": "Peak Spending & Gifting" if not is_tamil else "ஆண்டு உச்சபட்ச விற்பனை காலம்",
            "demand_level": "Maximum (150%)",
            "recommendation": "Accept advance bookings. Combine value combos and offer loyalty perks." if not is_tamil else "முன்பதிவு பெற்றுக் கொண்டு பலகாரங்கள், ஆடை தையல், தீப எண்ணெய் வகைகளை கூடுதல் விலையின்றி விற்கலாம்."
        }
    ]

    # Customer Segments
    customer_segments = [
        {
            "segment": "Local Farming Families" if not is_tamil else "விவசாய குடும்பங்கள்",
            "share": "45%",
            "buying_behavior": "Cash purchases post-harvest, values durability and honest measure." if not is_tamil else "அறுவடைக்கு பின் மொத்தமாக வாங்குவர். நம்பகத்தன்மை மற்றும் தரத்தை எதிர்பார்ப்பர்."
        },
        {
            "segment": "Daily Wage & MGNREGA Workers" if not is_tamil else "தினக்கூலி & 100 நாள் திட்ட தொழிலாளர்கள்",
            "share": "25%",
            "buying_behavior": "Daily or weekly small ticket purchases; highly price-sensitive; prefers ₹10-₹50 packs." if not is_tamil else "தினசரி சிறு தொகைக்கு வாங்குவர்; ₹10 முதல் ₹50 மதிப்பிலான சிறு பாக்கெட்டுகளை விரும்புவர்."
        },
        {
            "segment": "Salaried Employees (Teachers, Bank, Panchayat staff)" if not is_tamil else "மாத சம்பளக்காரர்கள் (ஆசிரியர்கள், வங்கி, அரசு ஊழியர்கள்)",
            "share": "15%",
            "buying_behavior": "Steady monthly income, willing to pay premium for organic, pure, and doorstep delivered items." if not is_tamil else "மாத தொடக்கத்தில் மொத்தமாக வாங்குவர்; கலப்படமற்ற இயற்கை உணவுகளுக்கு கூடுதல் விலை தருவர்."
        },
        {
            "segment": "Youth & School/College Students" if not is_tamil else "இளைஞர்கள் & கல்லூரி மாணவர்கள்",
            "share": "15%",
            "buying_behavior": "Enthusiastic about fast snacks, digital recharges, Xerox, tailoring trends." if not is_tamil else "டிஜிட்டல் சேவைகள், துரித உணவு, நவீன ஆடை வடிவமைப்பு ஆகியவற்றில் ஆர்வம் கொண்டவர்கள்."
        }
    ]

    # Field Survey Questions (10 essential localized questions)
    survey_questions = [
        {
            "q_no": 1,
            "en": f"Where do you currently purchase your {business_type or 'daily essentials'}?",
            "ta": f"நீங்கள் தற்போது உங்கள் {business_type or 'அத்தியாவசியப் பொருட்கள்'}-களை எங்கு வாங்குகிறீர்கள்?",
            "options": ["Village local petty shop", "Weekly shandy / Santhai", "Nearby town / Taluk centre", "Online / Travelling vans"]
        },
        {
            "q_no": 2,
            "en": "How often do you or your family buy this item?",
            "ta": "இப்பொருளை நீங்கள் எவ்வளவு கால இடைவெளியில் வாங்குகிறீர்கள்?",
            "options": ["Daily", "Twice a week", "Weekly on shandy day", "Once a month in bulk"]
        },
        {
            "q_no": 3,
            "en": "What is the average amount you spend per purchase?",
            "ta": "ஒரு முறை வாங்கும்போது தோராயமாக எவ்வளவு செலவு செய்கிறீர்கள்?",
            "options": ["Less than ₹50", "₹50 - ₹150", "₹150 - ₹500", "Above ₹500"]
        },
        {
            "q_no": 4,
            "en": "What is your main problem with the current shops nearby?",
            "ta": "தற்போதுள்ள கடைகளில் நீங்கள் சந்திக்கும் முக்கிய குறைபாடு என்ன?",
            "options": ["High price", "Poor quality / Adulteration", "Lack of variety / Stockouts", "Too far to travel"]
        },
        {
            "q_no": 5,
            "en": "If a new trusted shop opens right in your village, will you support it?",
            "ta": "உங்கள் கிராமத்திலேயே புதிய தரமான கடை துவங்கினால் ஆதரவு தருவீர்களா?",
            "options": ["Definitely yes", "Yes, if price is competitive", "Only if quality is better", "Depends on credit facility"]
        },
        {
            "q_no": 6,
            "en": "Which payment method do you most frequently use?",
            "ta": "பொருட்கள் வாங்கும் போது நீங்கள் அதிகம் பயன்படுத்தும் முறை எது?",
            "options": ["Cash (ரொக்கம்)", "GPay / PhonePe (UPI)", "Monthly credit book (கடன் முறை)", "Both Cash & UPI"]
        },
        {
            "q_no": 7,
            "en": "What packaging size would be most convenient for your household?",
            "ta": "எந்த அளவு பேக்கிங் உங்கள் குடும்பத்திற்கு மிகவும் வசதியாக இருக்கும்?",
            "options": ["Small trial pack (100g / ₹10-20)", "Medium pack (250g - 500g)", "1 kg standard pack", "5 kg / 10 kg bulk pack"]
        },
        {
            "q_no": 8,
            "en": "Would home delivery or WhatsApp order facility be useful for you?",
            "ta": "வாட்ஸ்அப் மூலம் ஆர்டர் செய்து வீடு தேடி கொடுக்கும் சேவை பயனுள்ளதாக இருக்குமா?",
            "options": ["Very useful", "Nice to have occasionally", "Not necessary, I prefer visiting shop"]
        },
        {
            "q_no": 9,
            "en": "What is the most important factor when you decide to buy?",
            "ta": "ஒரு பொருளை வாங்க முடிவெடுக்கும் போது உங்களுக்கு மிக முக்கியமானது எது?",
            "options": ["Freshness & Pure taste", "Lowest price", "Friendliness of shopkeeper", "Trusted brand name"]
        },
        {
            "q_no": 10,
            "en": "Any specific suggestion or item you feel is missing in this locality?",
            "ta": "இப்பகுதியில் கிடைக்காத அல்லது நீங்கள் எதிர்பார்க்கும் பொருட்கள் ஏதேனும் உள்ளதா?",
            "options": ["Text feedback / Open question"]
        }
    ]

    return {
        "location": f"{village_town or 'Local Village'}, {district or 'District'}",
        "business_type": business_type or "Rural Micro-Enterprise",
        "customer_segments": customer_segments,
        "seasonal_demand": seasonal_demand,
        "competitor_insights": {
            "primary_threats": "Wholesale products from nearby town arriving on weekly market day (சந்தை); cheap chemical adulterated alternatives." if not is_tamil else "நகரத்திலிருந்து வாரச் சந்தைக்கு வரும் மலிவு விலை பொருட்கள்; கலப்பட பொருட்கள்.",
            "competitive_edge": "100% freshness, personalized relationship, zero travel expense for villagers, custom small quantity sales." if not is_tamil else "நேரடி புத்துணர்ச்சி, கலப்படமின்மை, கிராமத்து மக்களுக்கு பயண நேரம் மற்றும் செலவு மிச்சம், வாடிக்கையாளர் மதிப்பு."
        },
        "survey_questions": survey_questions
    }

# ==========================================
# 6. BUSINESS PLAN GENERATOR ENGINE
# ==========================================
def generate_business_plan(
    title: str,
    category: str,
    location: str,
    startup_budget: float,
    monthly_sales_target: float,
    owner_name: str = "Micro-Entrepreneur",
    language: str = "en"
) -> Dict[str, Any]:
    """Generate comprehensive structured business plan with financial projections, marketing & risk mitigation."""
    is_tamil = (language == "ta")
    
    # Financial breakdown
    equipment_cost = round(startup_budget * 0.55)
    raw_material_stock = round(startup_budget * 0.25)
    licensing_and_branding = round(startup_budget * 0.08)
    contingency_cash = round(startup_budget * 0.12)
    
    monthly_cogs = round(monthly_sales_target * 0.60)
    monthly_operating_cost = round(monthly_sales_target * 0.15)
    monthly_net_profit = monthly_sales_target - monthly_cogs - monthly_operating_cost
    annual_projected_profit = monthly_net_profit * 12

    plan = {
        "metadata": {
            "title": title,
            "owner": owner_name,
            "category": category,
            "location": location,
            "startup_capital": startup_budget,
            "date": "2026-10-28"
        },
        "sections": [
            {
                "id": "exec_summary",
                "title": "1. Executive Summary" if not is_tamil else "1. நிர்வாக சுருக்கம்",
                "content": f"{title} is a rural micro-enterprise proposed to be established at {location} by {owner_name}. The project aims to address local rural consumer demand with a planned total investment of ₹{startup_budget:,.0f}, projecting an estimated monthly net profit of ₹{monthly_net_profit:,.0f} and creating sustainable self-employment." if not is_tamil else f"{title} என்பது {location} பகுதியில் {owner_name} அவர்களால் தொடங்க உத்தேசிக்கப்பட்டுள்ள கிராமப்புற குறுந்தொழில் ஆகும். இதன் மொத்த தொடக்க முதலீடு ₹{startup_budget:,.0f} ஆகவும், மாதாந்திர எதிர்பார்க்கப்படும் நிகர லாபம் ₹{monthly_net_profit:,.0f} ஆகவும் கணக்கிடப்பட்டுள்ளது."
            },
            {
                "id": "business_desc",
                "title": "2. Business Description & Objectives" if not is_tamil else "2. வணிக விளக்கம் & நோக்கங்கள்",
                "content": f"The enterprise operates in the {category} sector, providing high quality, unadulterated products/services directly to local villagers, farmers, and surrounding panchayats. The primary objective is to achieve operational break-even within 60 days of commencement and capture at least 25% share of the local village demand." if not is_tamil else f"இத்தொழில் {category} துறையில் செயல்பட்டு, உள்ளூர் மக்கள் மற்றும் விவசாயிகளுக்கு கலப்படமற்ற தரமான பொருட்களை நேரடியாக வழங்கும் நோக்கத்துடன் துவங்கப்படுகிறது. முதல் 60 நாட்களுக்குள் உற்பத்தி மற்றும் விற்பனையை சீராக்கி நிலைநிறுத்துவது முதன்மை இலக்காகும்."
            },
            {
                "id": "market_analysis",
                "title": "3. Market Opportunity & Target Customers" if not is_tamil else "3. சந்தை வாய்ப்பு & வாடிக்கையாளர்கள்",
                "content": f"In {location}, residents presently travel to taluk headquarters or wait for the weekly shandy for quality products. By establishing a local unit, customers save travel time and bus fare. Primary target segments include: (a) Local farming families, (b) Daily wage earners, (c) Local school & government staff." if not is_tamil else f"{location} பகுதியில் உள்ள மக்கள் தற்போது பொருட்களை வாங்க வாரச் சந்தை அல்லது அருகிலுள்ள நகரத்திற்கு செல்ல வேண்டியுள்ளது. உள்ளூரிலேயே தரமான பொருள் கிடைப்பதால் நேரம் மற்றும் பயணச் செலவு மிச்சமாகும்."
            },
            {
                "id": "startup_costs",
                "title": "4. Capital Expenditure & Working Capital Plan" if not is_tamil else "4. முதலீட்டுத் தேவை & நடைமுறை மூலதனம்",
                "content": f"• Machinery, Tools & Equipment: ₹{equipment_cost:,.0f}\n• Initial Raw Material Inventory: ₹{raw_material_stock:,.0f}\n• FSSAI/Udyam Registration, Signage & Packaging: ₹{licensing_and_branding:,.0f}\n• Cash Reserve / Working Capital Buffer: ₹{contingency_cash:,.0f}\n• Total Project Cost: ₹{startup_budget:,.0f}" if not is_tamil else f"• இயந்திரங்கள் & உபகரணங்கள்: ₹{equipment_cost:,.0f}\n• ஆரம்ப மூலப்பொருள் இருப்பு: ₹{raw_material_stock:,.0f}\n• பதிவு சான்றிதழ், பெயர் பலகை & பேக்கிங்: ₹{licensing_and_branding:,.0f}\n• அவசர கையிருப்பு நிதி: ₹{contingency_cash:,.0f}\n• மொத்த திட்ட முதலீடு: ₹{startup_budget:,.0f}"
            },
            {
                "id": "financial_projections",
                "title": "5. Financial Projections & Cash Flow" if not is_tamil else "5. நிதி மதிப்பீடு & பணப்புழக்க கணிப்பு",
                "content": f"• Projected Monthly Gross Revenue: ₹{monthly_sales_target:,.0f}\n• Cost of Goods Sold (Raw materials, packaging): ₹{monthly_cogs:,.0f}\n• Operating Overhead (Electricity, transport, maintenance): ₹{monthly_operating_cost:,.0f}\n• Projected Net Monthly Profit: ₹{monthly_net_profit:,.0f}\n• Annual Projected Net Surplus: ₹{annual_projected_profit:,.0f}\n• Estimated Capital Recovery / Payback Period: ~{round(startup_budget/monthly_net_profit, 1) if monthly_net_profit > 0 else 'N/A'} Months" if not is_tamil else f"• மாதாந்திர உத்தேச விற்பனை வருவாய்: ₹{monthly_sales_target:,.0f}\n• மூலப்பொருள் மற்றும் உற்பத்தி செலவு: ₹{monthly_cogs:,.0f}\n• மின்சாரம், போக்குவரத்து உள்ளிட்ட பிற செலவுகள்: ₹{monthly_operating_cost:,.0f}\n• மாதாந்திர நிகர லாபம்: ₹{monthly_net_profit:,.0f}\n• ஆண்டு உத்தேச நிகர வருமானம்: ₹{annual_projected_profit:,.0f}\n• முதலீடு திரும்பக் கிடைக்கும் காலம்: ~{round(startup_budget/monthly_net_profit, 1) if monthly_net_profit > 0 else 'N/A'} மாதங்கள்"
            },
            {
                "id": "marketing_strategy",
                "title": "6. Marketing & Sales Strategy" if not is_tamil else "6. விற்பனை & சந்தைப்படுத்தல் உத்திகள்",
                "content": "• Direct Village Word of Mouth: Distribute free taste/trial samples to influential village panchayat elders and self-help group (SHG) animators.\n• Weekly Shandy Stall: Set up a dedicated branded table at local weekly santhai.\n• WhatsApp Business Catalogue: Broadcast daily stock availability and accept orders via WhatsApp.\n• Competitive Bundling: Introduce small trial packs (₹10 - ₹25) to lower customer hesitation." if not is_tamil else "• வாய்மொழி விளம்பரம்: கிராமப் பெரியவர்கள் மற்றும் மகளிர் சுயஉதவிக்குழு தலைவிகளுக்கு மாதிரி கொடுத்து அறிமுகப்படுத்துதல்.\n• வாரச் சந்தை விற்பனை: அருகிலுள்ள வாரச் சந்தையில் தனிக் கடை அமைத்து விற்பனை செய்தல்.\n• வாட்ஸ்அப் குழுக்கள்: உள்ளூர் வாட்ஸ்அப் குழுக்களில் பொருட்கள் விபரங்களை பதிவிட்டு ஆர்டர் பெறுதல்.\n• சிறு பாக்கெட்டுகள்: மக்கள் தயக்கமின்றி வாங்க ₹10, ₹25 மதிப்புள்ள சிறு பாக்கெட்டுகளை அறிமுகப்படுத்துதல்."
            },
            {
                "id": "risk_management",
                "title": "7. Risk Analysis & Mitigation Plan" if not is_tamil else "7. இடர் மேலாண்மை & முன்னெச்சரிக்கை திட்டம்",
                "content": "• Risk: Raw material price volatility (crop harvest failure).\n  Mitigation: Maintain 45-day non-perishable buffer stock bought at harvest lows.\n• Risk: Customer credit requests resulting in working capital choke.\n  Mitigation: Strictly enforce cash/UPI sales; limit credit to vetted buyers with 7-day settlement.\n• Risk: Machine breakdown in rural area.\n  Mitigation: Learn basic maintenance, keep spare belts/screws, have local mechanic contact." if not is_tamil else "• இடர்: மூலப்பொருள் விலை உயர்வு.\n  தீர்வு: அறுவடை காலத்தில் விலை குறையும் போது 45 நாட்களுக்கான மூலப்பொருளை வாங்கி சேமித்தல்.\n• இடர்: வாடிக்கையாளர் கடன் கேட்பதால் பண முடக்கம் ஏற்படுதல்.\n  தீர்வு: ரொக்கம் மற்றும் UPI பரிவர்த்தனையை ஊக்குவித்தல்; அத்தியாவசிய கடன்களை 7 நாட்களுக்குள் வசூலித்தல்.\n• இடர்: இயந்திர பழுது.\n  தீர்வு: அடிப்படை பழுதுநீக்கும் முறைகளை கற்றுக்கொள்ளுதல் மற்றும் அவசர உதிரிபாகங்களை இருப்பு வைத்தல்."
            }
        ]
    }
    return plan

# ==========================================
# 7. MICROLOAN READINESS ASSISTANT ENGINE
# ==========================================
SCHEMES_GUIDE = [
    {
        "id": "mudra_shishu",
        "name": "PM MUDRA Yojana - Shishu (பிரதான் மந்திரி முத்ரா - சிசு)",
        "max_amount": 50000,
        "subsidy": "Zero collateral, subsidized low interest (7.5% - 9.5%)",
        "best_for": "First-time micro-entrepreneurs, tailoring, mushroom units, street stalls, small petty shops.",
        "ta_best_for": "முதல் முறை தொழில் தொடங்குவோர், தையல் கடை, காளான் வளர்ப்பு, சிறு பெட்டிக் கடை.",
        "processing_fee": "NIL",
        "tenure": "3 to 5 years"
    },
    {
        "id": "mudra_kishor",
        "name": "PM MUDRA Yojana - Kishor (முத்ரா - கிஷோர்)",
        "max_amount": 500000,
        "subsidy": "Collateral free, margin money 10-15%",
        "best_for": "Expanding units, cold-press oil expellers, poultry sheds, areca plate machinery.",
        "ta_best_for": "தொழில் விரிவாக்கம், மரச்செக்கு இயந்திரம், நாட்டுக்கோழி கொட்டகை, பாக்கு மட்டை இயந்திரம்.",
        "processing_fee": "0.50% or waived",
        "tenure": "3 to 5 years"
    },
    {
        "id": "pm_svanidhi",
        "name": "PM SVANidhi (பீ எம் சுவநிதி திட்டம்)",
        "max_amount": 10000,
        "subsidy": "7% interest subsidy on timely digital repayment; expands to ₹20k & ₹50k in cycles",
        "best_for": "Rural street vendors, vegetable sellers, mobile tiffin pushcarts, artisans.",
        "ta_best_for": "தெருவோர வியாபாரிகள், தள்ளுவண்டி காய்கறி/டிபன் வியாபாரம், கைவினைஞர்கள்.",
        "processing_fee": "NIL",
        "tenure": "1 year working capital loan"
    },
    {
        "id": "pmegp",
        "name": "PMEGP (பிரதமர் வேலைவாய்ப்பு உருவாக்கும் திட்டம்)",
        "max_amount": 5000000,
        "subsidy": "Up to 35% government capital subsidy for rural area applicants",
        "best_for": "Rural manufacturing units, food processing mills, agro-service centres.",
        "ta_best_for": "கிராமப்புற உற்பத்தி கூடங்கள், மாவு & எண்ணெய் ஆலைகள், விவசாய சேவை மையங்கள் (35% மானியம்).",
        "processing_fee": "Standard bank fee",
        "tenure": "5 to 7 years"
    },
    {
        "id": "shg_bank_linkage",
        "name": "SHG Bank Linkage / TNSRLM (மகளிர் சுயஉதவிக்குழு வங்கி கடன்)",
        "max_amount": 1000000,
        "subsidy": "Subsidized interest (7% with prompt repayment incentive), group guarantee",
        "best_for": "Women entrepreneur groups, catering units, value-added agro-products, handicrafts.",
        "ta_best_for": "பெண்கள் சுயஉதவிக்குழு உறுப்பினர்கள், குழுவாக தொழில் செய்வோர் (குறைந்த வட்டி).",
        "processing_fee": "Minimal",
        "tenure": "3 to 5 years"
    }
]

DOCUMENTS_CHECKLIST = [
    {"id": "doc_aadhaar", "title": "Aadhaar Card (ஆதார் அட்டை)", "mandatory": True, "category": "Identity & Address"},
    {"id": "doc_pan", "title": "PAN Card (பான் கார்டு)", "mandatory": True, "category": "Financial Identity"},
    {"id": "doc_bank_passbook", "title": "Bank Passbook / 6 Months Bank Statement (வங்கி கணக்கு புத்தகம்)", "mandatory": True, "category": "Financial Record"},
    {"id": "doc_photo", "title": "2 Passport Size Photographs (புகைப்படம்)", "mandatory": True, "category": "Identity"},
    {"id": "doc_udyam", "title": "Udyam Registration Certificate (உத்யம் பதிவு சான்றிதழ் - Free online)", "mandatory": False, "category": "Business Proof"},
    {"id": "doc_quotation", "title": "Machinery / Equipment Purchase Quotation (இயந்திர விலைப்புள்ளி / கொட்டேஷன்)", "mandatory": True, "category": "Project Cost"},
    {"id": "doc_business_plan", "title": "Project Report / Business Plan (திட்ட அறிக்கை)", "mandatory": True, "category": "Project Feasibility"},
    {"id": "doc_rent_deed", "title": "Shop/Unit Rental Agreement or Property Tax Receipt (வாடகை ஒப்பந்தம் / வரி ரசீது)", "mandatory": False, "category": "Business Location"}
]

def assess_microloan_readiness(
    requested_amount: float,
    monthly_net_profit: float,
    checked_documents: List[str],
    has_existing_loan: bool = False,
    existing_emi: float = 0.0
) -> Dict[str, Any]:
    """Calculate loan readiness score (0-100), eligible schemes, monthly EMI estimate, and DSCR."""
    # Find matching schemes
    suitable_schemes = []
    for s in SCHEMES_GUIDE:
        if requested_amount <= s["max_amount"]:
            suitable_schemes.append(s)
            
    if not suitable_schemes:
        suitable_schemes = [SCHEMES_GUIDE[3]] # PMEGP for large amounts

    # Estimate EMI (assume 9% interest for 36 months)
    rate_monthly = (9.0 / 12) / 100
    months = 36
    emi = (requested_amount * rate_monthly * ((1 + rate_monthly) ** months)) / (((1 + rate_monthly) ** months) - 1) if requested_amount > 0 else 0
    
    # Debt Service Coverage Ratio (DSCR)
    total_monthly_emi = emi + existing_emi
    dscr = (monthly_net_profit / total_monthly_emi) if total_monthly_emi > 0 else 0

    # Calculate Readiness Score (out of 100)
    score = 0
    # 1. Document readiness (40 pts)
    mandatory_docs = [d["id"] for d in DOCUMENTS_CHECKLIST if d["mandatory"]]
    mandatory_checked = sum(1 for d in mandatory_docs if d in checked_documents)
    score += int((mandatory_checked / len(mandatory_docs)) * 40)
    
    # 2. Financial viability / DSCR (40 pts)
    if dscr >= 2.0:
        score += 40
    elif dscr >= 1.5:
        score += 32
    elif dscr >= 1.2:
        score += 24
    elif dscr >= 1.0:
        score += 15
    else:
        score += 5

    # 3. Promoter contribution / existing debt health (20 pts)
    if not has_existing_loan:
        score += 20
    elif existing_emi < (monthly_net_profit * 0.25):
        score += 12
    else:
        score += 5

    # Banker approval readiness grade
    if score >= 80:
        grade = "Excellent (அதிக வாய்ப்பு - High Approval Likelihood)"
        status_color = "emerald"
        banker_verdict = "Your project is highly bankable! You meet all mandatory document requirements and have a strong surplus to service monthly EMIs with ease."
    elif score >= 60:
        grade = "Good (நடுத்தர வாய்ப்பு - Good Likelihood)"
        status_color = "blue"
        banker_verdict = "Your application is promising. Ensure you carry original machinery quotations and your Udyam registration to speed up loan sanction."
    else:
        grade = "Needs Preparation (தயாரிப்பு தேவை - Needs Improvement)"
        status_color = "amber"
        banker_verdict = "Complete your missing mandatory documents (especially machinery quotations and bank statement) and show realistic sales figures to satisfy the bank manager."

    return {
        "score": min(score, 100),
        "grade": grade,
        "status_color": status_color,
        "banker_verdict": banker_verdict,
        "requested_amount": requested_amount,
        "estimated_monthly_emi": round(emi, 2),
        "total_monthly_commitment": round(total_monthly_emi, 2),
        "monthly_net_surplus": round(monthly_net_profit, 2),
        "dscr_ratio": round(dscr, 2),
        "dscr_health": "Very Healthy (>2.0)" if dscr >= 2.0 else ("Acceptable (1.2 - 2.0)" if dscr >= 1.2 else "Risky (<1.2)"),
        "suitable_schemes": suitable_schemes,
        "all_documents": DOCUMENTS_CHECKLIST,
        "checked_docs_count": len(checked_documents),
        "total_docs_count": len(DOCUMENTS_CHECKLIST)
    }

# ==========================================
# 8. AI BUSINESS ADVISORY CHATBOT ENGINE
# ==========================================
CHAT_KNOWLEDGE_BASE = [
    {
        "keywords": ["mudra", "loan", "கடன்கு", "கடன்", "bank loan", "finance", "பணம்"],
        "en": "For rural micro-businesses, **PM MUDRA Yojana** is the most accessible collateral-free loan:\n1. **Shishu**: Up to ₹50,000 (ideal for petty shops, tailoring, poultry).\n2. **Kishor**: ₹50,000 to ₹5,00,000 (for oil expellers, machinery, vehicles).\n3. **Tarun**: ₹5,00,000 to ₹10,00,000.\n\n**Key Requirements**: Aadhaar, PAN, 6 months bank statement, and a machine quotation. No security or mortgage is needed. You can apply at any nationalized bank, rural regional bank (e.g. Tamil Nadu Grama Bank), or online via udyamimitra.in.",
        "ta": "கிராமப்புற குறுந்தொழில்களுக்கு **பிரதான் மந்திரி முத்ரா கடன் திட்டம்** சிறந்த வழியாகும்:\n1. **சிசு திட்டம்**: ₹50,000 வரை (தையல் கடை, மளிகை, சிறு தொழில்களுக்கு ஏற்றது).\n2. **கிஷோர் திட்டம்**: ₹50,000 முதல் ₹5,00,000 வரை (இயந்திரங்கள், எண்ணெய் ஆலை, வாகனங்களுக்கு).\n3. **தருண் திட்டம்**: ₹5,00,000 முதல் ₹10,00,000 வரை.\n\n**தேவையான ஆவணங்கள்**: ஆதார், பான், 6 மாத வங்கி கணக்கு புத்தகம் மற்றும் இயந்திர விலைப்புள்ளி (Quotation). சொத்து அடமானம் எதுவும் தேவையில்லை. தமிழ்நாடு கிராம வங்கி அல்லது பொதுத்துறை வங்கிகளில் விண்ணப்பிக்கலாம்."
    },
    {
        "keywords": ["working capital", "நடைமுறை மூலதனம்", "cash flow", "பணப்புழக்கம்"],
        "en": "**Working Capital** is the daily operating fuel for your business. It is the money needed to:\n1. Buy daily raw materials (e.g. seeds, cloth, grains).\n2. Pay daily electricity, transport, or helper wages.\n3. Keep cash in hand while waiting for customers to pay.\n\n**Golden Rule for Rural Entrepreneurs**: Always keep at least 30 to 45 days of operating expenses saved in reserve so your shop never stops running during seasonal dips.",
        "ta": "**நடைமுறை மூலதனம் (Working Capital)** என்பது உங்கள் தொழில் அன்றாடம் தடங்கலின்றி இயங்கத் தேவையான 'எரிபொருள்' போன்றது:\n1. அன்றாட மூலப்பொருட்கள் வாங்க (விதை, துணி, தானியம்).\n2. மின் கட்டணம், கூலி மற்றும் போக்குவரத்து செலவுகள் செய்ய.\n3. வாடிக்கையாளர் பணம் தர தாமதமானாலும் தொழிலை நடத்த.\n\n**முக்கிய விதி**: குறைந்தபட்சம் 30 முதல் 45 நாட்களுக்கான செலவு தொகையை எப்போதுமே அவசர கையிருப்பாக வைத்திருக்க வேண்டும்."
    },
    {
        "keywords": ["pricing", "price", "விலை", "விலை நிர்ணயம்", "profit margin", "லாபம்"],
        "en": "To price your rural product correctly without making a loss:\n1. **Calculate Total Unit Cost**: Raw materials + Labor + Packaging + Electricity/Fuel + Waste allowance (5%).\n2. **Add Your Desired Margin**: For rural markets, 20% to 30% profit margin is ideal.\n3. **Formula**: `Selling Price = Cost / (1 - Margin%)`. For example, if cost is ₹75 and you want 25% margin, selling price = `75 / 0.75 = ₹100` (Profit = ₹25).\n4. **Check Local Competition**: Don't price too far above or below your local weekly market standard.",
        "ta": "நஷ்டம் ஏற்படாமல் சரியான விற்பனை விலையை நிர்ணயிக்க:\n1. **உற்பத்தி செலவைக் கணக்கிடுங்கள்**: மூலப்பொருள் + கூலி + பேக்கிங் + மின்சாரம்/வண்டிச் செலவு + சேதாரம் (5%).\n2. **லாப சதவீதத்தை கூட்டுங்கள்**: கிராமப்புற சூழலுக்கு 20% முதல் 30% லாப வரம்பு சிறந்தது.\n3. **சூத்திரம்**: `விற்பனை விலை = அடக்கவிலை / (1 - லாப%)`. உதாரணத்திற்கு, அடக்கவிலை ₹75 மற்றும் லாபம் 25% எனில், விற்பனை விலை = ₹100 (லாபம் ₹25).\n4. **உள்ளூர் விலையை கவனியுங்கள்**: வாரச் சந்தை விலையை விட மிக அதிகமாகவோ குறைவாகவோ வைக்காதீர்கள்."
    },
    {
        "keywords": ["marketing", "sales", "விற்பனை", "வாடிக்கையாளர்", "விளம்பரம்", "promote"],
        "en": "Low-cost marketing tactics that work wonders in rural areas:\n1. **Village Word of Mouth**: Give free sample tastes to SHG leaders and local teachers.\n2. **WhatsApp Business**: Create a broadcast group of village customers; post photos of freshly prepared items every morning.\n3. **Weekly Shandy (சந்தை) Stall**: Put up a clean banner at the local market to attract visitors from 10 surrounding hamlets.\n4. **Small Trial Packs**: Offer ₹10 - ₹20 mini packs so first-time buyers can try your product without fear.\n5. **Special Festival Combos**: Offer Pongal/Diwali discount packages for families.",
        "ta": "கிராமப்புறங்களில் குறைந்த செலவில் விற்பனையை பெருக்கும் வழிகள்:\n1. **நேரடி அறிமுகம்**: மகளிர் சுயஉதவிக்குழு தலைவிகள் மற்றும் ஆசிரியர்களுக்கு சிறு மாதிரி கொடுத்து நற்பெயர் பெறுங்கள்.\n2. **வாட்ஸ்அப் குழு**: கிராமத்து வாடிக்கையாளர் எண்களைச் சேர்த்து தினசரி புத்தம் புதிய பொருட்களின் புகைப்படங்களை பகிருங்கள்.\n3. **வாரச் சந்தை**: சுற்றியுள்ள 10 கிராம மக்கள் கூடும் வாரச் சந்தையில் பெயர் பலகையுடன் கடை போடுங்கள்.\n4. **சிறு பாக்கெட்டுகள்**: மக்கள் தைரியமாக வாங்கிப் பார்க்க ₹10, ₹20 அளவிலான சிறு பாக்கெட்டுகளை வையுங்கள்.\n5. **பண்டிகை கால சலுகைகள்**: பொங்கல், தீபாவளி நாட்களில் குடும்பத்திற்கான சிறப்பு காம்போ பேக் வழங்குங்கள்."
    },
    {
        "keywords": ["poultry", "chicken", "கோழி", "நாட்டுக்கோழி", "broiler"],
        "en": "**Free-Range Country Chicken (நாட்டுக்கோழி) Guide**:\n• **Budget**: ₹20,000 - ₹35,000 for 50 birds.\n• **Cycle**: 90-110 days to reach 1.5 kg - 1.8 kg live weight.\n• **Feed Cost Reduction**: Cultivate Azolla pits and provide broken corn, wheat bran, and household greens to cut feed bills by 35%.\n• **Critical Vaccination**: Day 7 (F1/Lasota eyedrop), Day 28 (Lasota booster), Day 45 (Fowl Pox).\n• **Market Selling**: Live birds fetch ₹350 - ₹450 per kg in rural & semi-urban markets.",
        "ta": "**நாட்டுக்கோழி வளர்ப்பு வழிகாட்டி**:\n• **முதலீடு**: 50 குஞ்சுகளுக்கு சுமார் ₹20,000 - ₹35,000.\n• **வளர்ச்சி காலம்**: 90-110 நாட்களில் 1.5 முதல் 1.8 கிலோ எடை வரும்.\n• **தீவனச் செலவு குறைக்க**: அசோலா தொட்டி அமைத்து, மக்காச்சோளக் குருணை மற்றும் தவிடு கலந்து கொடுத்தால் தீவனச் செலவு 35% குறையும்.\n• **தடுப்பூசி அட்டவணை**: 7-வது நாள் (லசோட்டா சொட்டு மருந்து), 28-வது நாள் (பூஸ்டர்), 45-வது நாள் (அம்மை தடுப்பூசி).\n• **விற்பனை விலை**: உயிருடன் 1 கிலோ ₹350 முதல் ₹450 வரை விற்பனையாகிறது."
    },
    {
        "keywords": ["break-even", "நஷ்டம்", "லாப நஷ்டமற்ற நிலை", "break even point"],
        "en": "**Break-Even Point** is the exact sales volume where your business neither makes a profit nor incurs a loss. At this point, your total revenues equal all your fixed and variable costs. Every single unit you sell beyond the break-even point is pure profit for your family!",
        "ta": "**லாப நஷ்டமற்ற நிலை (Break-Even Point)** என்பது உங்கள் தொழில் நஷ்டமும் இல்லாமல், கூடுதல் லாபமும் இல்லாமல் செலவுகளை சரியாக ஈடுகட்டும் விற்பனை அளவாகும். இந்த இலக்கைத் தாண்டி நீங்கள் விற்கும் ஒவ்வொரு பொருளும் உங்கள் குடும்பத்திற்கான நிகர லாபமாகும்."
    }
]

def generate_ai_chat_response(message: str, language: str = "en", api_key: Optional[str] = None) -> str:
    """Provide intelligent advisory chat response either via Gemini API or rural domain expert engine."""
    client = get_gemini_client(api_key)
    
    # If live Gemini is configured, use it with a specialized rural micro-entrepreneur persona
    if client:
        try:
            sys_prompt = (
                "You are 'RuralBiz AI' (கிராமப்புற வணிக வழிகாட்டி), an empathetic, expert, and pragmatic "
                "hyper-local business and financial structuring advisor for rural micro-entrepreneurs in India (specifically Tamil Nadu). "
                "Explain business ideas, pricing, cash flow, break-even point, and banking schemes (like MUDRA, PM SVANidhi, PMEGP, SHG) "
                "in simple, actionable, jargon-free language with realistic rupee figures. "
                f"Respond in {'Tamil (தமிழ்)' if language == 'ta' else 'English'}. Keep formatting clear with bullet points and bold highlights."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"System Context: {sys_prompt}\nUser Question: {message}"
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print("Gemini API error in chatbot, falling back to local expert system:", e)

    # Local Knowledge Matcher
    msg_lower = message.lower()
    for item in CHAT_KNOWLEDGE_BASE:
        if any(kw.lower() in msg_lower for kw in item["keywords"]):
            return item["ta"] if language == "ta" else item["en"]

    # Default Contextual Response
    if language == "ta":
        return (
            "வணக்கம்! நான் உங்கள் **RuralBiz AI** வணிக வழிகாட்டி.\n\n"
            "உங்கள் தொழில் யோசனை, அடக்கவிலை கணக்கீடு, அரசு முத்ரா (MUDRA) கடன் விவரங்கள், "
            "நாட்டுக்கோழி வளர்ப்பு, சிறுதானிய உணவு அல்லது சந்தைப்படுத்துதல் குறித்து எதையும் என்னிடம் கேட்கலாம். "
            "உதாரணத்திற்கு:\n"
            "• *'முத்ரா சிசு கடன் பெற என்ன ஆவணங்கள் தேவை?'*\n"
            "• *'உற்பத்தி செலவில் இருந்து விற்பனை விலையை எப்படி கணக்கிடுவது?'*\n"
            "• *'₹20,000 முதலீட்டில் என்ன தொழில் துவங்கலாம்?'*"
        )
    else:
        return (
            "Hello! I am your **RuralBiz AI** Business Advisor.\n\n"
            "You can ask me anything regarding rural micro-business ideas, pricing calculations, break-even analysis, "
            "MUDRA / SVANidhi loan readiness, cash book accounting, or hyper-local marketing strategies.\n\n"
            "Try asking:\n"
            "• *'How to apply for MUDRA Shishu loan?'*\n"
            "• *'How to calculate profit margin and selling price?'*\n"
            "• *'What business can I start with ₹25,000 in a village?'*\n"
            "• *'How to manage daily cash book and working capital?'*"
        )
