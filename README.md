# 🚀 Finance-Hub

AI-powered stock investment analysis tool for Korean (KRX) and US (NYSE/NASDAQ) markets.

## 📋 Overview

Finance-Hub is an intelligent web application that helps you make data-driven investment decisions by:
- 📊 Real-time stock price tracking and portfolio management
- 🤖 AI-powered stock price predictions using LSTM/GRU models
- 💡 Smart buy/sell/hold signal generation
- 📈 Interactive charts and data visualization
- ⚖️ Multi-stock comparison analysis
- 🎯 Paper trading simulation
- ⭐ Watchlist management

## ✨ Key Features

### 🎨 Frontend Features
- **Dashboard**: Portfolio overview with AI recommendations
- **Popular Stocks**: Browse and analyze top stocks with detailed information
  - Real-time price charts with multiple timeframes (1mo, 3mo, 6mo, 1y, 5y)
  - AI prediction analysis with confidence scores
  - Multi-stock comparison (up to 5 stocks)
  - Company information and analyst targets
- **Stock Detail**: In-depth analysis with LSTM predictions and technical indicators
- **Paper Trading**: Virtual portfolio simulation with AI-driven trade suggestions
- **Watchlist**: Save and track your favorite stocks
- **Comparison Tool**: Side-by-side stock analysis
- **Prediction Map**: Visual treemap of AI predictions
- **Discovery**: Find new investment opportunities
- **Backtest**: Test AI predictions against historical data

### 🤖 AI/ML Features
- **LSTM Price Prediction**: 5-day forecast with high/low ranges
- **GRU Alternative**: Faster training alternative to LSTM
- **Buy/Sell/Hold Signals**: Automated investment recommendations
- **Confidence Scoring**: AI certainty levels for each prediction
- **Analyst Integration**: Compare AI predictions with analyst price targets
- **Model Persistence**: Saved models for quick re-predictions

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI**: shadcn/ui + Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Storage**: LocalStorage (portfolios, watchlists)

