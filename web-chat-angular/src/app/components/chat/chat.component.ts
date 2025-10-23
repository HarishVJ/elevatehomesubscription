import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { ChatService, ChatStep } from '../../services/chat.service';
import { ApiService } from '../../services/api.service';
import { ChatMessage, SearchResponse } from '../../models/product.model';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit, OnDestroy {
  messages: ChatMessage[] = [];
  currentStep: ChatStep = 'appliance_type';
  isLoading = false;
  searchResults: SearchResponse | null = null;

  // Form data
  applianceType = '';
  brand = '';
  model = '';
  brandForBrand = false;
  dollarLimit: number | null = null;

  // Options
  applianceTypes = ['range', 'dishwasher', 'refrigerator', 'microwave'];
  brands = [
    'GE', 'Whirlpool', 'LG', 'Samsung', 'Frigidaire', 'KitchenAid',
    'Kenmore', 'Bosch', 'Maytag', 'Electrolux', 'Amana', 'Other'
  ];

  private destroy$ = new Subject<void>();

  constructor(
    private chatService: ChatService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.chatService.messages$
      .pipe(takeUntil(this.destroy$))
      .subscribe(messages => {
        this.messages = messages;
        this.scrollToBottom();
      });

    this.chatService.state$
      .pipe(takeUntil(this.destroy$))
      .subscribe(state => {
        this.currentStep = state.step;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // Step 1: Appliance Type
  submitApplianceType(): void {
    if (!this.applianceType) return;

    this.chatService.addUserMessage(
      `<p><strong>Appliance Type:</strong> ${this.capitalize(this.applianceType)}</p>`
    );
    this.chatService.updateState({ 
      appliance_type: this.applianceType,
      step: 'brand'
    });
    this.chatService.addBotMessage('<p>Great! What brand are you looking for?</p>');
  }

  // Step 2: Brand
  submitBrand(): void {
    if (!this.brand) return;

    this.chatService.addUserMessage(`<p><strong>Brand:</strong> ${this.brand}</p>`);
    this.chatService.updateState({ 
      brand: this.brand,
      step: 'model'
    });
    this.chatService.addBotMessage('<p>Perfect! What\'s the model number?</p>');
  }

  // Step 3: Model
  submitModel(): void {
    if (!this.model) return;

    this.chatService.addUserMessage(`<p><strong>Model:</strong> ${this.model}</p>`);
    this.chatService.updateState({ 
      model: this.model,
      step: 'brand_for_brand'
    });
    this.chatService.addBotMessage(
      '<p>Do you need a brand-for-brand replacement (same brand only)?</p>'
    );
  }

  // Step 4: Brand-for-Brand
  submitBrandForBrand(): void {
    this.chatService.addUserMessage(
      `<p><strong>Brand-for-brand:</strong> ${this.brandForBrand ? 'Yes' : 'No'}</p>`
    );
    this.chatService.updateState({ 
      brand_for_brand: this.brandForBrand,
      step: 'dollar_limit'
    });
    this.chatService.addBotMessage('<p>What\'s your budget limit for replacements?</p>');
  }

  // Step 5: Dollar Limit
  submitDollarLimit(): void {
    if (this.dollarLimit) {
      this.chatService.addUserMessage(`<p><strong>Budget limit:</strong> $${this.dollarLimit}</p>`);
    } else {
      this.chatService.addUserMessage('<p><strong>Budget limit:</strong> No limit</p>');
    }
    
    this.chatService.updateState({ 
      dollar_limit: this.dollarLimit,
      step: 'results'
    });
    
    this.searchProducts();
  }

  // Search Products
  searchProducts(): void {
    this.chatService.addBotMessage(
      '<p>🔍 Searching for your product and finding replacements...</p>' +
      '<p>This may take a few seconds.</p>'
    );
    this.isLoading = true;

    const state = this.chatService.getState();
    const request = {
      brand: state.brand,
      model: state.model,
      appliance_type: state.appliance_type,
      brand_for_brand: state.brand_for_brand,
      dollar_limit: state.dollar_limit
    };

    this.apiService.completeSearch(request)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          if (response.success) {
            this.searchResults = response;
            this.displayResults(response);
          } else {
            this.chatService.addBotMessage(
              `<p>❌ <strong>Error:</strong> ${response.error}</p>` +
              '<p>Please try again or adjust your search criteria.</p>'
            );
          }
        },
        error: (error) => {
          this.isLoading = false;
          this.chatService.addBotMessage(
            '<p>❌ <strong>Connection Error:</strong> Could not connect to the server.</p>' +
            '<p>Make sure the API server is running on port 5000.</p>'
          );
        }
      });
  }

  // Display Results
  displayResults(data: SearchResponse): void {
    const original = data.original_product;
    
    // Original product
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
            <span class="info-value">${original.source || 'N/A'}</span>
          </div>
        </div>
        <div class="feature-list">
          ${original.features.slice(0, 8).map(f => `<span class="feature-tag">${f}</span>`).join('')}
        </div>
      </div>
    `;
    this.chatService.addBotMessage(originalHtml);

    // Replacements
    if (data.replacements && data.replacements.length > 0) {
      const replacementsHtml = `
        <p>🎯 <strong>Found ${data.replacements.length} Replacement Options</strong></p>
        <p style="font-size: 14px; color: #6c757d;">Searched ${data.search_summary.retailers_searched} retailers</p>
      `;
      this.chatService.addBotMessage(replacementsHtml);

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
        this.chatService.addBotMessage(replacementHtml);
      });
    } else {
      this.chatService.addBotMessage(
        '<p>😕 No replacement products found matching your criteria.</p>'
      );
    }
  }

  // Restart
  restart(): void {
    this.applianceType = '';
    this.brand = '';
    this.model = '';
    this.brandForBrand = false;
    this.dollarLimit = null;
    this.searchResults = null;
    this.chatService.reset();
  }

  // Go back
  goBack(step: ChatStep): void {
    this.chatService.updateState({ step });
  }

  // Utility
  capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  scrollToBottom(): void {
    setTimeout(() => {
      const container = document.getElementById('chatContainer');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  }
}
