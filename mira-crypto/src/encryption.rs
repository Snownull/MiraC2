use aes_gcm::{Aes256Gcm, KeyInit, aead::{Aead, generic_array::GenericArray}};
use rand::RngCore;
use anyhow::Result;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CryptoError {
    #[error("Encryption failed: {0}")]
    EncryptionFailed(String),
    #[error("Decryption failed: {0}")]
    DecryptionFailed(String),
    #[error("Invalid key length: expected {expected}, got {actual}")]
    InvalidKeyLength { expected: usize, actual: usize },
    #[error("Invalid data format")]
    InvalidDataFormat,
}

/// AES-256-GCM encryption implementation matching the C# version
pub struct AesEncryption {
    cipher: Aes256Gcm,
}

impl AesEncryption {
    /// Create new AES encryption instance with a 32-byte key
    pub fn new(key: &[u8]) -> Result<Self> {
        if key.len() != 32 {
            return Err(CryptoError::InvalidKeyLength { 
                expected: 32, 
                actual: key.len() 
            }.into());
        }
        
        let key = GenericArray::from_slice(key);
        let cipher = Aes256Gcm::new(key);
        
        Ok(Self { cipher })
    }

    /// Encrypt data with AES-256-GCM
    /// Returns: [nonce (12 bytes)][encrypted_data][tag (16 bytes)]
    pub fn encrypt(&self, data: &[u8]) -> Result<Vec<u8>> {
        // Generate random nonce
        let mut nonce_bytes = [0u8; 12];
        rand::thread_rng().fill_bytes(&mut nonce_bytes);
        let nonce = GenericArray::from_slice(&nonce_bytes);
        
        // Encrypt the data
        let ciphertext = self.cipher
            .encrypt(nonce, data)
            .map_err(|e| CryptoError::EncryptionFailed(e.to_string()))?;
        
        // Combine nonce + ciphertext
        let mut result = Vec::with_capacity(12 + ciphertext.len());
        result.extend_from_slice(&nonce_bytes);
        result.extend_from_slice(&ciphertext);
        
        Ok(result)
    }

    /// Decrypt data encrypted with encrypt()
    /// Expects: [nonce (12 bytes)][encrypted_data][tag (16 bytes)]
    pub fn decrypt(&self, data: &[u8]) -> Result<Vec<u8>> {
        if data.len() < 12 + 16 {
            return Err(CryptoError::InvalidDataFormat.into());
        }
        
        // Extract nonce and ciphertext
        let nonce = GenericArray::from_slice(&data[..12]);
        let ciphertext = &data[12..];
        
        // Decrypt the data
        let plaintext = self.cipher
            .decrypt(nonce, ciphertext)
            .map_err(|e| CryptoError::DecryptionFailed(e.to_string()))?;
        
        Ok(plaintext)
    }
}

/// Simple encryption utility functions
pub struct EncryptionUtils;

impl EncryptionUtils {
    /// Generate a random 256-bit (32-byte) encryption key
    pub fn generate_key() -> [u8; 32] {
        let mut key = [0u8; 32];
        rand::thread_rng().fill_bytes(&mut key);
        key
    }
    
    /// Encrypt data with a new random key
    /// Returns (encrypted_data, key)
    pub fn encrypt_with_new_key(data: &[u8]) -> Result<(Vec<u8>, [u8; 32])> {
        let key = Self::generate_key();
        let encryption = AesEncryption::new(&key)?;
        let encrypted_data = encryption.encrypt(data)?;
        Ok((encrypted_data, key))
    }
    
    /// Decrypt data with the given key
    pub fn decrypt_with_key(encrypted_data: &[u8], key: &[u8; 32]) -> Result<Vec<u8>> {
        let encryption = AesEncryption::new(key)?;
        encryption.decrypt(encrypted_data)
    }
    
    /// Convert key to base64 string (for storage/transmission)
    pub fn key_to_base64(key: &[u8; 32]) -> String {
        base64::encode(key)
    }
    
