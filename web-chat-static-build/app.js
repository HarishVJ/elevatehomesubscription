// API Configuration
const API_BASE_URL = 'https://sspripaelevateapp.proudbush-0db0d62f.eastus.azurecontainerapps.io/api';

// Application State
const state = {
    step: 'appliance_type',
    data: {
        appliance_type: '',
        brand: '',
        model: '',
        brand_for_brand: false,
        dollar_limit: null
    },
    originalProduct: null
};

// Appliance types
const applianceTypes = ['range', 'dishwasher', 'refrigerator', 'microwave'];

// Popular brands
const brands = [
    'GE', 'Whirlpool', 'LG', 'Samsung', 'Frigidaire', 'KitchenAid',
    'Kenmore', 'Bosch', 'Maytag', 'Electrolux', 'Amana', 'Other'
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showApplianceTypeInput();
});

// Add message to chat
function addMessage(content, isUser = false) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show loading indicator
function showLoading(show = true) {
    const loading = document.getElementById('loadingIndicator');
    const inputContainer = document.getElementById('inputContainer');
    
    if (show) {
        loading.style.display = 'block';
        inputContainer.style.display = 'none';
    } else {
        loading.style.display = 'none';
        inputContainer.style.display = 'block';
    }
}

// Step 1: Appliance Type
function showApplianceTypeInput() {
    const inputContainer = document.getElementById('inputContainer');
    inputContainer.innerHTML = `
        <div class="input-group">
            <label>What type of appliance are you looking for?</label>
            <select id="applianceType" class="form-control">
                <option value="">Select appliance type...</option>
                ${applianceTypes.map(type => `
                    <option value="${type}">${type.charAt(0).toUpperCase() + type.slice(1)}</option>
                `).join('')}
            </select>
        </div>
        <div class="button-group">
            <button class="btn-primary" onclick="submitApplianceType()" id="submitBtn" disabled>
                Next →
            </button>
        </div>
    `;
    
    // Enable button when selection is made
    document.getElementById('applianceType').addEventListener('change', (e) => {
        document.getElementById('submitBtn').disabled = !e.target.value;
    });
}

function submitApplianceType() {
    const select = document.getElementById('applianceType');
    const value = select.value;
    
    if (!value) return;
    
    state.data.appliance_type = value;
    addMessage(`<p><strong>Appliance Type:</strong> ${value.charAt(0).toUpperCase() + value.slice(1)}</p>`, true);
    
    addMessage('<p>Great! What brand are you looking for?</p>');
    showBrandInput();
}

// Step 2: Brand
function showBrandInput() {
    const inputContainer = document.getElementById('inputContainer');
    inputContainer.innerHTML = `
        <div class="input-group">
            <label>Select or enter the brand:</label>
            <select id="brandSelect" class="form-control">
                <option value="">Select a brand...</option>
                ${brands.map(brand => `
                    <option value="${brand}">${brand}</option>
                `).join('')}
            </select>
            <input type="text" id="brandInput" class="form-control" placeholder="Or type brand name..." style="margin-top: 10px;">
        </div>
        <div class="button-group">
            <button class="btn-secondary" onclick="goBack('appliance_type')">← Back</button>
            <button class="btn-primary" onclick="submitBrand()" id="submitBtn" disabled>
                Next →
            </button>
        </div>
    `;
    
    // Enable button when selection or input is made
    const updateButton = () => {
        const select = document.getElementById('brandSelect').value;
        const input = document.getElementById('brandInput').value;
        document.getElementById('submitBtn').disabled = !select && !input;
    };
    
    document.getElementById('brandSelect').addEventListener('change', updateButton);
    document.getElementById('brandInput').addEventListener('input', updateButton);
}

function submitBrand() {
    const select = document.getElementById('brandSelect').value;
    const input = document.getElementById('brandInput').value;
    const value = select || input;
    
    if (!value) return;
    
    state.data.brand = value;
    addMessage(`<p><strong>Brand:</strong> ${value}</p>`, true);
    
    addMessage('<p>Perfect! What\'s the model number?</p>');
    showModelInput();
}

