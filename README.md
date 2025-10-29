# JobConnect: Student Career and Job Finder Platform

## Project Overview
JobConnect is a web-based platform that connects students and recent graduates with verified employers through secure job postings, skill-based matching, and streamlined application workflows. Built with Django and Supabase, it offers role-based dashboards for students, employers, and admins—enabling job searches, postings, resume uploads, and real-time communication—all in one centralized career hub.

## Technology Stack

- **Framework**: Django (Python) 
- **Frontend**: HTML, CSS, Vanilla JavaScript 
- **Database**: Supabase 
- **Design/Wireframing**: Figma 
- **Version Control**: GitHub

## Setup & Run Instructions

### 🧱 Prerequisites
- Python 3.11 or above  
- Django 4.x  
- Supabase project (with session pooler)  
- Git installed  

### ⚙️ Installation Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/rmcky0/JobConnect.git
   cd JobConnect
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate     # On macOS/Linux
   env\Scripts\activate        # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root with:
   ```env
   DATABASE_URL=DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<database>
   SUPABASE_URL=https://abewsixrnjnfrlhotyvu.supabase.co
   SUPABASE_KEY=<your-supabase-key>
   DEBUG=True

   SUPABASE_S3_ACCESS_KEY=<storage-access-key>
   SUPABASE_S3_SECRET_KEY=<storage-secret-key>
   SUPABASE_BUCKET_NAME=jobconnect-media
   SUPABASE_PROJECT_ID=abewsixrnjnfrlhotyvu
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

7. **Access the app**
   Open your browser and visit:
   ```
   http://127.0.0.1:8000/
   ```

---

## 👥 Team Members

- Paul Andrie Bibit - Product Owner - paulandrie.bibit@cit.edu
- Justine Filip Custodio - Business Analyst - justinefilip.custodio@cit.edu
- Van Andrae Bigtasin - Scrum Master - vanandrae.bigtasin@cit.edu
- Richemmae V. Bigno - Developer - richemmae.bigno@cit.edu 
- Isaac Raphael Cortes - Developer - isaacraphael.cortes@cit.edu
- Ken Daniel Cortes - Developer - kendaniel.cortes@cit.edu

---

## 🌐 Deployed Link
🔗 *(Coming soon)*


