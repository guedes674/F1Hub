# F1Hub 🏎️

A central hub for Formula 1 enthusiasts, offering driver statistics, news, ratings, and driver comparisons powered by AI technology.

## 📊 Features

- **Driver Statistics**: Detailed and up-to-date data on each driver's performance
- **News Feed**: Latest news from the F1 world
- **AI-Powered Rating System**: Sophisticated evaluation of each driver using IA to analyze critical performance metrics, considering factors beyond traditional statistics.
- **Driver Comparison**: Tool for comparative analysis between drivers with detailed attribute breakdown
- **F1 Assistant**: Interactive chatbot powered by IA to answer all your F1 questions

## 🔮 In Development

- **Race Simulator**: Realistic simulations based on historical data
- **GP Predictions**: AI-driven forecasts for upcoming Grand Prix events using LLM to analyze historical statistics and current form. The user will be allowed to select any upcoming race to receive AI-generated predictions based on historical data, current form, and track-specific variables.

## 🛠️ Key Technologies

- **Frontend**: Next.js and Tailwind CSS for a responsive and modern UI
- **Backend**: Python for sophisticated data analysis and processing

## 📺 Preview

<div align="center">
  <h3>Dashboard</h3>
  <img src="media/f1hubhomepage.webp" alt="F1Hub Dashboard" width="800"/>
  
  <h3>Driver Statistics</h3>
  <img src="media/f1hubstats.png" alt="Driver Statistics" width="800"/>
  
  <h3>News Feed</h3>
  <img src="media/f1hubnews.webp" alt="F1Hub News" width="800"/>
  
  <h3>Driver Comparison</h3>
  <img src="media/f1hubcomp.webp" alt="Driver Comparison Tool" width="800"/>
</div>

## 🚀 Installation

### Frontend 
```bash
# Clone the repository
git clone https://github.com/Tiago5Carneiro/hackaton25

# Navigate to the directory
cd frontend

# Install dependencies
npm install

# Start the application
npm start
```

### Backend 

```bash
cd Backend/proxy

python3 proxy.py
```

### Database Injection

```bash
# Go to Backend 
cd Backend

# Open mysql
mysql

# Build squema
source squema.sql

# Run Database injection
python3 FastF1_Api.py
```