// Step 3: Model
function showModelInput() {
    const inputContainer = document.getElementById('inputContainer');
    inputContainer.innerHTML = `
        <div class="input-group">
            <label>Enter the model number:</label>
            <input type="text" id="modelInput" class="form-control" placeholder="e.g., JGB735, ABC123..." autofocus>
            <small style="color: #6c757d; margin-top: 5px;">Enter the model number as shown on the appliance</small>
        </div>
        <div class="button-group">
            <button class="btn-secondary" onclick="goBack('brand')">← Back</button>
            <button class="btn-primary" onclick="submitModel()" id="submitBtn" disabled>
                Next →
            </button>
        </div>
    `;
    
    // Enable button when input is made
    document.getElementById('modelInput').addEventListener('input', (e) => {
        document.getElementById('submitBtn').disabled = !e.target.value.trim();
    });
    
    // Submit on Enter
    document.getElementById('modelInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.target.value.trim()) {
            submitModel();
        }
    });
}

function submitModel() {
    const value = document.getElementById('modelInput').value.trim();
    
    if (!value) return;
    
    state.data.model = value;
    addMessage(`<p><strong>Model:</strong> ${value}</p>`, true);
    
    addMessage('<p>Do you need a brand-for-brand replacement (same brand only)?</p>');
    showBrandForBrandInput();
}

// Step 4: Brand-for-Brand
function showBrandForBrandInput() {
    const inputContainer = document.getElementById('inputContainer');
    inputContainer.innerHTML = `
        <div class="input-group">
            <label>Brand-for-brand coverage?</label>
            <select id="brandForBrand" class="form-control">
                <option value="false">No - Show all brands</option>
                <option value="true">Yes - Same brand only (${state.data.brand})</option>
            </select>
        </div>
        <div class="button-group">
            <button class="btn-secondary" onclick="goBack('model')">← Back</button>
            <button class="btn-primary" onclick="submitBrandForBrand()">
                Next →
            </button>
        </div>
    `;
}

function submitBrandForBrand() {
    const value = document.getElementById('brandForBrand').value === 'true';
    
    state.data.brand_for_brand = value;
    addMessage(`<p><strong>Brand-for-brand:</strong> ${value ? 'Yes' : 'No'}</p>`, true);
    
    addMessage('<p>What\'s your budget limit for replacements?</p>');
    showDollarLimitInput();
}

// Step 5: Dollar Limit
function showDollarLimitInput() {
    const inputContainer = document.getElementById('inputContainer');
    inputContainer.innerHTML = `
        <div class="input-group">
            <label>Maximum price (optional):</label>
            <input type="number" id="dollarLimit" class="form-control" placeholder="e.g., 2000" min="0" step="100">
            <small style="color: #6c757d; margin-top: 5px;">Leave empty for no limit</small>
        </div>
        <div class="button-group">
            <button class="btn-secondary" onclick="goBack('brand_for_brand')">← Back</button>
            <button class="btn-primary" onclick="submitDollarLimit()">
                🔍 Search Now
            </button>
        </div>
    `;
    
    // Submit on Enter
    document.getElementById('dollarLimit').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitDollarLimit();
        }
    });
}

function submitDollarLimit() {
    const value = document.getElementById('dollarLimit').value;
    
    if (value) {
        state.data.dollar_limit = parseFloat(value);
        addMessage(`<p><strong>Budget limit:</strong> $${value}</p>`, true);
    } else {
        addMessage(`<p><strong>Budget limit:</strong> No limit</p>`, true);
    }
    
    // Start search
    searchProducts();
}

