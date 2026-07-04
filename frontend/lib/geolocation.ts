/**
 * Production-grade geolocation utilities
 */

export interface LocationResult {
  success: boolean
  location?: string
  coordinates?: {
    lat: number
    lng: number
  }
  error?: string
}

/**
 * Get current device location using browser Geolocation API
 */
export async function getCurrentLocation(): Promise<LocationResult> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve({
        success: false,
        error: 'Geolocation is not supported by your browser',
      })
      return
    }

    const options: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 10000, // 10 seconds
      maximumAge: 0, // Don't use cached position
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords

        // Reverse geocode to get readable location
        try {
          const locationName = await reverseGeocode(latitude, longitude)
          resolve({
            success: true,
            location: locationName,
            coordinates: {
              lat: latitude,
              lng: longitude,
            },
          })
        } catch (error) {
          // If reverse geocoding fails, use coordinates
          resolve({
            success: true,
            location: `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`,
            coordinates: {
              lat: latitude,
              lng: longitude,
            },
          })
        }
      },
      (error) => {
        let errorMessage = 'Failed to get location'

        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access denied. Please enable location permissions and try again.'
            break
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable. Please enter location manually.'
            break
          case error.TIMEOUT:
            errorMessage = 'Location request timed out. Please try again.'
            break
          default:
            errorMessage = 'An error occurred while getting location.'
            break
        }

        resolve({
          success: false,
          error: errorMessage,
        })
      },
      options
    )
  })
}

/**
 * Reverse geocode coordinates to get readable location name
 * Uses OpenStreetMap Nominatim (free, no API key required)
 */
async function reverseGeocode(lat: number, lng: number): Promise<string> {
  try {
    // Use OpenStreetMap Nominatim API (free, respects rate limits)
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10&addressdetails=1`,
      {
        headers: {
          'User-Agent': 'Potato-Shield-App/1.0', // Required by Nominatim
        },
      }
    )

    if (!response.ok) {
      throw new Error('Reverse geocoding failed')
    }

    const data = await response.json()

    if (data.address) {
      const address = data.address

      // Build readable location string
      const parts: string[] = []

      if (address.city || address.town || address.village) {
        parts.push(address.city || address.town || address.village)
      }

      if (address.state || address.county) {
        parts.push(address.state || address.county)
      }

      if (address.country) {
        parts.push(address.country)
      }

      // If we have parts, join them, otherwise use display_name
      if (parts.length > 0) {
        return parts.join(', ')
      }

      // Fallback to display_name
      if (data.display_name) {
        return data.display_name.split(',')[0] // Just the first part
      }
    }

    // Final fallback to coordinates
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`
  } catch (error) {
    console.error('Reverse geocoding error:', error)
    // Return coordinates as fallback
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`
  }
}

/**
 * Check if geolocation is available
 */
export function isGeolocationAvailable(): boolean {
  return 'geolocation' in navigator
}

/**
 * Request location permission
 */
export async function requestLocationPermission(): Promise<boolean> {
  if (!isGeolocationAvailable()) {
    return false
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      () => resolve(true),
      () => resolve(false),
      { timeout: 1000 }
    )
  })
}

