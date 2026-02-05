# Deep Gallary

A modern photography portfolio platform where photographers can showcase their work with AI-powered image captioning and tagging. Built with FastAPI, React, and advanced ML models.

## ✨ Features

- **Multi-photographer Platform**: Multiple photographers can create accounts and manage their portfolios
- **Project Management**: Organize images into projects with descriptions
- **Automatic Image Tagging and Captioning**: Automatic caption generation and tag prediction using BLIP, CLIP, and ViT models
- **Similarity Search**: Find visually similar images using embedding-based recommendations
- **Search Images**: Find images using keywords. 
- **Profile Customization**: Photographers can upload profile photos and manage their information
- **Responsive Design**: Clean, minimal UI optimized for showcasing photography

## 🛠️ Tech Stack

### Backend
- **Python 3.12** with FastAPI
- **MongoDB** for database
- **PyTorch** for ML model inference
- **Transformers** (Hugging Face) for AI models
- **Pydantic** for data validation
- **Argon2** for password hashing
- **Motor** for async MongoDB operations

### Frontend
- **React 19** with Vite
- **React Router** for navigation
- **Tailwind CSS** for styling
- **Axios** for API requests

### ML Models
- **BLIP** (Salesforce) - Image captioning
- **CLIP** (OpenAI) - Zero-shot classification
- **ViT** (Google) - Image classification and embeddings

## 🚀 Installation & Setup

### Clone the Repository
```bash
git clone <repository-url>
cd deep_gallary
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with required variables:
```
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=deep_gallary
```

5. Start MongoDB service
```bash
sudo systemctl start mongod
```

6. Run the backend server:
```bash
uvicorn main:app --reload
```
Backend runs on `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```
Frontend runs on `http://localhost:5173`

## 📖 Usage

1. **Sign Up**: Create a photographer account
2. **Create Project**: Organize your images into projects
3. **Upload Images**: Upload photos with AI-generated or custom captions and tags
4. **Manage Portfolio**: Edit projects, update images, customize your profile
5. **Browse**: Explore other photographers' work
6. **Search**: Find images by keywords or tags

## 📄 License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

## 🤝 Contributions
PRs and suggestions are welcome.
