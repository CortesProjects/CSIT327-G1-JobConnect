# JobConnect: Student Career and Job Finder Platform

## Project Overview
JobConnect is a web-based platform that connects students and recent graduates with verified employers through secure job postings, skill-based matching, and streamlined application workflows. Built with Django and Supabase, it offers role-based dashboards for students, employers, and admins—enabling job searches, postings, resume uploads, and real-time communication—all in one centralized career hub.

## Technology Stack

- **Framework**: Django 4.2+ (Python 3.9+)
- **Frontend**: HTML, CSS, Vanilla JavaScript 
- **Database**: PostgreSQL (via Supabase)
- **Storage**: Supabase S3-compatible Storage
- **Design/Wireframing**: Figma 
- **Version Control**: GitHub
- **Deployment**: Render

## Setup & Run Instructions

### 🧱 Prerequisites
- Python 3.9 or above  
- pip (Python package manager)
- Git installed  
- Supabase account with a project set up

### ⚙️ Installation Steps

#### 1. **Clone the repository**
```bash
git clone https://github.com/rmcky0/JobConnect.git
cd JobConnect/JobConnect
```

#### 2. **Create and activate a virtual environment**
```bash
# Create virtual environment
python -m venv env

# Activate on macOS/Linux
source env/bin/activate

# Activate on Windows
env\Scripts\activate
```

#### 3. **Install dependencies**
```bash
pip install -r requirements.txt
```

#### 4. **Configure environment variables**
Create a `.env` file in the `JobConnect/` directory (same level as `manage.py`) with the following:

```env
# Django Security
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# Database - Use your Supabase connection string
DATABASE_URL=postgresql://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Supabase
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_PROJECT_ID=YOUR_PROJECT_REF

# Supabase S3 Storage
SUPABASE_S3_ACCESS_KEY=your-s3-access-key
SUPABASE_S3_SECRET_KEY=your-s3-secret-key
SUPABASE_BUCKET_NAME=jobconnect-media

# AWS S3 Configuration
AWS_S3_REGION_NAME=ap-southeast-1
AWS_DEFAULT_ACL=public-read
```

**Note:** Replace the placeholder values with your actual Supabase credentials from:
- Database credentials: Supabase Dashboard → Project Settings → Database → Connection Pooling
- Storage credentials: Supabase Dashboard → Project Settings → API
- S3 credentials: Supabase Dashboard → Storage → Settings

#### 5. **Apply database migrations**
```bash
python manage.py migrate
```

#### 6. **Create a superuser (optional, for admin access)**
```bash
python manage.py createsuperuser
```

#### 7. **Collect static files (for production)**
```bash
python manage.py collectstatic --no-input
```

#### 8. **Run the development server**
```bash
python manage.py runserver
```

#### 9. **Access the application**
Open your browser and visit:
```
http://127.0.0.1:8000/
```

For admin panel access:
```
http://127.0.0.1:8000/admin/
```

---


## 🚀 Deployment

### Deploy to Render

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Set **Root Directory**: `JobConnect`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn JobConnect.wsgi:application`

3. **Add Environment Variables in Render**
   - Copy all variables from your `.env` file
   - Set `DEBUG=False` for production
   - Render will auto-generate `SECRET_KEY`

4. **Deploy**
   - Render will automatically build and deploy
   - Your app will be live at: `https://csit327-g1-jobconnect.onrender.com/`
---


## 🛠️ Troubleshooting

### Database Connection Issues
- Ensure your Supabase project is not paused (free tier pauses after inactivity)
- Verify `DATABASE_URL` format is correct
- Check if your IP is allowed in Supabase database settings

### Static Files Not Loading
```bash
python manage.py collectstatic --clear
python manage.py collectstatic --no-input
```

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

---

## 👥 Team Members

- **Paul Andrie Bibit** - Product Owner - paulandrie.bibit@cit.edu
- **Justine Filip Custodio** - Business Analyst - justinefilip.custodio@cit.edu
- **Van Andrae Bigtasin** - Scrum Master - vanandrae.bigtasin@cit.edu
- **Isaac Raphael Cortes** - Lead Developer - isaacraphael.cortes@cit.edu
- **Richemmae V. Bigno** - Developer - richemmae.bigno@cit.edu
- **Ken Daniel Cortes** - Developer - kendaniel.cortes@cit.edu


## 🌐 Deployed Link

🔗 [JobConnect on Render](https://csit327-g1-jobconnect.onrender.com/) 


