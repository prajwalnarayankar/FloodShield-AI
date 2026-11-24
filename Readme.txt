================================================================================
PROJECT SUBMISSION - AIL06 LAB (INTELLIGENT SYSTEMS LABORATORY)
DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING
CANARA ENGINEERING COLLEGE, MANGALURU
================================================================================

1. PROJECT TITLE:
   Flood Risk Prediction and Alert System using Machine Learning (FloodShield-AI)
   Sub-title: Yadgir District Flood Risk Monitoring & Hydrological Decision Support System
   (Bhima & Upper Krishna Basin Real-Time Telemetry & Hybrid Safety Engine)

2. TEAM MEMBERS:
   Sl.No.   Name                        USN
   ------------------------------------------------------------
   1.       PRAJWAL NARAYANKAR          4CB23AI067
   2.       VIGNESH R POOJARY           4CB23AI123
   3.       AMARESH PRABHU BARASHATTI   4CB23AI127

   Under the Guidance of:
   Mr. Sandesh Kamath
   Assistant Professor, Dept. of AI & ML, Canara Engineering College

3. SYSTEM DETAILS (AIL06 LAB):
   Lab: AIL06 (Project Lab / Intelligent Systems Laboratory)
   System Number: [ENTER YOUR AIL06 PC NUMBER HERE, e.g., SYS-14]

4. SOFTWARE REQUIREMENTS & DOWNLOAD LINKS:
   - Python 3.11+: https://www.python.org/downloads/
   - Google Chrome / Microsoft Edge: Pre-installed on Windows
   - Node.js v18+ (Optional; frontend is pre-compiled in dist/): https://nodejs.org/
   - PostgreSQL 14+ (Optional; system falls back to local database): https://www.postgresql.org/download/
   - Visual Studio Code: https://code.visualstudio.com/

5. DATASETS USED:
   - Central Water Commission (CWC) & National Water Informatics Centre (NWIC):
     Continuous hydrological river stage (water level in meters) and discharge (m3/s) telemetry.
   - India Meteorological Department (IMD):
     Catchment precipitation telemetry and district-level weather advisories.
   - Historical Indian River Basin Flood Observations:
     Located in ml/dataset/flood_risk_dataset_india.xlsx

6. DETAILS OF DATASET GENERATED:
   File Name: NewDataset_FloodShieldHydrological_Yadgir.csv
   Description: A high-density 15-parameter hydrological dataset incorporating:
     - Water Level (m), Discharge (m3/s), 1h/6h/24h Water Level Change Rates
     - Catchment and Upstream Basin Rainfall (Maharashtra/Karnataka border)
     - Warning Level & Danger Level Proximity Ratios
     - Multi-class Ground Truth Targets: LOW, MEDIUM, HIGH, EXTREME
   Total Samples: 3,500 synthesized and verified hydrological telemetry records.

7. EXECUTION INSTRUCTIONS:
   Step 1: Open terminal in project backend folder:
           cd backend
   Step 2: Activate virtual environment:
           .\venv\Scripts\activate
   Step 3: Run the automated verification test:
           python test_all_endpoints.py
   Step 4: Start the FastAPI backend server:
           uvicorn app.main:app --reload --port 8000
   Step 5: Open a second terminal for the frontend:
           cd frontend
           npm run dev
   Step 6: Open your browser at: http://localhost:5173 (or http://localhost:8000/docs for Swagger API)
================================================================================
