# Appliance Research Chat - Angular TypeScript

Angular TypeScript application for the Appliance Research Assistant.

## Features

✅ **TypeScript** - Full type safety
✅ **Angular 17** - Latest Angular framework
✅ **Reactive Programming** - RxJS observables
✅ **Service Architecture** - Clean separation of concerns
✅ **Type-Safe Models** - Strongly typed interfaces
✅ **Responsive Design** - Mobile-friendly UI

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+ (for backend API)
- Angular CLI (will be installed with npm install)

## Quick Start

### 1. Install Dependencies

```bash
cd web-chat-angular
npm install
```

### 2. Start Backend API

In a separate terminal:
```bash
cd ..
python3 api_server.py
```

The API will start on http://localhost:5000

### 3. Start Angular App

```bash
npm start
```

The app will start on http://localhost:4200

Open browser: **http://localhost:4200**

## Project Structure

```
web-chat-angular/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   └── chat/
│   │   │       ├── chat.component.ts       # Main chat component
│   │   │       ├── chat.component.html     # Template
│   │   │       └── chat.component.css      # Styles
│   │   ├── models/
│   │   │   └── product.model.ts            # TypeScript interfaces
│   │   ├── services/
│   │   │   ├── api.service.ts              # HTTP API service
│   │   │   └── chat.service.ts             # Chat state management
│   │   ├── app.component.ts                # Root component
│   │   └── app.module.ts                   # App module
│   ├── environments/
│   │   ├── environment.ts                  # Dev environment
│   │   └── environment.prod.ts             # Prod environment
│   ├── index.html                          # Main HTML
│   ├── main.ts                             # Bootstrap
│   └── styles.css                          # Global styles
├── angular.json                            # Angular config
├── package.json                            # Dependencies
├── tsconfig.json                           # TypeScript config
└── README.md                               # This file
```

## Architecture

### Services

#### **ApiService** (`api.service.ts`)
- HTTP communication with backend
- Type-safe API calls
- Error handling

#### **ChatService** (`chat.service.ts`)
- Chat state management
- Message handling
- Observable streams

### Models

#### **product.model.ts**
- `ProductSpecification` - Product specs
- `OriginalProduct` - Original product data
- `ReplacementProduct` - Replacement product
- `SearchRequest` - API request
- `SearchResponse` - API response
- `ChatMessage` - Chat message

### Components

#### **ChatComponent** (`chat.component.ts`)
- Main chat interface
- Step-by-step flow
- User input handling
- Results display

## Development

### Run Development Server
```bash
npm start
```

### Build for Production
```bash
npm run build
```

Output will be in `dist/appliance-research-chat/`

### Watch Mode
```bash
npm run watch
```

## Configuration

### API URL

Edit `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api'
};
```

For production, edit `src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-api.com/api'
};
```

## Type Safety

All data structures are strongly typed:

```typescript
// Example: Search request
const request: SearchRequest = {
  brand: 'GE',
  model: 'JGB735',
  appliance_type: 'range',
  brand_for_brand: false,
  dollar_limit: 2000
};

// TypeScript will catch errors at compile time
this.apiService.completeSearch(request).subscribe({
  next: (response: SearchResponse) => {
    // response is fully typed
    console.log(response.original_product.brand);
  }
});
```

## Reactive Programming

Uses RxJS observables for state management:

```typescript
// Subscribe to messages
this.chatService.messages$.subscribe(messages => {
  this.messages = messages;
});

// Subscribe to state changes
this.chatService.state$.subscribe(state => {
  this.currentStep = state.step;
});
```

## User Flow

1. **Appliance Type** → Select from dropdown
2. **Brand** → Select or enter custom
3. **Model** → Enter model number
4. **Brand-for-Brand** → Yes/No
5. **Budget Limit** → Optional price limit
6. **Results** → Display original + replacements

## API Integration

### Complete Search
```typescript
this.apiService.completeSearch(request).subscribe({
  next: (response) => {
    if (response.success) {
      this.displayResults(response);
    }
  },
  error: (error) => {
    console.error('API Error:', error);
  }
});
```

## Styling

- Global styles: `src/styles.css`
- Component styles: `chat.component.css`
- Responsive design with CSS Grid and Flexbox
- Purple gradient theme

## Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
npm run e2e
```

## Production Deployment

### Build
```bash
npm run build -- --configuration production
```

### Deploy
1. Upload `dist/appliance-research-chat/` to web server
2. Configure API URL in environment
3. Set up HTTPS
4. Configure CORS on backend

### Serve with nginx
```nginx
server {
  listen 80;
  server_name your-domain.com;
  root /path/to/dist/appliance-research-chat;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

## Troubleshooting

### "Cannot find module"
```bash
npm install
```

### Port 4200 already in use
```bash
ng serve --port 4300
```

### API connection error
- Check API server is running on port 5000
- Verify CORS is enabled on backend
- Check `environment.ts` has correct API URL

### Build errors
```bash
rm -rf node_modules package-lock.json
npm install
```

## Scripts

- `npm start` - Start dev server
- `npm run build` - Build for production
- `npm run watch` - Build and watch for changes
- `npm test` - Run unit tests

## Dependencies

### Core
- `@angular/core` - Angular framework
- `@angular/common` - Common Angular modules
- `@angular/forms` - Form handling
- `rxjs` - Reactive programming

### Dev
- `@angular/cli` - Angular CLI
- `typescript` - TypeScript compiler
- `@angular-devkit/build-angular` - Build tools

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Lazy loading ready
- AOT compilation
- Tree shaking enabled
- Optimized bundle size

## Next Steps

1. ✅ Install dependencies
2. ✅ Start backend API
3. ✅ Start Angular app
4. 🔄 Customize styling
5. 🔄 Add more features
6. 🔄 Deploy to production

---

**Version**: 1.0.0
**Framework**: Angular 17
**Language**: TypeScript 5.2
**Status**: Production Ready ✅
