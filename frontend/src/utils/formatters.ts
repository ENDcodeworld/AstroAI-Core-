/**
 * Format large numbers with K, M, B suffixes
 */
export const formatNumber = (num: number, decimals: number = 1): string => {
  if (num >= 1e9) {
    return (num / 1e9).toFixed(decimals) + 'B';
  }
  if (num >= 1e6) {
    return (num / 1e6).toFixed(decimals) + 'M';
  }
  if (num >= 1e3) {
    return (num / 1e3).toFixed(decimals) + 'K';
  }
  return num.toFixed(decimals);
};

/**
 * Format distance with appropriate unit
 */
export const formatDistance = (lightYears: number): string => {
  if (lightYears < 1) {
    return `${(lightYears * 3.26).toFixed(2)} pc`; // Parsecs
  }
  if (lightYears < 1000) {
    return `${lightYears.toFixed(1)} ly`;
  }
  return `${formatNumber(lightYears, 1)} ly`;
};

/**
 * Format temperature
 */
export const formatTemperature = (kelvin: number): string => {
  const celsius = kelvin - 273.15;
  return `${kelvin.toFixed(0)} K (${celsius.toFixed(0)}°C)`;
};

/**
 * Format mass in Earth masses
 */
export const formatMass = (earthMasses: number): string => {
  if (earthMasses >= 318) {
    return `${(earthMasses / 318).toFixed(2)} MJ`; // Jupiter masses
  }
  return `${earthMasses.toFixed(2)} M⊕`;
};

/**
 * Format radius in Earth radii
 */
export const formatRadius = (earthRadii: number): string => {
  if (earthRadii >= 11) {
    return `${(earthRadii / 11).toFixed(2)} RJ`; // Jupiter radii
  }
  return `${earthRadii.toFixed(2)} R⊕`;
};

/**
 * Format orbital period
 */
export const formatOrbitalPeriod = (days: number): string => {
  if (days < 1) {
    return `${(days * 24).toFixed(1)} hours`;
  }
  if (days < 365) {
    return `${days.toFixed(1)} days`;
  }
  return `${(days / 365).toFixed(2)} years`;
};

/**
 * Format semi-major axis
 */
export const formatSemiMajorAxis = (au: number): string => {
  if (au < 1) {
    return `${(au * 149597870.7).toFixed(0)} km`;
  }
  return `${au.toFixed(3)} AU`;
};

/**
 * Format confidence percentage
 */
export const formatConfidence = (confidence: number): string => {
  return `${(confidence * 100).toFixed(1)}%`;
};

/**
 * Format date relative to now
 */
export const formatRelativeDate = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - new Date(date).getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return new Date(date).toLocaleDateString();
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

export default {
  formatNumber,
  formatDistance,
  formatTemperature,
  formatMass,
  formatRadius,
  formatOrbitalPeriod,
  formatSemiMajorAxis,
  formatConfidence,
  formatRelativeDate,
  formatFileSize,
};
