/// Format file size in human readable format (matching C# FormatFileSize)
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

/// Generate a random string of specified length (matching C# RandomStringGenerator)
pub fn generate_random_string(length: usize) -> String {
    use rand::Rng;
    const CHARS: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    
    let mut rng = rand::thread_rng();
    (0..length)
        .map(|_| {
            let idx = rng.gen_range(0..CHARS.len());
            CHARS[idx] as char
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_file_size() {
        assert_eq!(format_file_size(512), "512.00 B");
        assert_eq!(format_file_size(1024), "1.00 KB");
        assert_eq!(format_file_size(1536), "1.50 KB");
        assert_eq!(format_file_size(1048576), "1.00 MB");
    }

    #[test]
    fn test_generate_random_string() {
        let s1 = generate_random_string(16);
        let s2 = generate_random_string(16);
        
        assert_eq!(s1.len(), 16);
        assert_eq!(s2.len(), 16);
        assert_ne!(s1, s2); // Very unlikely to be the same
        
        // Check that all characters are alphanumeric
        assert!(s1.chars().all(|c| c.is_alphanumeric()));
    }
}