### Backend
- **Framework**: FastAPI (Python 3.13+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ML**: TensorFlow/Keras + scikit-learn
- **Models**: LSTM, GRU for time-series prediction
- **Data Sources**:
  - 🇰🇷 Korean stocks: yfinance (KRX)
  - 🇺🇸 US stocks: yfinance (NYSE/NASDAQ)
  - 📊 Stock info & quotes via yfinance
  - 📰 Analyst targets and recommendations

## 📂 Project Structure

```
finance-hub/
├── frontend/               # Next.js application
│   ├── app/               # App Router pages
│   │   ├── page.tsx       # Dashboard
│   │   ├── stocks-list/   # Popular stocks with comparison
│   │   ├── stocks/[ticker]/ # Stock details
│   │   ├── paper-trading/ # Virtual trading
│   │   ├── watchlist/     # Saved stocks
│   │   ├── compare/       # Stock comparison
│   │   ├── prediction-map/# Visual predictions
│   │   ├── discovery/     # New opportunities
│   │   └── backtest/      # Historical testing
│   ├── components/        # React components
│   │   ├── stock-chart.tsx       # Price charts
│   │   ├── prediction-explanation.tsx # AI analysis
│   │   ├── stock-treemap.tsx     # Visual map
│   │   └── watchlist-toggle.tsx  # Watchlist button
│   ├── lib/              # Utilities & API client
│   │   ├── api.ts        # Backend integration
│   │   ├── watchlist.ts  # Watchlist manager
│   │   ├── portfolio.ts  # Paper trading manager
│   │   └── stock-names.ts# Stock info database
│   └── public/           # Static assets
│
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   │   └── v1/       # Version 1 endpoints
│   │   │       ├── predictions.py  # AI predictions
│   │   │       ├── stocks.py       # Stock data
│   │   │       └── models.py       # Model management
│   │   ├── models/       # Database models (SQLAlchemy)
│   │   ├── schemas/      # Pydantic schemas
│   │   └── ml/           # ML models & training
│   │       ├── lstm_predictor.py   # LSTM model
│   │       └── data_loader.py      # Data preprocessing
│   ├── models/           # Saved ML models (.keras)
│   │   └── scalers/      # Feature scalers (.pkl)
│   └── scripts/          # Training scripts
│       ├── train_model.py         # Single stock
│       └── train_multiple.py      # Batch training
│
└── docker-compose.yml    # Local development setup
```

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.13+
- SQLite (development) or PostgreSQL (production)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train initial models (optional)
python scripts/train_multiple.py --tickers AAPL GOOGL MSFT

# Start development server
uvicorn app.main:app --reload --port 8001
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL (default: http://localhost:8001)

# Start development server
npm run dev
```

Visit `http://localhost:3000` to see the application.

## 📊 Features Status

### ✅ Completed
- ✅ Portfolio management with paper trading
- ✅ Real-time stock price fetching
- ✅ Historical data collection (up to 5 years)
- ✅ LSTM/GRU price prediction models
- ✅ Buy/Sell/Hold signal generation
- ✅ Interactive dashboard with charts
- ✅ AI recommendation cards
- ✅ Watchlist functionality
- ✅ Multi-stock comparison
- ✅ Stock detail pages with charts
- ✅ Prediction explanation with analyst targets
- ✅ Visual prediction map (treemap)
- ✅ Backtest functionality
- ✅ Popular stocks page with comparison mode

### 🔮 Future Enhancements
- [ ] Real-time WebSocket updates
- [ ] News sentiment analysis
- [ ] Alternative stock recommendations based on correlations
- [ ] Advanced backtesting framework
- [ ] Portfolio optimization strategies
- [ ] Mobile app (React Native)
- [ ] User authentication & cloud sync
- [ ] Reinforcement learning for optimal trading

## 🤖 ML Models

### 1. LSTM Price Predictor
- **Input**: 60 days of OHLCV data (open, high, low, close, volume)
- **Output**: 5-day price forecast with confidence score
- **Features**: Normalized price and volume data
- **Training**: 80/20 train-test split
- **Accuracy Target**: 70%+

### 2. GRU Predictor (Alternative)
- **Similar to LSTM** but faster training
- **Best for**: Quick retraining and experimentation
- **Trade-off**: Slightly lower accuracy for faster performance

### 3. Signal Generation
- **Logic**: Compare predicted vs current price
- **BUY**: >2% expected increase
- **SELL**: <-2% expected decrease
- **HOLD**: -2% to +2% range
- **Confidence**: Based on model prediction variance

## 📈 API Endpoints

### Stock Data
- `GET /api/v1/stocks/{ticker}/quote` - Current price
- `GET /api/v1/stocks/{ticker}/info` - Company information
- `GET /api/v1/stocks/{ticker}/history?period=3mo` - Historical data

### Predictions
- `GET /api/v1/predictions/{ticker}` - AI prediction for stock
- `GET /api/v1/predictions/summary` - All predictions overview
- `GET /api/v1/predictions/backtest/{ticker}` - Historical accuracy

### Models
- `GET /api/v1/models/trained` - List of trained models
- `POST /api/v1/models/train/{ticker}` - Train new model

## 🗄️ Data Storage

### Frontend (LocalStorage)
- **Portfolios**: Virtual trading positions and transactions
- **Watchlist**: Saved favorite stocks
- **Theme**: Dark/light mode preference

### Backend (SQLite/PostgreSQL)
- **Models**: Trained LSTM/GRU model files (.keras)
- **Scalers**: Feature normalization parameters (.pkl)
- **Cache**: Stock data cache (optional)

## 📈 Data Sources

| Market | Source | API Limit | Cost |
|--------|--------|-----------|------|
| 🇰🇷 KRX | yfinance | Unlimited | Free |
| 🇺🇸 NYSE/NASDAQ | yfinance | Unlimited | Free |
| 📊 Stock Info | yfinance | Unlimited | Free |
| 💹 Analyst Targets | yfinance | Unlimited | Free |

## 🔐 Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./finance_hub.db
# For production: postgresql://user:password@localhost:5432/finance_hub
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 🧪 Training Models

### Train a single stock
```bash
cd backend
source venv/bin/activate
python scripts/train_model.py AAPL --model-type LSTM
```

### Train multiple stocks
```bash
python scripts/train_multiple.py --tickers AAPL GOOGL MSFT TSLA
```

### Training parameters
- `--model-type`: LSTM or GRU (default: LSTM)
- `--epochs`: Number of training epochs (default: 100)
- `--sequence-length`: Days of history to use (default: 60)

## 📦 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel deploy
```

### Backend (Railway/Render/Fly.io)
```bash
cd backend
# Connect your GitHub repo to hosting platform
# Set environment variables in dashboard
# Deploy via Git push
```

### Database
- **Development**: SQLite (included)
- **Production**: PostgreSQL on Supabase/Neon/Railway

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It does not constitute financial advice. The AI predictions are based on historical data and may not reflect future performance. Always do your own research and consult with a licensed financial advisor before making investment decisions.

**Investment Warning**:
- Past performance does not guarantee future results
- AI predictions can be wrong
- Only invest what you can afford to lose
- This is a learning/simulation tool, not professional trading software

## 📞 Contact

- GitHub: [@dennis](https://github.com/dennis)
- Issues: [GitHub Issues](https://github.com/dennis/finance-hub/issues)

---

**Built with ❤️ by Dennis**
**Last Updated**: 2025-11-16
