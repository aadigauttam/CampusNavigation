from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import sqlite3
import os
import datetime
import uvicorn

app = FastAPI(title="Campus Assistant API")

# VERCEL FIX: Route database to the writable /tmp directory if deployed
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    DB_PATH = "/tmp/campus.db"
else:
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
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            day TEXT NOT NULL,
            start_min INTEGER NOT NULL,
            end_min INTEGER NOT NULL,
            time_label TEXT NOT NULL,
            subject TEXT NOT NULL,
            faculty TEXT NOT NULL,
            room TEXT NOT NULL
        );
    """)
    
    cursor.executescript("DELETE FROM rooms; DELETE FROM proctors; DELETE FROM timetable;")
    
    # --- 1. DIRECTORY DATA ---
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

    # --- 2. PROCTOR DATA ---
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

    proctor_db_data = []
    for p_name, usns in raw_usn_mappings.items():
        meta = proctor_metadata[p_name]
        for usn in usns:
            proctor_db_data.append((usn, p_name, meta[0], meta[1], meta[2], meta[3]))
            
    cursor.executemany("INSERT INTO proctors (usn, proctor_name, title, phone, email, location) VALUES (?, ?, ?, ?, ?, ?)", proctor_db_data)

    # --- 3. TIMETABLE DATA ---
    schedule = [
        # SECTION A (Room A424)
        ('A', 'Monday', 510, 565, '08:30-09:25', 'ARM', 'Dr. Shivarudraiah B', 'A424'),
        ('A', 'Monday', 565, 620, '09:25-10:20', 'DSP', 'Dr. Mamatha K R', 'A424'),
        ('A', 'Monday', 640, 750, '10:40-12:30', 'DSP LAB / ARM LAB', 'Dr. Mamatha / Dr. Shivarudraiah', 'A1 / A2 Labs'),
        ('A', 'Tuesday', 510, 565, '08:30-09:25', 'ME', 'Dr. Asha K', 'A424'),
        ('A', 'Tuesday', 565, 620, '09:25-10:20', 'ARM', 'Dr. Shivarudraiah B', 'A424'),
        ('A', 'Tuesday', 640, 695, '10:40-11:35', 'DSP', 'Dr. Mamatha K R', 'A424'),
        ('A', 'Wednesday', 510, 565, '08:30-09:25', 'ARM', 'Dr. Shivarudraiah B', 'A424'),
        ('A', 'Thursday', 510, 565, '08:30-09:25', 'DSP', 'Dr. Mamatha K R', 'A424'),
        ('A', 'Thursday', 565, 620, '09:25-10:20', 'RMIPR', 'Dr. Rashmi N', 'A424'),
        ('A', 'Friday', 565, 620, '09:25-10:20', 'ME', 'Dr. Asha K', 'A424'),
        
        # SECTION B (Room A320)
        ('B', 'Monday', 510, 565, '08:30-09:25', 'ME', 'Dr. Deepa N Reddy', 'A320'),
        ('B', 'Monday', 565, 620, '09:25-10:20', 'DSP', 'Dr. Thejaswini S', 'A320'),
        ('B', 'Monday', 640, 695, '10:40-11:35', 'ARM', 'Dr. Suryakanth B', 'A320'),
        ('B', 'Tuesday', 510, 565, '08:30-09:25', 'DSP', 'Dr. Thejaswini S', 'A320'),
        ('B', 'Tuesday', 565, 620, '09:25-10:20', 'RMIPR', 'Dr. Soumya Vastrad', 'A320'),
        
        # SECTION C (Room A321)
        ('C', 'Monday', 510, 565, '08:30-09:25', 'DSP', 'Dr. Vijayalakshmi G V', 'A321'),
        ('C', 'Monday', 565, 620, '09:25-10:20', 'ARM', 'Dr. Anil Kumar D', 'A321'),
        ('C', 'Tuesday', 510, 565, '08:30-09:25', 'RMIPR', 'Dr. Asha G H', 'A321'),
        ('C', 'Tuesday', 565, 620, '09:25-10:20', 'ARM', 'Dr. Anil Kumar D', 'A321')
    ]
    cursor.executemany("INSERT INTO timetable (section, day, start_min, end_min, time_label, subject, faculty, room) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", schedule)
    
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
        body { font-family: 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #fff; margin: 0; padding: 25px; }
        .top-banner { text-align: center; margin-bottom: 25px; }
        .top-banner h1 { margin: 0; color: #3498db; font-size: 26px; font-weight: 700; }
        .top-banner p { margin: 6px 0 0; color: #999; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; }

        .kiosk-container { display: flex; gap: 30px; max-width: 1200px; margin: 0 auto; }
        
        .sidebar { width: 450px; display: flex; flex-direction: column; gap: 15px; }
        .panel { background: #151515; border: 1px solid #333; padding: 20px; border-radius: 12px; }
        
        .main-tabs { display: flex; gap: 8px; margin-bottom: 10px; }
        .tab-btn { flex: 1; padding: 12px 6px; background: #222; color: #aaa; border: 1px solid #333; border-radius: 8px; font-size: 13px; font-weight: bold; cursor: pointer; transition: 0.2s; text-align: center;}
        .tab-btn.active { background: #3498db; color: #fff; border-color: #3498db; }
        
        .view { display: none; }
        .view.active { display: block; }
        
        label { font-size: 12px; color: #bbb; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 8px; }
        select, input { width: 100%; padding: 12px; background: #0a0a0a; color: #fff; border: 1px solid #444; border-radius: 8px; font-size: 14px; outline: none; margin-bottom: 15px; }
        select:focus, input:focus { border-color: #3498db; }
        
        /* Directory Specifics */
        .category-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; }
        .cat-btn { background: #222; color: #ddd; border: 1px solid #444; padding: 12px; border-radius: 8px; font-size: 12px; cursor: pointer; }
        .cat-btn.active, .cat-btn:hover { background: #444; border-color: #3498db; color: #fff; }
        .facility-list { height: 280px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 5px; }
        .facility-card { background: #1a1a1a; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; cursor: pointer; }
        .facility-card:hover { border-color: #3498db; background: #222; }

        /* Actions & Cards */
        .action-btn { width: 100%; padding: 14px; background: #3498db; color: #fff; font-weight: bold; font-size: 14px; border: none; border-radius: 8px; cursor: pointer; }
        .result-card { margin-top: 15px; padding: 15px; background: #111; border: 1px solid #444; border-radius: 8px; display: none; }
        
        .contact-detail { font-size: 14px; margin-top: 8px; color: #bbb; display: flex; align-items: center; gap: 8px; }
        .contact-detail i { color: #3498db; font-style: normal; font-weight: bold; }
        
        /* Main Directions Area */
        .directions-panel { flex: 1; background: #151515; border: 1px solid #333; border-radius: 12px; padding: 40px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
        .directions-panel h2 { color: #fff; font-size: 32px; margin: 0 0 10px 0; }
        .directions-panel .room-num { color: #3498db; font-size: 24px; font-weight: bold; margin-bottom: 30px; }
        .directions-box { background: #222; padding: 25px; border-radius: 12px; width: 100%; font-size: 18px; line-height: 1.6; color: #ddd; border: 1px solid #444; }
    </style>
</head>
<body>

    <div class="top-banner">
        <h1>SIR M. VISVESVARAYA BLOCK</h1>
        <p>Interactive Campus Directory & AI Assistant</p>
    </div>

    <div class="kiosk-container">
        <div class="sidebar">
            <div class="panel" style="padding-bottom: 5px;">
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
                <button class="tab-btn active" onclick="switchTab('directoryView', this)">🏢 Directory</button>
                <button class="tab-btn" onclick="switchTab('studentServicesView', this)">🎓 Proctors</button>
                <button class="tab-btn" onclick="switchTab('scheduleView', this)">📅 Schedule</button>
            </div>

            <!-- 1. DIRECTORY TAB -->
            <div id="directoryView" class="panel view active">
                <div class="category-row">
                    <button class="cat-btn active" onclick="loadCategory('Offices', this)">Offices</button>
                    <button class="cat-btn" onclick="loadCategory('Labs', this)">Labs</button>
                    <button class="cat-btn" onclick="loadCategory('Amenities', this)">Amenities</button>
                </div>
                <div class="facility-list" id="facilityList"></div>
            </div>

            <!-- 2. PROCTOR TAB -->
            <div id="studentServicesView" class="panel view">
                <label>Find Your Assigned Proctor</label>
                <input type="text" id="usnInput" placeholder="Enter USN (e.g., 1BY24EC006)" style="text-transform: uppercase;">
                <button class="action-btn" onclick="lookupProctor()">Search Proctor</button>
                
                <div id="proctorCard" class="result-card">
                    <h3 id="p_usn" style="margin:0 0 5px 0; color:#3498db; font-size:14px;"></h3>
                    <div style="font-size: 20px; font-weight: bold; color: #fff; margin-bottom: 5px;" id="p_name"></div>
                    <div style="color: #888; font-size: 13px; margin-bottom: 12px;" id="p_title"></div>
                    <div class="contact-detail"><i>📞</i> <span id="p_phone"></span></div>
                    <div class="contact-detail"><i>✉️</i> <span id="p_email"></span></div>
                </div>
            </div>

            <!-- 3. LIVE SCHEDULE TAB -->
            <div id="scheduleView" class="panel view">
                <label>Find Professor's Live Location</label>
                <div style="display:flex; gap:10px; margin-bottom:20px;">
                    <input type="text" id="facultyName" placeholder="Enter name (e.g. Mamatha)" style="margin-bottom:0;">
                    <button class="action-btn" style="width:auto; padding:0 20px;" onclick="trackFaculty()">Track</button>
                </div>

                <label>Check 5th Sem Section Status</label>
                <div style="display:flex; gap:10px;">
                    <select id="sectionSelect" style="margin-bottom:0;">
                        <option value="A">Section A</option>
                        <option value="B">Section B</option>
                        <option value="C">Section C</option>
                    </select>
                    <button class="action-btn" style="width:auto; padding:0 20px;" onclick="checkSchedule()">Check</button>
                </div>
            </div>
        </div>

        <!-- MAIN DISPLAY PANEL -->
        <div class="directions-panel" id="directionsPanel">
            <div style="color: #666; font-size: 20px;">Select a room, search a proctor, or check the schedule.</div>
        </div>
    </div>

    <script>
        function switchTab(viewId, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(viewId).classList.add('active');
            document.getElementById('directionsPanel').innerHTML = `<div style="color: #666; font-size: 20px;">Awaiting Query...</div>`;
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
                card.style.display = 'block';

                let assumedFloor = data.location.includes("Floor") ? data.location : "Check Directory";
                if (data.location === "3rd Floor (Middle)") assumedFloor = "3rd Floor";
                showDirections(data.proctor, data.location, assumedFloor); 
                
            } catch (err) {
                card.style.display = 'none';
                alert("USN not found in records.");
            }
        }

        async function trackFaculty() {
            const name = document.getElementById('facultyName').value.trim();
            if (!name) return;
            
            try {
                const res = await fetch(`/faculty_status?name=${name}`);
                const data = await res.json();
                const panel = document.getElementById('directionsPanel');
                
                if (data.status === "out_of_hours") {
                    panel.innerHTML = `
                        <h2 style="color:#7f8c8d;">OUTSIDE COLLEGE HOURS</h2>
                        <div class="directions-box">It is currently before 8:30 AM or after 4:30 PM.<br>Regular classes are not in session.</div>
                    `;
                } else if (data.status === "teaching") {
                    panel.innerHTML = `
                        <h2 style="color:#e74c3c;">IN CLASS NOW</h2>
                        <div class="room-num">Room ${data.room}</div>
                        <div class="directions-box">
                            Currently teaching <strong>${data.subject}</strong> (Sec ${data.section})<br>
                            Time: ${data.time_label}<br><br>
                            <span style="color:#e74c3c; font-size:16px;">Please do not disturb unless urgent.</span>
                        </div>
                    `;
                } else {
                    panel.innerHTML = `
                        <h2 style="color:#2ecc71;">PROFESSOR AVAILABLE</h2>
                        <div class="directions-box">No class scheduled right now.<br>They are likely in their cabin. Please check the directory for office locations.</div>
                    `;
                }
            } catch (err) {
                alert("Could not retrieve faculty data.");
            }
        }

        async function checkSchedule() {
            const sec = document.getElementById('sectionSelect').value;
            
            try {
                const res = await fetch(`/section_status?sec=${sec}`);
                const data = await res.json();
                const panel = document.getElementById('directionsPanel');
                
                if (data.status === "out_of_hours") {
                    panel.innerHTML = `
                        <h2 style="color:#7f8c8d;">OUTSIDE COLLEGE HOURS</h2>
                        <div class="directions-box">It is currently before 8:30 AM or after 4:30 PM.<br>Regular classes are not in session.</div>
                    `;
                } else if (data.status === "active") {
                    panel.innerHTML = `
                        <h2 style="color:#e74c3c;">CLASS IN SESSION</h2>
                        <div class="room-num">Room ${data.room}</div>
                        <div class="directions-box">
                            <strong>${data.subject}</strong> with ${data.faculty}<br>
                            <span style="color:#888; font-size:15px;">${data.time_label}</span>
                        </div>
                    `;
                } else if (data.status === "upcoming") {
                    panel.innerHTML = `
                        <h2 style="color:#3498db;">FREE PERIOD</h2>
                        <div class="directions-box">
                            <em>No class right now.</em><br><br>
                            <strong>Up Next:</strong> ${data.subject} with ${data.faculty}<br>
                            <strong>Room:</strong> ${data.room} (${data.time_label})
                        </div>
                    `;
                } else {
                    panel.innerHTML = `
                        <h2 style="color:#2ecc71;">CLASSES OVER</h2>
                        <div class="directions-box">No more classes scheduled for Section ${sec} today.</div>
                    `;
                }
            } catch (err) {
                alert("Error fetching schedule.");
            }
        }

        loadCategory('Offices');
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

def get_real_time():
    now = datetime.datetime.now()
    day_name = now.strftime('%A')
    current_min = now.hour * 60 + now.minute
    return day_name, current_min

@app.get("/faculty_status")
def get_faculty_status(name: str):
    day_name, current_min = get_real_time()
    
    if current_min < 510 or current_min > 990 or day_name == 'Sunday':
        return {"status": "out_of_hours"}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT subject, section, room, time_label 
        FROM timetable 
        WHERE faculty LIKE ? AND day = ? AND ? >= start_min AND ? < end_min
    """, ('%' + name + '%', day_name, current_min, current_min))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"status": "teaching", "subject": result[0], "section": result[1], "room": result[2], "time_label": result[3]}
    return {"status": "free"}

@app.get("/section_status")
def get_section_status(sec: str):
    day_name, current_min = get_real_time()
    
    if current_min < 510 or current_min > 990 or day_name == 'Sunday':
        return {"status": "out_of_hours"}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT subject, faculty, room, time_label 
        FROM timetable 
        WHERE section = ? AND day = ? AND ? >= start_min AND ? < end_min
    """, (sec, day_name, current_min, current_min))
    live_class = cursor.fetchone()
    
    if live_class:
        conn.close()
        return {"status": "active", "subject": live_class[0], "faculty": live_class[1], "room": live_class[2], "time_label": live_class[3]}
        
    cursor.execute("""
        SELECT subject, faculty, room, time_label 
        FROM timetable 
        WHERE section = ? AND day = ? AND start_min > ?
        ORDER BY start_min ASC LIMIT 1
    """, (sec, day_name, current_min))
    next_class = cursor.fetchone()
    
    conn.close()
    
    if next_class:
        return {"status": "upcoming", "subject": next_class[0], "faculty": next_class[1], "room": next_class[2], "time_label": next_class[3]}
        
    return {"status": "done"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)