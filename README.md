

```txt
edmonton-fire-optimizer/
├── .gitignore
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── app.py                  # Main Streamlit Dashboard
├── src/
│   ├── __init__.py
│   ├── data_loader.py      # OSMnx & Real Data Ingestion
│   ├── optimizer.py        # MCLP (PuLP) + Monte Carlo Stress Test
│   ├── geospatial.py       # Travel Time Matrix & Isochrones
│   └── visualization.py    # Folium Map Generation
└── tests/
    ├── __init__.py
    ├── conftest.py         # Shared Fixtures (Mock Graphs)
    ├── test_data_loader.py
    └── test_optimizer.py
```

## Deployment Instructions (Oracle Cloud Free Tier)

### Step A: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Darkhorse-ready Fire Optimizer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/edmonton-fire-optimizer.git
git push -u origin main

```

### Step B: Oracle Cloud Setup (SSH into your VM)

```bash
# 1. Update & Install Docker
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# LOG OUT AND LOG BACK IN HERE

# 2. Clone Repo
git clone https://github.com/YOUR_USERNAME/edmonton-fire-optimizer.git
cd edmonton-fire-optimizer

# 3. Run Tests (CI Check)
docker compose run --rm fire-optimizer pytest

# 4. Deploy
docker compose up -d --build
```

### Step C: Open Firewall

```markdown
In Oracle Console: VCN -> Security Lists -> Add Ingress Rule:
- Source: 0.0.0.0/0
- Port: 8501
Access: `http://<YOUR_ORACLE_IP>:8501`
```