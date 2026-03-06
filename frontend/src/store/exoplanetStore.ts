import { create } from 'zustand';
import type { Exoplanet, FilterState } from '../types';

interface ExoplanetState {
  planets: Exoplanet[];
  filteredPlanets: Exoplanet[];
  selectedPlanet: Exoplanet | null;
  filters: FilterState;
  currentPage: number;
  itemsPerPage: number;
  loading: boolean;
  error: string | null;
  
  // Actions
  setPlanets: (planets: Exoplanet[]) => void;
  setSelectedPlanet: (planet: Exoplanet | null) => void;
  updateFilters: (filters: Partial<FilterState>) => void;
  resetFilters: () => void;
  setCurrentPage: (page: number) => void;
  fetchPlanets: () => Promise<void>;
}

const defaultFilters: FilterState = {
  search: '',
  constellation: '',
  discoveryMethod: '',
  habitableOnly: false,
  sortBy: 'name',
  sortOrder: 'asc',
};

// Mock data for development
const mockPlanets: Exoplanet[] = [
  {
    id: '1',
    name: 'Kepler-452b',
    hostStar: 'Kepler-452',
    constellation: 'Cygnus',
    distance: 1402,
    mass: 5.0,
    radius: 1.63,
    orbitalPeriod: 384.8,
    semiMajorAxis: 1.046,
    eccentricity: 0.0,
    discoveryYear: 2015,
    discoveryMethod: 'Transit',
    temperature: 265,
    habitableZone: true,
    description: 'Often called Earth\'s cousin, Kepler-452b orbits in the habitable zone of a Sun-like star.',
  },
  {
    id: '2',
    name: 'Proxima Centauri b',
    hostStar: 'Proxima Centauri',
    constellation: 'Centaurus',
    distance: 4.24,
    mass: 1.27,
    radius: 1.1,
    orbitalPeriod: 11.2,
    semiMajorAxis: 0.0485,
    eccentricity: 0.0,
    discoveryYear: 2016,
    discoveryMethod: 'Radial Velocity',
    temperature: 234,
    habitableZone: true,
    description: 'The closest known exoplanet to Earth, orbiting our nearest stellar neighbor.',
  },
  {
    id: '3',
    name: 'TRAPPIST-1e',
    hostStar: 'TRAPPIST-1',
    constellation: 'Aquarius',
    distance: 39.6,
    mass: 0.772,
    radius: 0.918,
    orbitalPeriod: 6.1,
    semiMajorAxis: 0.0293,
    eccentricity: 0.0,
    discoveryYear: 2017,
    discoveryMethod: 'Transit',
    temperature: 251,
    habitableZone: true,
    description: 'One of seven planets in the TRAPPIST-1 system, potentially rocky and in the habitable zone.',
  },
  {
    id: '4',
    name: '51 Pegasi b',
    hostStar: '51 Pegasi',
    constellation: 'Pegasus',
    distance: 50.9,
    mass: 150.0,
    radius: 1.9,
    orbitalPeriod: 4.23,
    semiMajorAxis: 0.0527,
    eccentricity: 0.01,
    discoveryYear: 1995,
    discoveryMethod: 'Radial Velocity',
    temperature: 1284,
    habitableZone: false,
    description: 'The first exoplanet discovered orbiting a Sun-like star, a hot Jupiter.',
  },
  {
    id: '5',
    name: 'HD 209458 b',
    hostStar: 'HD 209458',
    constellation: 'Pegasus',
    distance: 159,
    mass: 220.0,
    radius: 1.38,
    orbitalPeriod: 3.52,
    semiMajorAxis: 0.047,
    eccentricity: 0.0,
    discoveryYear: 1999,
    discoveryMethod: 'Transit',
    temperature: 1450,
    habitableZone: false,
    description: 'First exoplanet observed transiting its star, allowing atmospheric studies.',
  },
];

export const useExoplanetStore = create<ExoplanetState>((set, get) => ({
  planets: [],
  filteredPlanets: [],
  selectedPlanet: null,
  filters: defaultFilters,
  currentPage: 1,
  itemsPerPage: 10,
  loading: false,
  error: null,

  setPlanets: (planets) => {
    const { filters } = get();
    const filtered = applyFilters(planets, filters);
    set({ planets, filteredPlanets: filtered });
  },

  setSelectedPlanet: (planet) => set({ selectedPlanet: planet }),

  updateFilters: (newFilters) => {
    const { planets, filters } = get();
    const updatedFilters = { ...filters, ...newFilters };
    const filtered = applyFilters(planets, updatedFilters);
    set({ filters: updatedFilters, filteredPlanets: filtered, currentPage: 1 });
  },

  resetFilters: () => {
    const { planets } = get();
    set({ filters: defaultFilters, filteredPlanets: planets, currentPage: 1 });
  },

  setCurrentPage: (page) => set({ currentPage: page }),

  fetchPlanets: async () => {
    set({ loading: true, error: null });
    try {
      // In production, fetch from API
      // const response = await axios.get('/api/exoplanets');
      // setPlanets(response.data);
      
      // Using mock data for now
      await new Promise(resolve => setTimeout(resolve, 500));
      get().setPlanets(mockPlanets);
    } catch (error) {
      set({ error: 'Failed to fetch exoplanets', loading: false });
    } finally {
      set({ loading: false });
    }
  },
}));

function applyFilters(planets: Exoplanet[], filters: FilterState): Exoplanet[] {
  let result = [...planets];

  if (filters.search) {
    const search = filters.search.toLowerCase();
    result = result.filter(p => 
      p.name.toLowerCase().includes(search) ||
      p.hostStar.toLowerCase().includes(search) ||
      p.constellation.toLowerCase().includes(search)
    );
  }

  if (filters.constellation) {
    result = result.filter(p => p.constellation === filters.constellation);
  }

  if (filters.discoveryMethod) {
    result = result.filter(p => p.discoveryMethod === filters.discoveryMethod);
  }

  if (filters.habitableOnly) {
    result = result.filter(p => p.habitableZone);
  }

  // Sorting
  result.sort((a, b) => {
    const aValue = a[filters.sortBy];
    const bValue = b[filters.sortBy];
    const modifier = filters.sortOrder === 'asc' ? 1 : -1;
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return aValue.localeCompare(bValue) * modifier;
    }
    return ((aValue as number) - (bValue as number)) * modifier;
  });

  return result;
}
