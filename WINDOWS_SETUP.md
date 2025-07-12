# 🪟 Windows Setup Guide for MiraC2

This guide helps fix common Windows build issues when compiling the Rust components of MiraC2.

## 🔴 Common Issue: dlltool.exe Error

If you encounter this error when running `cargo run --bin mira-server`:
```
error: Error calling dlltool 'dlltool.exe': program not found
error: could not compile `getrandom` (lib) due to 1 previous error
```

## 💡 Solutions

### Option 1: Use MSVC Toolchain (Recommended)

1. **Install Visual Studio Build Tools**
   ```bash
   # Download and install Visual Studio Build Tools
   # https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
   ```

2. **Set Rust to use MSVC**
   ```bash
   rustup default stable-msvc
   ```

3. **Clean and rebuild**
   ```bash
   cargo clean
   cargo build --release
   ```

### Option 2: Fix GNU Toolchain

If you prefer to use the GNU toolchain:

1. **Install MinGW-w64**
   ```bash
   # Using Chocolatey
   choco install mingw

   # Or download from: https://www.mingw-w64.org/downloads/
   ```

2. **Add MinGW to PATH**
   - Add `C:\mingw64\bin` to your system PATH
   - Ensure `dlltool.exe` is available: `where dlltool`

3. **Set environment variable**
   ```bash
   set CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER=gcc
   ```

### Option 3: Switch Target

Use the MSVC target explicitly:
```bash
cargo build --target x86_64-pc-windows-msvc --release
```

## 🚀 Running MiraC2 on Windows

After fixing the build issue:

1. **Start Rust Server**
   ```bash
   cargo run --bin mira-server
   ```

2. **Start Python GUI** (in separate terminal)
   ```bash
   cd python-gui
   pip install -r requirements.txt
   python main.py
   ```

## 🔧 Verification

Test that everything works:
```bash
# Check Rust toolchain
rustc --version
cargo --version

# Test compilation
cargo check

# Test running
cargo run --bin mira-server --help
```

## 📋 Additional Notes

- The MSVC toolchain is generally more stable on Windows
- Ensure you have the latest Rust version: `rustup update`
- If issues persist, try: `cargo clean && cargo update`

## 🆘 Still Having Issues?

1. Check your Rust installation: `rustup show`
2. Verify toolchain: `rustup toolchain list`
3. Update everything: `rustup update && cargo update`
4. Clear registry: `cargo clean`

For more help, check the [Rust Windows documentation](https://forge.rust-lang.org/infra/channel-layout.html#windows).