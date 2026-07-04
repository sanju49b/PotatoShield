'use client'

import React from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix default marker
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface MapViewProps {
  location: { name: string; lat: number; lon: number }
  diseaseRisks: any[]
  fields: any[]
}

export default function MapView({ location, diseaseRisks, fields }: MapViewProps) {
  if (!location) return null
  
  const position: [number, number] = [location.lat, location.lon]
  const avgRisk = diseaseRisks.length > 0 
    ? diseaseRisks.reduce((sum, r) => sum + (r.overall_pct || 0), 0) / diseaseRisks.length 
    : 0

  return (
    <section className="bg-[#2d2d2d] rounded-xl p-6 border border-[#3a3a3a] shadow-xl">
      <h2 className="text-2xl font-bold text-[#e8e8e8] mb-4 flex items-center gap-2">
        🗺️ Field Location & Risk Map
      </h2>
      <div className="h-96 rounded-lg overflow-hidden border border-[#3a3a3a]">
        <MapContainer
          center={position}
          zoom={12}
          style={{ height: '100%', width: '100%' }}
          className="z-0"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={position}>
            <Popup>
              <div className="text-sm">
                <strong>{location.name}</strong><br />
                Avg Risk: {Math.round(avgRisk)}%<br />
                Lat: {location.lat.toFixed(4)}, Lon: {location.lon.toFixed(4)}
              </div>
            </Popup>
          </Marker>
        </MapContainer>
      </div>
    </section>
  )
}

