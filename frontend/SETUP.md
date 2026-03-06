# AstroAI-Core Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd /home/admin/.openclaw/workspace/projects/AstroAI-Core/frontend
npm install
```

### 2. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your API settings if connecting to a backend
```

### 3. Start Development Server

```bash
npm run dev
```

The app will open at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
npm run preview  # Test production build
```

## Development Workflow

### Running in Development

The Vite dev server provides:
- Hot Module Replacement (HMR)
- Fast refresh
- TypeScript checking
- ESLint warnings

### Code Style

- ESLint is configured for React + TypeScript
- Run linting: `npm run lint`
- Fix auto-fixable issues: `npm run lint -- --fix`

### Adding New Features

1. **New Component**: Create in `src/components/`
2. **New Page**: Create in `src/pages/` and add route in `App.tsx`
3. **New Store**: Create in `src/store/` and export from `index.ts`
4. **New Hook**: Create in `src/hooks/` and export from `index.ts`
5. **New Utility**: Create in `src/utils/` and export from `index.ts`

### State Management

We use Zustand for state management:

```typescript
import { useExoplanetStore } from '@store/exoplanetStore';

function MyComponent() {
  const planets = useExoplanetStore(state => state.planets);
  const setPlanets = useExoplanetStore(state => state.setPlanets);
  
  // Use state and actions
}
```

### API Integration

API calls are organized in `src/utils/api.ts`:

```typescript
import { exoplanetApi } from '@utils/api';

async function loadPlanets() {
  const response = await exoplanetApi.getAll();
  return response.data;
}
```

## Testing

### Manual Testing Checklist

- [ ] Exoplanet list loads correctly
- [ ] Search and filters work
- [ ] Planet detail page shows correct data
- [ ] 3D orbit visualization renders
- [ ] Image upload works (single and batch)
- [ ] Classification results display
- [ ] Charts render correctly
- [ ] Responsive design on mobile/tablet
- [ ] Navigation works
- [ ] User authentication flow

### Browser Testing

Test on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Deployment

### Build Optimization

The production build includes:
- Minification
- Tree shaking
- Code splitting
- Asset optimization

### Deploy to Static Host

1. Build: `npm run build`
2. Upload `dist/` folder to:
   - Vercel
   - Netlify
   - GitHub Pages
   - AWS S3 + CloudFront
   - Your own server

### Environment Variables for Production

Set these in your hosting platform:
- `VITE_API_BASE_URL` - Your production API URL
- `VITE_API_VERSION` - API version (e.g., `v1`)

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Node modules issues:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors:**
```bash
npx tsc --noEmit
```

**Build fails:**
```bash
npm run build -- --debug
```

### Performance Issues

- Check bundle size: `npm run build`
- Analyze bundle: `npx vite-bundle-visualizer`
- Lazy load heavy components (Three.js, charts)

## Architecture Overview

### Component Hierarchy

```
App (Router + Theme + Layout)
├── Navigation (AppBar + Drawer)
├── Exoplanets (List Page)
│   └── PlanetCard (Reusable)
├── ExoplanetDetail (Detail Page)
│   └── OrbitViewer (3D Visualization)
├── ImageClassifier (Classification Page)
│   └── ImageUpload (Reusable)
└── Visualization (Data Viz Page)
    └── SizeChart (Charts)
```

### State Flow

```
User Action → Store Action → State Update → Component Re-render
```

### Data Flow

```
API → Store → Components → UI
User Input → Store → API → Store → Components
```

## Contributing Guidelines

1. **Branch Naming**: `feature/xyz`, `bugfix/xyz`, `chore/xyz`
2. **Commit Messages**: Conventional Commits format
3. **Code Review**: All changes require review
4. **Testing**: Test all affected features
5. **Documentation**: Update README for new features

## Resources

- [React Documentation](https://react.dev)
- [Material-UI Documentation](https://mui.com)
- [Zustand Documentation](https://zustand-demo.pmnd.rs)
- [Three.js Documentation](https://threejs.org)
- [Chart.js Documentation](https://www.chartjs.org)
- [Vite Documentation](https://vitejs.dev)

## Support

For issues or questions:
1. Check existing issues
2. Review documentation
3. Contact the development team

---

**Happy Coding! 🚀**
