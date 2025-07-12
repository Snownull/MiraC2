use rand::RngCore;
use sha2::{Sha256, Digest};

/// Key generation utilities
pub struct KeyGenerator;

impl KeyGenerator {
    /// Generate a cryptographically secure random key
    pub fn generate_random_key(length: usize) -> Vec<u8> {
        let mut key = vec![0u8; length];
        rand::thread_rng().fill_bytes(&mut key);
        key
    }
    
    /// Generate a key from a password using PBKDF2-like stretching
    pub fn derive_key_from_password(password: &str, salt: &[u8], iterations: u32) -> [u8; 32] {
        let mut key = password.as_bytes().to_vec();
        key.extend_from_slice(salt);
        
        for _ in 0..iterations {
            key = Sha256::digest(&key).to_vec();
        }
        
        let mut result = [0u8; 32];
        result.copy_from_slice(&key[..32]);
        result
    }
    
    /// Generate a deterministic key from client information
    /// This can be used to generate consistent keys for client identification
    pub fn derive_client_key(client_ip: &str, secret: &str) -> [u8; 32] {
        let input = format!("{}:{}", client_ip, secret);
        let hash = Sha256::digest(input.as_bytes());
        
        let mut key = [0u8; 32];
        key.copy_from_slice(&hash);
        key
    }
    
    /// Generate a session key from multiple inputs
    pub fn generate_session_key(components: &[&str]) -> [u8; 32] {
        let combined = components.join(":");
        let hash = Sha256::digest(combined.as_bytes());
        
        let mut key = [0u8; 32];
        key.copy_from_slice(&hash);
        key
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_random_key_generation() {
        let key1 = KeyGenerator::generate_random_key(32);
        let key2 = KeyGenerator::generate_random_key(32);
        
        assert_eq!(key1.len(), 32);
        assert_eq!(key2.len(), 32);
        assert_ne!(key1, key2); // Should be different
    }

    #[test]
    fn test_password_key_derivation() {
        let password = "test_password";
        let salt = b"test_salt";
        let iterations = 1000;
        
        let key1 = KeyGenerator::derive_key_from_password(password, salt, iterations);
        let key2 = KeyGenerator::derive_key_from_password(password, salt, iterations);
        
        assert_eq!(key1, key2); // Should be deterministic
        
        // Different password should produce different key
        let key3 = KeyGenerator::derive_key_from_password("different_password", salt, iterations);
        assert_ne!(key1, key3);
    }

    #[test]
    fn test_client_key_derivation() {
        let client_ip = "192.168.1.100";
        let secret = "server_secret";
        
        let key1 = KeyGenerator::derive_client_key(client_ip, secret);
        let key2 = KeyGenerator::derive_client_key(client_ip, secret);
        
        assert_eq!(key1, key2); // Should be deterministic
        
        // Different IP should produce different key
        let key3 = KeyGenerator::derive_client_key("192.168.1.101", secret);
        assert_ne!(key1, key3);
    }

    #[test]
    fn test_session_key_generation() {
        let components = vec!["component1", "component2", "component3"];
        
        let key1 = KeyGenerator::generate_session_key(&components);
        let key2 = KeyGenerator::generate_session_key(&components);
        
        assert_eq!(key1, key2); // Should be deterministic
        
        // Different components should produce different key
        let different_components = vec!["component1", "component2", "different"];
        let key3 = KeyGenerator::generate_session_key(&different_components);
        assert_ne!(key1, key3);
    }
}