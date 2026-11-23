import os

def create_synthetic_binaries(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # Common strings for DLMS and OBIS
    dlms_cosem_strings = b"DLMS Protocol handler initialized...\x00COSEM Application Layer\x00"
    obis_strings = b"OBIS mapped: 0.0.96.1.0.255\x00OBIS mapped: 1.0.1.8.0.255\x00"
    mbedtls_strings = b"mbedtls_ssl_handshake\x00MBEDTLS_CONFIG_FILE\x00mbed TLS 2.28.0\x00"

    # Variant 1: Security Suite 2 (AES-GCM + ECDSA)
    v1_crypto_strings = b"AES-GCM encryption enabled\x00Using ECDSA for signatures\x00secp256r1\x00"
    v1_content = dlms_cosem_strings + obis_strings + mbedtls_strings + v1_crypto_strings + (b"\x00" * 1024)
    v1_path = os.path.join(output_dir, "synthetic_dlms_variant1.bin")
    with open(v1_path, "wb") as f:
        f.write(v1_content)
    print(f"Created {v1_path}")

    # Variant 2: No Security Suite (Plaintext / Suite 0)
    # Exclude AES-GCM and ECDSA, but keep DLMS/COSEM and mbedtls just for YARA validation
    v2_content = dlms_cosem_strings + obis_strings + mbedtls_strings + (b"\x00" * 1024)
    v2_path = os.path.join(output_dir, "synthetic_dlms_variant2.bin")
    with open(v2_path, "wb") as f:
        f.write(v2_content)
    print(f"Created {v2_path}")

if __name__ == "__main__":
    fixtures_dir = os.path.dirname(os.path.abspath(__file__))
    create_synthetic_binaries(fixtures_dir)
