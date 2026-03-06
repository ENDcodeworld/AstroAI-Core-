import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Trail } from '@react-three/drei';
import * as THREE from 'three';
import type { Exoplanet } from '../types';

interface OrbitViewerProps {
  planet: Exoplanet;
  width?: number;
  height?: number;
}

function PlanetOrbit({ planet }: { planet: Exoplanet }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const orbitRef = useRef<THREE.LineSegments>(null);
  
  // Scale factors for visualization
  const orbitScale = 5;
  const planetScale = 0.3;
  
  // Create orbit path
  const orbitPoints = useMemo(() => {
    const points = [];
    const segments = 128;
    
    for (let i = 0; i <= segments; i++) {
      const angle = (i / segments) * Math.PI * 2;
      const r = planet.semiMajorAxis * orbitScale;
      
      // Account for eccentricity
      const x = r * (1 - planet.eccentricity ** 2) / (1 + planet.eccentricity * Math.cos(angle)) * Math.cos(angle);
      const z = r * (1 - planet.eccentricity ** 2) / (1 + planet.eccentricity * Math.cos(angle)) * Math.sin(angle);
      
      points.push(new THREE.Vector3(x, 0, z));
    }
    
    return points;
  }, [planet.semiMajorAxis, planet.eccentricity]);

  const orbitGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(orbitPoints);
  }, [orbitPoints]);

  // Animate planet along orbit
  useFrame(({ clock }) => {
    if (meshRef.current) {
      const t = clock.getElapsedTime() * 0.1;
      const angle = t % (Math.PI * 2);
      
      const r = planet.semiMajorAxis * orbitScale;
      const x = r * Math.cos(angle);
      const z = r * Math.sin(angle);
      
      meshRef.current.position.set(x, 0, z);
      meshRef.current.rotation.y += 0.01;
    }
  });

  return (
    <group>
      {/* Orbit path */}
      <lineSegments ref={orbitRef}>
        <bufferGeometry attach="geometry" {...orbitGeometry} />
        <lineBasicMaterial attach="material" color="#4a90d9" transparent opacity={0.4} />
      </lineSegments>

      {/* Star at center */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial 
          color="#feca57" 
          emissive="#feca57" 
          emissiveIntensity={2}
        />
        <pointLight intensity={2} distance={20} />
      </mesh>

      {/* Planet */}
      <Trail width={1} length={4} color={planet.habitableZone ? '#4caf50' : '#ff6b6b'} attenuation={(t) => t * t}>
        <mesh ref={meshRef}>
          <sphereGeometry args={[planetScale * planet.radius, 32, 32]} />
          <meshStandardMaterial
            color={planet.habitableZone ? '#4caf50' : '#ff6b6b'}
            roughness={0.8}
            metalness={0.2}
          />
        </mesh>
      </Trail>
    </group>
  );
}

function Scene({ planet }: { planet: Exoplanet }) {
  return (
    <>
      <ambientLight intensity={0.2} />
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <PlanetOrbit planet={planet} />
      <OrbitControls 
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={2}
        maxDistance={50}
        autoRotate
        autoRotateSpeed={0.5}
      />
    </>
  );
}

export const OrbitViewer: React.FC<OrbitViewerProps> = ({ 
  planet, 
  width = 800, 
  height = 600 
}) => {
  return (
    <div style={{ width, height, background: '#0a0a1a' }}>
      <Canvas camera={{ position: [0, 10, 15], fov: 60 }}>
        <Scene planet={planet} />
      </Canvas>
    </div>
  );
};
