use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use crate::data::{ClientInfo, PasswordEntry, FileTransfer};

/// Event types for communication between Rust core and Python GUI
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MiraEvent {
    /// Client events
    ClientConnected(ClientInfo),
    ClientDisconnected(String), // IP address
    ClientUpdated(ClientInfo),
    
    /// File transfer events
    FileTransferStarted(FileTransfer),
    FileTransferProgress(String, u64, u64), // client_ip, received_bytes, total_bytes
    FileTransferCompleted(String, String),   // client_ip, filename
    FileTransferFailed(String, String),      // client_ip, error_message
    
    /// Password events
    PasswordsExtracted(Vec<PasswordEntry>),
    
    /// System events
    ServerStarted(u16), // port
    ServerStopped,
    ServerError(String),
    
    /// Log events matching the original LogType enum
    LogEntry(LogEntry),
    
    /// Statistics updates
    StatsUpdated(crate::data::SystemStats),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEntry {
    pub timestamp: DateTime<Utc>,
    pub message: String,
    pub log_type: LogType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum LogType {
    Info,
    Warning,
    Error,
    Connection,
    DataTransfer,
    Security,
    System,
}

impl LogType {
    /// Get the color for this log type (RGB tuple for Python GUI)
    pub fn color_rgb(&self) -> (u8, u8, u8) {
        match self {
            LogType::Error => (255, 0, 0),        // Red
            LogType::Warning => (255, 165, 0),     // Orange
            LogType::Info => (255, 255, 255),      // White
            LogType::Connection => (144, 238, 144), // LightGreen
            LogType::DataTransfer => (173, 216, 230), // LightBlue
            LogType::Security => (255, 255, 0),    // Yellow
            LogType::System => (128, 128, 128),    // Gray
        }
    }
}

impl LogEntry {
    pub fn new(message: String, log_type: LogType) -> Self {
        Self {
            timestamp: Utc::now(),
            message,
            log_type,
        }
    }
    
    pub fn info(message: String) -> Self {
        Self::new(message, LogType::Info)
    }
    
    pub fn warning(message: String) -> Self {
        Self::new(message, LogType::Warning)
    }
    
    pub fn error(message: String) -> Self {
        Self::new(message, LogType::Error)
    }
    
    pub fn connection(message: String) -> Self {
        Self::new(message, LogType::Connection)
    }
    
    pub fn data_transfer(message: String) -> Self {
        Self::new(message, LogType::DataTransfer)
    }
    
    pub fn security(message: String) -> Self {
        Self::new(message, LogType::Security)
    }
    
    pub fn system(message: String) -> Self {
        Self::new(message, LogType::System)
    }
}