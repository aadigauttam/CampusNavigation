from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import sqlite3
import os
import uvicorn

app = FastAPI(title="Campus Assistant API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "campus.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            floor TEXT NOT NULL,
            room_number TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proctors (
            usn TEXT PRIMARY KEY,
            proctor_name TEXT NOT NULL,
            title TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            location TEXT NOT NULL
        );
    """)
    
    cursor.executescript("DELETE FROM rooms; DELETE FROM proctors;")
    
    # ECE Department Data
    rooms = [
        ('rm_ece_hod', 'ECE HOD (Dr. Sobha Rani)', 'Offices', '1st Floor', 'Right Wing'),
        ('rm_ladies_lounge', 'Ladies Lounge', 'Amenities', '1st Floor', '107'),
        ('rm_dsd', 'Digital System Design Lab', 'Labs', '1st Floor', 'A120'),
        ('rm_comm_analog', 'Communication & Analog Circuits Lab', 'Labs', '1st Floor', 'A121'),
        ('rm_adv_comm', 'Advanced Communication Lab', 'Labs', '1st Floor', 'A122'),
        ('rm_dsp', 'Digital Signal Processing Lab', 'Labs', '1st Floor', 'A123'),
        ('rm_mmm', 'Mechanical Measurements Lab', 'Labs', '2nd Floor', 'A203'),
        ('rm_cim', 'Computer Integrated Mfg Lab', 'Labs', '2nd Floor', 'A204'),
        ('rm_camd', 'CAMD Modelling Lab', 'Labs', '2nd Floor', 'A205'),
        ('rm_thin_films', 'Thin Films & Optoelectronic Lab', 'Labs', '2nd Floor', 'A219'),
        ('rm_cner', 'CNER', 'Labs', '2nd Floor', 'A220'),
        ('rm_hdl', 'HDL & Embedded Controller Lab', 'Labs', '2nd Floor', 'A221'),
        ('rm_vlsi_2', 'VLSI Laboratory', 'Labs', '2nd Floor', 'A222'),
        ('rm_vlsi_design', 'VLSI Design Lab', 'Labs', '3rd Floor', 'A317'),
        ('rm_ece_project', 'ECE Project Lab', 'Labs', '3rd Floor', 'A318'),
        ('rm_basic_elec', 'Basic Electronics Lab', 'Labs', '3rd Floor', 'A319'),
        ('rm_electronic_circuits', 'Electronic Circuits Lab', 'Labs', '4th Floor', 'A404'),
        ('rm_shakuntala', 'Shakuntala Devi Lab', 'Labs', '4th Floor', 'A405'),
        ('rm_research', 'Research and Project Lab', 'Labs', '4th Floor', 'A432')
    ]
    cursor.executemany("INSERT INTO rooms (id, name, category, floor, room_number) VALUES (?, ?, ?, ?, ?)", rooms)

    # Proctor Metadata
    proctor_metadata = {
        "Dr. Thejaswini S": ("Associate Professor", "9008637144", "thejaswini.s@bmsit.in", "3rd Floor"),
        "Dr. Mamatha K R": ("Assistant Professor", "9972042574", "mamathakr@bmsit.in", "1st Floor"),
        "Dr. Shivarudraiah B": ("Assistant Professor", "9482138388", "shivab@bmsit.in", "2nd Floor"),
        "Prof. Chandra Prabha R": ("Assistant Professor", "8867618157", "chandra@bmsit.in", "Ground Floor"),
        "Dr. Jayadeva G S": ("Professor", "9538303888", "jayadevags@bmsit.in", "2nd Floor"),
        "Dr. Dankan Gowda V": ("Assistant Professor", "9844554940", "dankan.v@bmsit.in", "3rd Floor (Middle)"),
        "Dr. Anil Kumar D": ("Professor", "9886216203", "anilkumard81@bmsit.in", "Location not available"),
        "Dr. Laxmisagar H S": ("Assistant Professor", "8123008252", "sagar8.hs@bmsit.in", "Location not available"),
        "Dr. Thyagaraj Tanjavur": ("Assistant Professor", "9845133392", "thyagaraj_tanjavur@bmsit.in", "Location not available")
    }

    # Clean Dictionary mapping for USNs
    raw_usn_mappings = {
        "Dr. Thejaswini S": ["1BY24EC003", "1BY24EC005", "1BY24EC006", "1BY24EC008", "1BY24EC011", "1BY24EC013", "1BY24EC014", "1BY24EC015", "1BY24EC016", "1BY24EC029", "1BY24EC030", "1BY24EC038", "1BY24EC039", "1BY24EC045", "1BY24EC046", "1BY24EC052", "1BY24EC053", "1BY24EC062", "1BY24EC073", "1BY24EC074", "1BY25EC400", "1BY25EC401", "1BY24EC193", "1BY24EC194"],
        "Dr. Mamatha K R": ["1BY24EC076", "1BY24EC081", "1BY24EC084", "1BY24EC087", "1BY24EC093", "1BY24EC095", "1BY24EC096", "1BY24EC098", "1BY24EC105", "1BY24EC109", "1BY24EC110", "1BY24EC113", "1BY24EC116", "1BY24EC117", "1BY24EC119", "1BY24EC120", "1BY24EC121", "1BY24EC124", "1BY24EC131", "1BY24EC132", "1BY24EC133", "1BY24EC134", "1BY25EC402", "1BY25EC403"],
        "Dr. Shivarudraiah B": ["1BY24EC135", "1BY24EC136", "1BY24EC139", "1BY24EC141", "1BY24EC142", "1BY24EC145", "1BY24EC156", "1BY24EC157", "1BY24EC158", "1BY24EC161", "1BY24EC164", "1BY24EC165", "1BY24EC168", "1BY24EC169", "1BY24EC170", "1BY24EC174", "1BY24EC175", "1BY24EC179", "1BY24EC180", "1BY24EC184", "1BY24EC187", "1BY25EC404", "1BY25EC405"],
        "Prof. Chandra Prabha R": ["1BY24EC004", "1BY24EC021", "1BY24EC017", "1BY24EC018", "1BY24EC020", "1BY24EC022", "1BY24EC023", "1BY24EC024", "1BY24EC025", "1BY24EC028", "1BY24EC032", "1BY24EC033", "1BY24EC034", "1BY24EC035", "1BY24EC042", "1BY24EC044", "1BY24EC047", "1BY24EC050", "1BY24EC051", "1BY24EC055", "1BY25EC406", "1BY25EC407"],
        "Dr. Jayadeva G S": ["1BY24EC063", "1BY24EC064", "1BY24EC065", "1BY24EC067", "1BY24EC068", "1BY24EC070", "1BY24EC071", "1BY24EC077", "1BY24EC083", "1BY24EC085", "1BY24EC086", "1BY24EC088", "1BY24EC089", "1BY24EC094", "1BY24EC101", "1BY24EC103", "1BY24EC106", "1BY24EC107", "1BY25EC408", "1BY25EC409", "1BY23EC133"],
        "Dr. Dankan Gowda V": ["1BY24EC112", "1BY24EC115", "1BY24EC118", "1BY24EC122", "1BY24EC125", "1BY24EC127", "1BY24EC128", "1BY24EC143", "1BY24EC148", "1BY24EC150", "1BY24EC151", "1BY24EC155", "1BY24EC159", "1BY24EC160", "1BY24EC162", "1BY24EC166", "1BY24EC177", "1BY24EC182", "1BY24EC183", "1BY24EC186", "1BY24EC189", "1BY24EC190", "1BY25EC410", "1BY25EC411"],
        "Dr. Anil Kumar D": ["1BY24EC001", "1BY24EC002", "1BY24EC007", "1BY24EC010", "1BY24EC012", "1BY24EC019", "1BY24EC026", "1BY24EC027", "1BY24EC036", "1BY24EC037", "1BY24EC040", "1BY24EC041", "1BY24EC043", "1BY24EC049", "1BY24EC054", "1BY24EC056", "1BY24EC057", "1BY24EC058", "1BY24EC059", "1BY24EC060", "1BY24EC061", "1BY25EC412", "1BY25EC413"],
        "Dr. Laxmisagar H S": ["1BY24EC066", "1BY24EC069", "1BY24EC072", "1BY24EC075", "1BY24EC078", "1BY24EC079", "1BY24EC082", "1BY24EC091", "1BY24EC092", "1BY24EC097", "1BY24EC102", "1BY24EC104", "1BY24EC108", "1BY24EC111", "1BY24EC114", "1BY24EC123", "1BY24EC126", "1BY24EC129", "1BY24EC130", "1BY24EC137", "1BY24EC154", "1BY25EC414", "1BY25EC415"],
        "Dr. Thyagaraj Tanjavur": ["1BY24EC138", "1BY24EC140", "1BY24EC144", "1BY24EC146", "1BY24EC147", "1BY24EC149", "1BY24EC152", "1BY24EC153", "1BY24EC163", "1BY24EC171", "1BY24EC172", "1BY24EC173", "1BY24EC176", "1BY24EC178", "1BY24EC185", "1BY24EC188", "1BY24EC191", "1BY24EC192", "1BY22EC027", "1BY23EC011", "1BY25EC416", "1BY25EC417"]
    }

    # Combine mapping with metadata dynamically
    proctor_db_data = []
    for p_name, usns in raw_usn_mappings.items():
        meta = proctor_metadata[p_name]
        for usn in usns:
            proctor_db_data.append((usn, p_name, meta[0], meta[1], meta[2], meta[3]))
        
    cursor.executemany("INSERT INTO proctors (usn, proctor_name, title, phone, email, location) VALUES (?, ?, ?, ?, ?, ?)", proctor_db_data)
    
    conn.commit()
    conn.close()

init_db()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sir M. Visvesvaraya Block - Kiosk Wayfinding</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #fff; margin: 0; padding: 30px; }
        .top-banner { text-align: center; margin-bottom: 30px; }
        .top-banner h1 { margin: 0; color: #3498db; font-size: 28px; font-weight: 700; }
        .top-banner p { margin: 8px 0 0; color: #999; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; }

        .kiosk-container { display: flex; gap: 30px; max-width: 1200px; margin: 0 auto; }
        
        .sidebar { width: 450px; display: flex; flex-direction: column; gap: 18px; }
        
        .panel { background: #151515; border: 1px solid #333; padding: 20px; border-radius: 12px; }
        .panel label { font-size: 12px; color: #bbb; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 8px; }
        select, input { width: 100%; padding: 12px; background: #0a0a0a; color: #fff; border: 1px solid #444; border-radius: 8px; font-size: 15px; outline: none; }
        select:focus, input:focus { border-color: #3498db; }
        
        .main-tabs { display: flex; gap: 10px; margin-bottom: 10px; }
        .tab-btn { flex: 1; padding: 12px; background: #222; color: #aaa; border: 1px solid #333; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .tab-btn.active { background: #3498db; color: #fff; border-color: #3498db; }

        #directoryView, #studentServicesView { display: none; }
        #directoryView.active, #studentServicesView.active { display: block; }
        
        .category-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; }
        .cat-btn { background: #222; color: #ddd; border: 1px solid #444; padding: 12px; border-radius: 8px; font-size: 13px; cursor: pointer; }
        .cat-btn.active, .cat-btn:hover { background: #444; border-color: #3498db; color: #fff; }
        
        .facility-list { height: 350px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 5px; }
        .facility-card { background: #1a1a1a; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; cursor: pointer; transition: 0.2s; }
        .facility-card:hover { border-color: #3498db; background: #222; }
        
        .search-btn { width: 100%; padding: 14px; background: #3498db; color: #fff; font-weight: bold; font-size: 14px; border: none; border-radius: 8px; cursor: pointer; margin-top: 10px; }
        .proctor-result { margin-top: 15px; padding: 15px; background: #111; border: 1px solid #444; border-radius: 8px; display: none; }
        
        .contact-detail { font-size: 14px; margin-top: 8px; color: #bbb; display: flex; align-items: center; gap: 8px; }
        .contact-detail i { color: #3498db; font-style: normal; font-weight: bold; }
        .location-tag { display: inline-block; background: rgba(52, 152, 219, 0.1); color: #3498db; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-top: 10px; border: 1px solid rgba(52,152,219,0.3); }
        .location-tag.unknown { background: rgba(231, 76, 60, 0.1); color: #e74c3c; border-color: rgba(231,76,60,0.3); }

        /* Navigation Display Area */
        .directions-panel { flex: 1; background: #151515; border: 1px solid #333; border-radius: 12px; padding: 40px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
        .directions-panel h2 { color: #fff; font-size: 32px; margin: 0 0 10px 0; }
        .directions-panel .room-num { color: #3498db; font-size: 24px; font-weight: bold; margin-bottom: 30px; }
        .directions-box { background: #222; padding: 25px; border-radius: 12px; width: 100%; font-size: 18px; line-height: 1.6; color: #ddd; border: 1px solid #444; }
    </style>
</head>
<body>

    <div class="top-banner">
        <h1>SIR M. VISVESVARAYA BLOCK</h1>
        <p>Interactive Campus Directory</p>
    </div>

    <div class="kiosk-container">
        <div class="sidebar">
            <div class="panel">
                <label>📍 Where are you right now?</label>
                <select id="startFloor">
                    <option value="Ground Floor">Ground Floor</option>
                    <option value="1st Floor">1st Floor</option>
                    <option value="2nd Floor">2nd Floor</option>
                    <option value="3rd Floor">3rd Floor</option>
                    <option value="4th Floor">4th Floor</option>
                </select>
            </div>

            <div class="main-tabs">
                <button class="tab-btn active" onclick="switchMainTab('directoryView', this)">🏢 Directory</button>
                <button class="tab-btn" onclick="switchMainTab('studentServicesView', this)">🎓 Student Services</button>
            </div>

            <div id="directoryView" class="panel active">
                <div class="category-row">
                    <button class="cat-btn active" onclick="loadCategory('Offices', this)">Offices</button>
                    <button class="cat-btn" onclick="loadCategory('Labs', this)">Labs</button>
                    <button class="cat-btn" onclick="loadCategory('Amenities', this)">Amenities</button>
                </div>
                <div class="facility-list" id="facilityList"></div>
            </div>

            <div id="studentServicesView" class="panel">
                <label>Find Your Assigned Proctor</label>
                <input type="text" id="usnInput" placeholder="Enter USN (e.g., 1BY24EC006)" style="text-transform: uppercase;">
                <button class="search-btn" onclick="lookupProctor()">Search Proctor</button>
                
                <div id="proctorCard" class="proctor-result">
                    <h3 id="p_usn" style="margin:0 0 5px 0; color:#3498db; font-size:16px;"></h3>
                    <div style="font-size: 22px; font-weight: bold; color: #fff; margin-bottom: 5px;" id="p_name"></div>
                    <div style="color: #888; font-size: 14px; margin-bottom: 12px;" id="p_title"></div>
                    
                    <div class="contact-detail"><i>📞</i> <span id="p_phone"></span></div>
                    <div class="contact-detail"><i>✉️</i> <span id="p_email"></span></div>
                    
                    <div id="p_location" class="location-tag"></div>
                </div>
            </div>
        </div>

        <div class="directions-panel" id="directionsPanel">
            <div style="color: #666; font-size: 20px;">Select a room or search a proctor to get directions.</div>
        </div>
    </div>

    <script>
        function switchMainTab(viewId, btnElem) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btnElem.classList.add('active');
            document.getElementById('directoryView').classList.remove('active');
            document.getElementById('studentServicesView').classList.remove('active');
            document.getElementById(viewId).classList.add('active');
        }

        async function loadCategory(catName, btnElem) {
            if (btnElem) {
                document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
                btnElem.classList.add('active');
            }
            const res = await fetch(`/rooms?category=${catName}`);
            const rooms = await res.json();
            const list = document.getElementById('facilityList');
            list.innerHTML = '';
            
            rooms.forEach(r => {
                const card = document.createElement('div');
                card.className = 'facility-card';
                card.onclick = () => showDirections(r.name, r.room_number, r.floor);
                card.innerHTML = `
                    <div style="line-height:1.4;">
                        <strong style="display:block; color:#fff;">${r.name}</strong>
                        <span style="font-size:12px; color:#888;">${r.floor} • ${r.room_number}</span>
                    </div>
                    <span style="color:#3498db; font-size: 20px;">→</span>
                `;
                list.appendChild(card);
            });
        }

        function showDirections(roomName, roomNum, targetFloor) {
            const currentFloor = document.getElementById('startFloor').value;
            const panel = document.getElementById('directionsPanel');
            
            let directionsText = "";
            if (roomNum === "Location not available") {
                directionsText = "We do not have the exact office location for this faculty member yet.";
            } else if (currentFloor === targetFloor) {
                directionsText = `You are already on the <strong>${targetFloor}</strong>.<br><br>Walk down the corridor and look for <strong>${roomNum}</strong>.`;
            } else {
                directionsText = `You are currently on the <strong>${currentFloor}</strong>.<br><br>Take the stairs or elevator to the <strong>${targetFloor}</strong>.<br>Once there, walk down the corridor to find <strong>${roomNum}</strong>.`;
            }

            panel.innerHTML = `
                <h2>${roomName}</h2>
                <div class="room-num">${targetFloor} ${roomNum !== "Location not available" && roomNum !== targetFloor ? '| Room ' + roomNum : ''}</div>
                <div class="directions-box">${directionsText}</div>
            `;
        }

        async function lookupProctor() {
            const usn = document.getElementById('usnInput').value.trim();
            const card = document.getElementById('proctorCard');
            if (!usn) return;
            
            try {
                const res = await fetch(`/proctor?usn=${usn}`);
                if (!res.ok) throw new Error("USN not found");
                const data = await res.json();
                
                document.getElementById('p_usn').innerText = "PROCTOR ASSIGNMENT - " + data.usn;
                document.getElementById('p_name').innerText = data.proctor;
                document.getElementById('p_title').innerText = data.title;
                document.getElementById('p_phone').innerText = data.phone;
                document.getElementById('p_email').innerText = data.email;
                
                const locBadge = document.getElementById('p_location');
                if (data.location === "Location not available") {
                    locBadge.innerText = "📍 Location not available";
                    locBadge.className = "location-tag unknown";
                    showDirections(data.proctor, data.location, "Unknown Floor");
                } else {
                    locBadge.innerText = "📍 Office: " + data.location;
                    locBadge.className = "location-tag";
                    
                    // Show directions based on location data
                    let assumedFloor = data.location.includes("Floor") ? data.location : "Check location badge";
                    if (data.location === "3rd Floor (Middle)") assumedFloor = "3rd Floor";
                    showDirections(data.proctor, data.location, assumedFloor); 
                }
                
                card.style.display = 'block';
            } catch (err) {
                card.style.display = 'none';
                alert("USN not found in 4th Semester records.");
            }
        }

        loadCategory('Labs');
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_index():
    return HTML_CONTENT

@app.get("/rooms")
def get_rooms(category: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, floor, room_number FROM rooms WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "category": r[2], "floor": r[3], "room_number": r[4]} for r in rows]

@app.get("/proctor")
def get_proctor(usn: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT proctor_name, title, phone, email, location FROM proctors WHERE usn = ?", (usn.upper(),))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "usn": usn.upper(), 
            "proctor": result[0],
            "title": result[1],
            "phone": result[2],
            "email": result[3],
            "location": result[4]
        }
    raise HTTPException(status_code=404)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)