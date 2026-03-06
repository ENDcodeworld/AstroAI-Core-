export interface Exoplanet {
  id: string;
  name: string;
  hostStar: string;
  constellation: string;
  distance: number; // light years
  mass: number; // Earth masses
  radius: number; // Earth radii
  orbitalPeriod: number; // days
  semiMajorAxis: number; // AU
  eccentricity: number;
  discoveryYear: number;
  discoveryMethod: string;
  temperature: number; // Kelvin
  habitableZone: boolean;
  description: string;
  imageUrl?: string;
}

export interface ClassificationResult {
  id: string;
  imageUrl: string;
  className: string;
  confidence: number;
  timestamp: Date;
  alternativeClasses: { class: string; confidence: number }[];
}

export interface User {
  id: string;
  username: string;
  email: string;
  createdAt: Date;
}

export interface FilterState {
  search: string;
  constellation: string;
  discoveryMethod: string;
  habitableOnly: boolean;
  sortBy: 'name' | 'distance' | 'mass' | 'discoveryYear';
  sortOrder: 'asc' | 'desc';
}

export type PageState = 'list' | 'detail';
