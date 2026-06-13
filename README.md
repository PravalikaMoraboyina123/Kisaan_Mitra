# Kisaan Mitra 🌾

**AI-Powered Multilingual Farmer Assistant**

Kisaan Mitra is an intelligent farming companion that provides personalized advice for crops, weather, market prices, pest diagnosis, and government schemes - all in your preferred language (English, Hindi, or Telugu).

## 🌟 Features

### 🌱 Crop Advisor
Get expert advice on crop selection, sowing, fertilizers, and harvest timing based on your location and crop type.

### 🌤️ Weather Forecast
7-day weather forecast with AI-powered farming recommendations tailored to your crops.

### 🏪 Mandi Prices
Real-time market prices and AI advice on when and where to sell your produce for maximum profit.

### 🔍 Pest Diagnosis
Upload images of affected crops for AI-powered disease and pest identification with treatment recommendations.

### 📋 Government Schemes
Discover relevant government schemes and subsidies based on your profile (state, crop, land size).

## 🌍 Multilingual Support

The app is available in three languages:
- **English** - For widespread accessibility
- **हिंदी (Hindi)** - For Hindi-speaking farmers
- **తెలుగు (Telugu)** - For Telugu-speaking farmers

## 🤖 AI Integration

### Local AI (Ollama)
- Free, offline-capable AI inference
- Supports models: Llama3, Mistral, Gemma2
- No API keys required

### Cloud AI (BYOK - Bring Your Own Keys)
- Support for multiple cloud providers:
  - OpenAI GPT-4o
  - Anthropic Claude Sonnet
  - Google Gemini 1.5 Pro
- Users provide their own API keys

## 📁 Project Structure

```
Kisaan_Mitra/
├── backend/                    # Python backend
│   ├── config.py              # Configuration and constants
│   ├── utils/
│   │   └── llm_client.py      # Unified LLM client (Ollama + Cloud)
│   ├── modules/
│   │   ├── crop_advisor.py    # Crop recommendation engine
│   │   ├── weather.py         # Weather forecast and advice
│   │   ├── mandi_prices.py    # Market price analysis
│   │   ├── pest_diagnosis.py  # Image-based pest diagnosis
│   │   └── scheme_finder.py   # Government scheme matching
│   └── requirements.txt       # Backend dependencies
├── frontend/                   # Streamlit frontend
│   ├── app.py                 # Main application entry point
│   ├── i18n_utils.py          # Internationalization utilities
│   ├── i18n/                  # Translation files
│   │   ├── en.json           # English translations
│   │   ├── hi.json           # Hindi translations
│   │   └── te.json           # Telugu translations
│   └── pages/                 # Feature pages
│       ├── crop_advisor_page.py
│       ├── weather_page.py
│       ├── mandi_prices_page.py
│       ├── pest_diagnosis_page.py
│       └── scheme_finder_page.py
├── requirements.txt           # Root-level dependencies
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Ollama for local AI inference

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kisaan_mitra.git
   cd kisaan_mitra
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama (Optional - for local AI)**
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull a model (e.g., llama3)
   ollama pull llama3
   ```

### Running the Application

```bash
cd frontend
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## 🎯 How to Use

### 1. Select Your Language
Use the language dropdown in the sidebar to switch between English, Hindi, or Telugu.

### 2. Choose AI Provider
- **Local (Ollama)**: Select for free, offline AI (requires Ollama running)
- **Cloud (BYOK)**: Select to use cloud AI with your own API key

### 3. Explore Features

#### Crop Advisor
1. Select your crop from the dropdown
2. Enter your district and state
3. Choose sowing date
4. Click "Get Advice" for personalized recommendations

#### Weather Forecast
1. Enter your district
2. Select your crop
3. Get 7-day forecast with AI-powered farming advice

#### Mandi Prices
1. Select your commodity
2. Choose your state
3. View current prices and AI selling recommendations

#### Pest Diagnosis
1. Upload a clear photo of the affected plant part
2. Select the crop type
3. Get AI-powered diagnosis and treatment advice

#### Government Schemes
1. Select your state
2. Choose your main crop
3. Enter your land size
4. Discover relevant schemes and how to apply

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file in the root directory:

```env
# OpenWeatherMap API key (for real weather data)
OPENWEATHER_API_KEY=your_api_key_here

# data.gov.in API key (for real mandi prices)
DATAGOV_API_KEY=your_api_key_here

# OpenAI API key (if using GPT)
OPENAI_API_KEY=your_api_key_here

# Anthropic API key (if using Claude)
ANTHROPIC_API_KEY=your_api_key_here

# Google AI API key (if using Gemini)
GOOGLE_API_KEY=your_api_key_here
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web app framework)
- **Backend**: Python with modular architecture
- **AI/ML**: 
  - LiteLLM for unified LLM interface
  - Ollama for local inference
  - Support for OpenAI, Anthropic, Google APIs
- **Internationalization**: JSON-based translation system
- **Data Processing**: Pandas for data manipulation

## 📝 API Integrations

### External APIs (Optional)
- **OpenWeatherMap**: For real-time weather forecasts
- **data.gov.in**: For mandi price data
- **Cloud AI Providers**: OpenAI, Anthropic, Google

### Local AI
- **Ollama**: For offline, free AI inference

**🌾 Kisaan Mitra - Empowering Farmers with AI 🌾**

*Built with ❤️ for Indian Farmers*
