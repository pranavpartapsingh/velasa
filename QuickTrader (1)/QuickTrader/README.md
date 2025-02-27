# Velasa Trading Platform - Installation Guide

## Setup Instructions for Visual Studio Code

### Prerequisites
1. Download and install:
   - [Visual Studio Code](https://code.visualstudio.com/download)
   - [Python 3.11](https://www.python.org/downloads/) (Make sure to check "Add to PATH" during installation)
   - [Git](https://git-scm.com/downloads) (Optional)

### Step 1: Open the Project
1. Extract the downloaded ZIP file to a folder
2. Open Visual Studio Code
3. Go to File -> Open Folder
4. Select the extracted project folder

### Step 2: Install VS Code Extensions
1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search and install:
   - "Python" (by Microsoft)
   - "Streamlit" (Optional, for syntax highlighting)

### Step 3: Install Dependencies
1. Open VS Code Terminal (Ctrl+`)
2. Run these commands:
   ```bash
   pip install streamlit==1.42.2
   pip install google-auth==2.38.0
   pip install google-auth-oauthlib==1.2.1
   pip install nltk==3.9.1
   pip install plotly==6.0.0
   pip install twilio==9.4.6
   pip install yfinance==0.2.54
   ```

### Step 4: Configure Environment Variables
1. Create a file named `.env` in the project root
2. Add these lines (replace with your actual Twilio credentials):
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone
   ```

### Step 5: Run the App
1. In VS Code Terminal, run:
   ```bash
   python run_app.py
   ```
2. Open your browser and go to: `http://localhost:5000`

### Common Issues & Solutions

1. **Port 5000 is in use**
   - Close other applications using port 5000
   - Or change the port in `run_app.py`

2. **Module not found errors**
   - Verify Python 3.11 is installed: `python --version`
   - Reinstall dependencies: Run Step 3 again

3. **Environment variables not working**
   - Make sure `.env` file is in the correct location
   - Restart VS Code after creating `.env`

4. **App not loading**
   - Check console for error messages
   - Verify all files are in the correct structure:
     ```
     project/
     ├── components/         # UI Components
     ├── utils/             # Helper functions
     ├── styles/            # CSS styles
     ├── assets/           # Static assets
     ├── .env             # Environment variables
     ├── main.py          # Main application
     └── run_app.py       # Launcher script
     ```

### Getting Help
If you encounter any issues:
1. Check the error message in the terminal
2. Verify all setup steps are completed
3. Restart VS Code and try again

For additional support, contact our team.


## Features
- Advanced trading capabilities
- Real-time market data analysis
- Multi-factor authentication
- Interactive charting with Plotly
- Social trading features
- Institutional trading support

## Project Structure
```
├── components/         # UI Components
├── utils/             # Helper functions
├── styles/            # CSS styles
├── assets/           # Static assets
└── main.py           # Main application file