    /// Convert base64 string back to key
    pub fn key_from_base64(base64_key: &str) -> Result<[u8; 32]> {
        let key_bytes = base64::decode(base64_key)
            .map_err(|e| anyhow::anyhow!("Invalid base64 key: {}", e))?;
        
        if key_bytes.len() != 32 {
            return Err(CryptoError::InvalidKeyLength { 
                expected: 32, 
                actual: key_bytes.len() 
            }.into());
        }
        
        let mut key = [0u8; 32];
        key.copy_from_slice(&key_bytes);
        Ok(key)
    }
}

// Add base64 dependency to the Cargo.toml if not already present
// We'll implement a simple base64 encoder/decoder for now

mod base64 {
    const ALPHABET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    
    pub fn encode(data: &[u8]) -> String {
        let mut result = String::new();
        let mut i = 0;
        
        while i + 2 < data.len() {
            let chunk = ((data[i] as u32) << 16) | ((data[i + 1] as u32) << 8) | (data[i + 2] as u32);
            result.push(ALPHABET[((chunk >> 18) & 63) as usize] as char);
            result.push(ALPHABET[((chunk >> 12) & 63) as usize] as char);
            result.push(ALPHABET[((chunk >> 6) & 63) as usize] as char);
            result.push(ALPHABET[(chunk & 63) as usize] as char);
            i += 3;
        }
        
        // Handle padding
        match data.len() - i {
            1 => {
                let chunk = (data[i] as u32) << 16;
                result.push(ALPHABET[((chunk >> 18) & 63) as usize] as char);
                result.push(ALPHABET[((chunk >> 12) & 63) as usize] as char);
                result.push_str("==");
            }
            2 => {
                let chunk = ((data[i] as u32) << 16) | ((data[i + 1] as u32) << 8);
                result.push(ALPHABET[((chunk >> 18) & 63) as usize] as char);
                result.push(ALPHABET[((chunk >> 12) & 63) as usize] as char);
                result.push(ALPHABET[((chunk >> 6) & 63) as usize] as char);
                result.push('=');
            }
            _ => {}
        }
        
        result
    }
    
    pub fn decode(data: &str) -> Result<Vec<u8>, &'static str> {
        let data = data.trim_end_matches('=');
        let mut result = Vec::new();
        let mut buffer = 0u32;
        let mut bits = 0;
        
        for c in data.chars() {
            let value = match c {
                'A'..='Z' => c as u32 - 'A' as u32,
                'a'..='z' => c as u32 - 'a' as u32 + 26,
                '0'..='9' => c as u32 - '0' as u32 + 52,
                '+' => 62,
                '/' => 63,
                _ => return Err("Invalid character in base64"),
            };
            
            buffer = (buffer << 6) | value;
            bits += 6;
            
            if bits >= 8 {
                result.push((buffer >> (bits - 8)) as u8);
                bits -= 8;
            }
        }
        
        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_aes_encryption_roundtrip() {
        let key = EncryptionUtils::generate_key();
        let aes = AesEncryption::new(&key).unwrap();
        
        let original_data = b"Hello, World! This is a test message.";
        let encrypted = aes.encrypt(original_data).unwrap();
        let decrypted = aes.decrypt(&encrypted).unwrap();
        
        assert_eq!(original_data, decrypted.as_slice());
    }

    #[test]
    fn test_encryption_utils() {
        let data = b"Test data for encryption";
        let (encrypted, key) = EncryptionUtils::encrypt_with_new_key(data).unwrap();
        let decrypted = EncryptionUtils::decrypt_with_key(&encrypted, &key).unwrap();
        
        assert_eq!(data, decrypted.as_slice());
    }

    #[test]
    fn test_key_base64_conversion() {
        let key = EncryptionUtils::generate_key();
        let base64_key = EncryptionUtils::key_to_base64(&key);
        let restored_key = EncryptionUtils::key_from_base64(&base64_key).unwrap();
        
        assert_eq!(key, restored_key);
    }
}