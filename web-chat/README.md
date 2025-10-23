# Appliance Research Chat Interface

Simple, responsive web chat interface for the Product Research Agent.

## Quick Start

### 1. Install Python Dependencies
```bash
cd ..
pip install -r requirements.txt
```

### 2. Start Backend API Server
```bash
python3 api_server.py
```

The API will start on http://localhost:5000

### 3. Open Web Interface
Simply open `index.html` in your browser, or use a local server:

```bash
# Option 1: Python simple server
python3 -m http.server 8000

# Option 2: Open directly
open index.html
```

Then visit: http://localhost:8000

## Features

✅ **Interactive Chat Interface** - Conversational UI for easy interaction  
✅ **Step-by-Step Collection** - Guided input for all required information  
✅ **Real-Time Search** - Instant product research and replacement finding  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Modern UI** - Clean, gradient design with smooth animations  
✅ **No Build Required** - Pure HTML/CSS/JS, no compilation needed

## User Flow

1. **Select Appliance Type** - Range, Dishwasher, Refrigerator, Microwave
2. **Choose Brand** - Select from list or enter custom
3. **Enter Model Number** - Product model identifier
4. **Brand-for-Brand** - Same brand only or all brands
5. **Budget Limit** - Optional price limit
6. **View Results** - Original product specs + top 10 replacements

## API Endpoints Used

- `POST /api/complete` - Complete workflow (research + replacements)

## Troubleshooting

### "Connection Error"
- Make sure API server is running: `python3 api_server.py`
- Check API is accessible: http://localhost:5000/api/health

### CORS Issues
- API server has CORS enabled by default
- If issues persist, check Flask-CORS is installed

### No Results Found
- Verify Google API keys are set
- Check internet connection
- Try different model number format

## Files

- `index.html` - Main HTML structure
- `styles.css` - Responsive CSS styling
- `app.js` - Application logic and API integration
- `README.md` - This file

## Customization

### Change API URL
Edit `app.js`:
```javascript
const API_BASE_URL = 'http://your-server:5000/api';
```

### Add More Brands
Edit `app.js`:
```javascript
const brands = ['GE', 'Whirlpool', 'YourBrand', ...];
```

### Modify Styling
Edit `styles.css` to customize colors, fonts, layout, etc.
