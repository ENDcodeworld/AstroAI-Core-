# AstroAI-Core Frontend

🌌 **Astronomy × AI Research Platform** - A modern web application for exploring exoplanets and classifying astronomical images using artificial intelligence.

## Features

### 🔭 Exoplanet Browser
- Browse discovered exoplanets with detailed information
- Advanced filtering and search capabilities
- Sort by distance, mass, discovery year, and more
- Interactive 3D orbital visualization
- Habitable zone indicators

### 🖼️ AI Image Classifier
- Upload astronomical images for classification
- Support for batch uploads (up to 10 images)
- Real-time classification with confidence scores
- Classification history with detailed results
- Drag-and-drop interface

### 📊 Data Visualization
- Interactive mass vs radius scatter plots
- Size comparison bubble charts
- Statistical analysis dashboard
- Distribution by constellation and discovery method
- Multiple view modes (charts, grid, statistics)

### 🎨 Modern UI/UX
- Dark theme optimized for astronomy
- Responsive design (mobile, tablet, desktop)
- Smooth animations and transitions
- Material-UI component library
- Accessible and intuitive navigation

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI (MUI)** - Component library
- **React Router v6** - Navigation
- **Zustand** - State management
- **Three.js + React Three Fiber** - 3D visualizations
- **Chart.js + react-chartjs-2** - Data visualization
- **Vite** - Build tool and dev server
- **date-fns** - Date formatting

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd projects/AstroAI-Core/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── PlanetCard.tsx   # Exoplanet card component
│   │   ├── ImageUpload.tsx  # Image upload with drag-drop
│   │   ├── OrbitViewer.tsx  # 3D orbital visualization
│   │   └── SizeChart.tsx    # Data visualization charts
│   ├── pages/               # Page components
│   │   ├── Exoplanets.tsx   # Exoplanet browser page
│   │   ├── ExoplanetDetail.tsx  # Planet detail page
│   │   ├── ImageClassifier.tsx  # AI classifier page
│   │   └── Visualization.tsx    # Data viz page
│   ├── store/               # Zustand state stores
│   │   ├── exoplanetStore.ts
│   │   ├── classificationStore.ts
│   │   └── userStore.ts
│   ├── types/               # TypeScript type definitions
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
└── README.md                # This file
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The current implementation uses mock data for demonstration. To connect to a real backend:

1. Update the store files to make actual API calls
2. Replace mock data with axios/fetch requests
3. Configure API base URL in environment variables
4. Handle authentication tokens

Example for exoplanet store:
```typescript
// In exoplanetStore.ts
const response = await axios.get('/api/exoplanets', {
  headers: { Authorization: `Bearer ${token}` }
});
setPlanets(response.data);
```

## Customization

### Theme

Modify the theme in `App.tsx`:
```typescript
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#4a90d9' },
    // ... customize colors
  },
});
```

### Add New Pages

1. Create page component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation item to menu

### Add New Visualizations

1. Create component in `src/components/`
2. Use Chart.js, Three.js, or D3.js
3. Import and use in pages

## Responsive Design

The application is fully responsive:
- **Mobile**: < 600px (hamburger menu, single column)
- **Tablet**: 600px - 1200px (2-column layouts)
- **Desktop**: > 1200px (full sidebar, multi-column)

## Performance

- Code splitting with React.lazy (future enhancement)
- Lazy loading for 3D visualizations
- Optimized image loading
- Memoized computations in charts

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create a feature branch
2. Make your changes
3. Run linting and tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Exoplanet data from NASA Exoplanet Archive
- Icons from Material-UI Icons
- Fonts from Google Fonts (Inter)

---

**Built with ❤️ for astronomy research and education**

🔬 AstroAI-Core Project | 2024