// Search Products
async function searchProducts() {
    console.log('=== SEARCH STARTED ===');
    console.log('API URL:', API_BASE_URL);
    
    addMessage('<p>🔍 Searching for your product and finding replacements...</p><p>This may take a few seconds.</p>');
    showLoading(true);
    
    const requestData = {
        brand: state.data.brand,
        model: state.data.model,
        appliance_type: state.data.appliance_type,
        brand_for_brand: state.data.brand_for_brand,
        dollar_limit: state.data.dollar_limit
    };
    
    console.log('Request data:', requestData);
    
    try {
        console.log('Sending request to:', `${API_BASE_URL}/complete`);
        const response = await fetch(`${API_BASE_URL}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                brand: state.data.brand,
                model: state.data.model,
                appliance_type: state.data.appliance_type,
                brand_for_brand: state.data.brand_for_brand,
                dollar_limit: state.data.dollar_limit
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        showLoading(false);
        
        if (data.success) {
            console.log('Success! Displaying results...');
            displayResults(data);
        } else {
            console.error('API returned error:', data.error);
            addMessage(`<p>❌ <strong>Error:</strong> ${data.error}</p><p>Please try again or adjust your search criteria.</p>`);
            showRestartButton();
        }
        
    } catch (error) {
        console.error('=== FETCH ERROR ===');
        console.error('Error type:', error.name);
        console.error('Error message:', error.message);
        console.error('Full error:', error);
        
        showLoading(false);
        addMessage(`<p>❌ <strong>Connection Error:</strong> Could not connect to the server.</p><p>Make sure the API server is running on port 5001.</p><p>Error: ${error.message}</p>`);
        showRestartButton();
    }
}

// Display Results
function displayResults(data) {
    // Show original product
    const original = data.original_product;
    const originalHtml = `
        <p>✅ <strong>Original Product Found!</strong></p>
        <div class="product-card">
            <h3>${original.brand} ${original.model}</h3>
            <div class="product-info">
                <div class="info-item">
                    <span class="info-label">Type</span>
                    <span class="info-value">${original.type}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Size</span>
                    <span class="info-value">${original.size || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Fuel</span>
                    <span class="info-value">${original.fuel || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Source</span>
                    <span class="info-value">${original.source}</span>
                </div>
            </div>
            <div class="feature-list">
                ${original.features.slice(0, 8).map(f => `<span class="feature-tag">${f}</span>`).join('')}
            </div>
        </div>
    `;
    addMessage(originalHtml);
    
    // Show replacements
    if (data.replacements && data.replacements.length > 0) {
        const replacementsHtml = `
            <p>🎯 <strong>Found ${data.replacements.length} Replacement Options</strong></p>
            <p style="font-size: 14px; color: #6c757d;">Searched ${data.search_summary.retailers_searched} retailers</p>
        `;
        addMessage(replacementsHtml);
        
        data.replacements.forEach(r => {
            const replacementHtml = `
                <div class="replacement-card">
                    <div class="replacement-header">
                        <div class="replacement-rank">${r.rank}</div>
                        <div class="replacement-title">
                            <h4>${r.product_name}</h4>
                            <div>
                                <span class="badge badge-info">${r.retailer}</span>
                                ${r.availability === 'in stock' ? '<span class="badge badge-success">In Stock</span>' : ''}
                                ${r.availability === 'limited stock' ? '<span class="badge badge-warning">Limited Stock</span>' : ''}
                            </div>
                        </div>
                        <div class="replacement-score">Score: ${r.match_score}</div>
                    </div>
                    <div class="replacement-details">
                        <div class="info-item">
                            <span class="info-label">Brand</span>
                            <span class="info-value">${r.brand || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Price</span>
                            <span class="info-value">${r.price ? '$' + r.price.toFixed(2) : 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Size</span>
                            <span class="info-value">${r.size || 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Fuel</span>
                            <span class="info-value">${r.fuel || 'N/A'}</span>
                        </div>
                    </div>
                    ${r.features && r.features.length > 0 ? `
                        <div class="feature-list">
                            ${r.features.slice(0, 5).map(f => `<span class="feature-tag">${f}</span>`).join('')}
                        </div>
                    ` : ''}
                    <a href="${r.url}" target="_blank" class="replacement-link">View Product →</a>
                </div>
            `;
            addMessage(replacementHtml);
        });
    } else {
        addMessage('<p>😕 No replacement products found matching your criteria.</p>');
    }
    
    showRestartButton();
}

// Show restart button
function showRestartButton() {
    const inputContainer = document.getElementById('inputContainer');
    inputContainer.innerHTML = `
        <div class="button-group">
            <button class="btn-primary" onclick="restart()">
                🔄 Start New Search
            </button>
        </div>
    `;
}

// Restart
function restart() {
    state.step = 'appliance_type';
    state.data = {
        appliance_type: '',
        brand: '',
        model: '',
        brand_for_brand: false,
        dollar_limit: null
    };
    
    document.getElementById('chatContainer').innerHTML = `
        <div class="message bot-message">
            <div class="message-content">
                <p>👋 Let's start a new search!</p>
                <p>What type of appliance are you looking for?</p>
            </div>
        </div>
    `;
    
    showApplianceTypeInput();
}

// Go back to previous step
function goBack(step) {
    state.step = step;
    
    switch(step) {
        case 'appliance_type':
            showApplianceTypeInput();
            break;
        case 'brand':
            showBrandInput();
            break;
        case 'model':
            showModelInput();
            break;
        case 'brand_for_brand':
            showBrandForBrandInput();
            break;
    }
}
