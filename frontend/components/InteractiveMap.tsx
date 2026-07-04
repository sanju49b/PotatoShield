'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { getApiBaseUrl } from '@/lib/api'
import { LatLngExpression } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import type { LeafletMouseEvent } from 'leaflet'

// Fix default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Dynamically import Leaflet components (required for Next.js SSR)
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
)
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
)
const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
)
const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
)
const Circle = dynamic(
  () => import('react-leaflet').then((mod) => mod.Circle),
  { ssr: false }
)

interface InteractiveMapProps {
  location: string
  latitude?: number
  longitude?: number
  elevation?: number
  risk?: number
  onPointClick?: (payload: { lat: number; lon: number; location: string }) => void
}


export default function InteractiveMap({ location, latitude, longitude, elevation, risk, onPointClick }: InteractiveMapProps) {
  const [coordinates, setCoordinates] = useState<[number, number] | null>(null)
  const [loading, setLoading] = useState(true)
  const [mapView, setMapView] = useState<'streets' | 'satellite'>('streets')

  useEffect(() => {
    const loadCoordinates = async () => {
      // Priority 1: Use provided coordinates directly (most reliable)
      // Convert to numbers in case they're strings
      const lat = typeof latitude === 'string' ? parseFloat(latitude) : latitude
      const lon = typeof longitude === 'string' ? parseFloat(longitude) : longitude
      
      if (lat && lon && !isNaN(lat) && !isNaN(lon) && 
          lat >= -90 && lat <= 90 && 
          lon >= -180 && lon <= 180) {
        console.log('[MAP] Using provided coordinates:', lat, lon, '(converted from:', latitude, longitude, ')')
        setCoordinates([lat, lon])
        setLoading(false)
        return
      }

      // Priority 2: Geocode location name using backend
      if (location) {
        try {
          setLoading(true)
          const token = localStorage.getItem('auth_token')
          const response = await fetch(
            `${getApiBaseUrl()}/api/geocode?query=${encodeURIComponent(location)}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            }
          )
          
          if (response.ok) {
            const data = await response.json()
            if (data.success && data.location) {
              const lat = data.location.latitude
              const lon = data.location.longitude
              console.log('[MAP] Backend geocoded:', lat, lon, 'for', location)
              setCoordinates([lat, lon])
              setLoading(false)
              return
            }
          }
        } catch (error) {
          console.error('[MAP] Backend geocoding error:', error)
        }

        // Fallback: Try Open-Meteo directly
        try {
          const fallbackResponse = await fetch(
            `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(location)}&count=1&language=en&format=json`
          )
          const fallbackData = await fallbackResponse.json()
          
          if (fallbackData.results && fallbackData.results.length > 0) {
            const result = fallbackData.results[0]
            console.log('[MAP] Open-Meteo geocoded:', result.latitude, result.longitude, 'for', location)
            setCoordinates([result.latitude, result.longitude])
            setLoading(false)
            return
          }
        } catch (error) {
          console.error('[MAP] Open-Meteo geocoding error:', error)
        }
      }

      // Default: India center
      console.warn('[MAP] Using default India center')
      setCoordinates([20.5937, 78.9629])
      setLoading(false)
    }

    loadCoordinates()
  }, [location, latitude, longitude])

  // Debug logging - must be before any returns
  useEffect(() => {
    if (coordinates) {
      console.log('[MAP] Current coordinates:', coordinates)
      console.log('[MAP] Props received - location:', location, 'lat:', latitude, 'lon:', longitude)
    }
  }, [coordinates, location, latitude, longitude])

  if (loading || !coordinates) {
    return (
      <div className="w-full h-full bg-[#1a1a1a] rounded-lg flex items-center justify-center border border-[#4a4a4a]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#b8b8b8]">Loading Map...</p>
        </div>
      </div>
    )
  }

  const position: LatLngExpression = coordinates

  return (
    <div className="relative w-full h-full" style={{ position: 'relative', zIndex: 1 }}>
      {/* Simple Map View Toggle */}
      <div className="absolute top-4 left-4 z-[1001] bg-gradient-to-br from-[#2d2d2d] to-[#1a1a1a] rounded-lg p-2 border border-orange-500/30 shadow-2xl backdrop-blur-sm" style={{ pointerEvents: 'auto' }}>
        <div className="flex gap-2">
          <button
            onClick={() => setMapView('streets')}
            className={`px-3 py-2 rounded text-sm font-medium transition-all whitespace-nowrap ${
              mapView === 'streets'
                ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-lg'
                : 'bg-[#3a3a3a] text-[#b8b8b8] hover:bg-[#4a4a4a]'
            }`}
          >
            🗺️ Streets
          </button>
          <button
            onClick={() => setMapView('satellite')}
            className={`px-3 py-2 rounded text-sm font-medium transition-all whitespace-nowrap ${
              mapView === 'satellite'
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                : 'bg-[#3a3a3a] text-[#b8b8b8] hover:bg-[#4a4a4a]'
            }`}
          >
            🛰️ Satellite
          </button>
        </div>
      </div>

      {/* Location Info Card */}
      <div className="absolute top-4 right-4 z-[1001] bg-gradient-to-br from-orange-500/95 to-yellow-500/95 rounded-lg p-4 border border-orange-400 shadow-2xl max-w-[220px] backdrop-blur-md" style={{ pointerEvents: 'auto' }}>
        <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2 leading-tight">
          📍 Your Field
        </h3>
        <div className="text-xs text-white/95 space-y-1.5 leading-relaxed">
          <p className="font-medium truncate" title={location}>📌 {location}</p>
          <p>🌐 {coordinates[0].toFixed(4)}°, {coordinates[1].toFixed(4)}°</p>
          {elevation && <p>⛰️ {elevation}m</p>}
        </div>
      </div>

      {/* Simple Plain Map - No Weather Layers */}
      <MapContainer
        center={position}
        zoom={12}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%', borderRadius: '8px', position: 'relative', zIndex: 0 }}
        className="leaflet-container-custom"
        key={`map-${coordinates[0].toFixed(2)}-${coordinates[1].toFixed(2)}`} // Force re-render on coordinate change
      >
        {/* Base Map Layer Only - No Weather Overlays */}
        {mapView === 'streets' ? (
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        ) : (
          <TileLayer
            attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        )}


        {/* Location Marker */}
        <Marker
          position={position}
          eventHandlers={{
            click: () => {
              if (onPointClick) {
                onPointClick({ lat: coordinates[0], lon: coordinates[1], location })
              }
            }
          }}
        >
          <Popup>
            <div className="text-sm">
              <strong>{location}</strong>
              <br />
              <span className="text-xs text-gray-600">
                {coordinates[0].toFixed(4)}°, {coordinates[1].toFixed(4)}°
              </span>
              {elevation && (
                <>
                  <br />
                  <span className="text-xs text-gray-600">Elevation: {elevation}m</span>
                </>
              )}
            </div>
          </Popup>
        </Marker>

        {/* Risk intensity circle (simple heat overlay) */}
        {typeof risk === 'number' && (
          <Circle
            center={position}
            radius={Math.max(300, Math.min(1500, 300 + (risk / 100) * 1200))}
            pathOptions={{
              color: risk > 75 ? '#ef4444' : risk > 50 ? '#f97316' : risk > 25 ? '#eab308' : '#22c55e',
              fillColor: risk > 75 ? '#ef4444' : risk > 50 ? '#f97316' : risk > 25 ? '#eab308' : '#22c55e',
              fillOpacity: 0.25,
              opacity: 0.6,
              weight: 2,
            }}
          />
        )}
      </MapContainer>

      {/* Heatmap-style legend */}
      <div className="absolute bottom-4 right-4 z-[1001] bg-[#1a1a1a]/90 border border-white/10 rounded-lg p-3 shadow-2xl backdrop-blur-md">
        <div className="text-xs text-white/80 mb-2">Risk Intensity</div>
        <div className="w-56 h-3 rounded bg-gradient-to-r from-[#22c55e] via-[#eab308] via-50% to-[#ef4444]"></div>
        <div className="flex justify-between text-[10px] text-white/60 mt-1">
          <span>0%</span>
          <span>25%</span>
          <span>50%</span>
          <span>75%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  )
}
