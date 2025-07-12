use anyhow::{Result, Context};
use std::path::Path;

/// Async file operations utilities
pub struct FileUtils;

impl FileUtils {
    /// Create directory recursively if it doesn't exist
    pub async fn ensure_dir_exists<P: AsRef<Path>>(path: P) -> Result<()> {
        let path = path.as_ref();
        if !path.exists() {
            tokio::fs::create_dir_all(path).await
                .with_context(|| format!("Failed to create directory: {:?}", path))?;
        }
        Ok(())
    }

    /// Get file size
    pub async fn get_file_size<P: AsRef<Path>>(path: P) -> Result<u64> {
        let metadata = tokio::fs::metadata(path).await?;
        Ok(metadata.len())
    }

    /// Check if file exists
    pub async fn file_exists<P: AsRef<Path>>(path: P) -> bool {
        tokio::fs::metadata(path).await.is_ok()
    }

    /// Read file to string
    pub async fn read_to_string<P: AsRef<Path>>(path: P) -> Result<String> {
        tokio::fs::read_to_string(path).await
            .context("Failed to read file to string")
    }

    /// Write string to file
    pub async fn write_string<P: AsRef<Path>>(path: P, content: &str) -> Result<()> {
        tokio::fs::write(path, content).await
            .context("Failed to write string to file")
    }

    /// Copy file
    pub async fn copy_file<P: AsRef<Path>, Q: AsRef<Path>>(from: P, to: Q) -> Result<()> {
        tokio::fs::copy(from, to).await
            .context("Failed to copy file")?;
        Ok(())
    }

    /// Remove file
    pub async fn remove_file<P: AsRef<Path>>(path: P) -> Result<()> {
        tokio::fs::remove_file(path).await
            .context("Failed to remove file")
    }

    /// List directory contents
    pub async fn list_dir<P: AsRef<Path>>(path: P) -> Result<Vec<std::path::PathBuf>> {
        let mut entries = tokio::fs::read_dir(path).await?;
        let mut files = Vec::new();
        
        while let Some(entry) = entries.next_entry().await? {
            files.push(entry.path());
        }
        
        Ok(files)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[tokio::test]
    async fn test_ensure_dir_exists() {
        let temp_dir = tempdir().unwrap();
        let test_path = temp_dir.path().join("test").join("nested");
        
        assert!(!test_path.exists());
        FileUtils::ensure_dir_exists(&test_path).await.unwrap();
        assert!(test_path.exists());
    }

    #[tokio::test]
    async fn test_file_operations() {
        let temp_dir = tempdir().unwrap();
        let test_file = temp_dir.path().join("test.txt");
        let content = "Hello, World!";
        
        // Write and read
        FileUtils::write_string(&test_file, content).await.unwrap();
        assert!(FileUtils::file_exists(&test_file).await);
        
        let read_content = FileUtils::read_to_string(&test_file).await.unwrap();
        assert_eq!(content, read_content);
        
        // Get size
        let size = FileUtils::get_file_size(&test_file).await.unwrap();
        assert_eq!(size, content.len() as u64);
        
        // Remove
        FileUtils::remove_file(&test_file).await.unwrap();
        assert!(!FileUtils::file_exists(&test_file).await);
    }
}