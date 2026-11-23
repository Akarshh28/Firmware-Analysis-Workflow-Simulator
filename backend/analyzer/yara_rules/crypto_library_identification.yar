rule mbedTLS_Library_Identification
{
    meta:
        description = "Identifies mbedTLS / PolarSSL cryptographic library usage (Informational)"
        author = "FAWS Analyzer"
        severity = "info"
        category = "crypto_library"
    strings:
        $s1 = "mbedtls_" ascii wide nocase
        $s2 = "MBEDTLS_" ascii wide
        $s3 = "mbed TLS " ascii wide nocase
        $s4 = "PolarSSL" ascii wide nocase
        $s5 = "mbedtls_ssl_handshake" ascii wide
    condition:
        2 of them
}

rule wolfSSL_Library_Identification
{
    meta:
        description = "Identifies wolfSSL (formerly CyaSSL) cryptographic library usage (Informational)"
        author = "FAWS Analyzer"
        severity = "info"
        category = "crypto_library"
    strings:
        $s1 = "wolfSSL_" ascii wide
        $s2 = "WOLFSSL_" ascii wide
        $s3 = "CyaSSL_" ascii wide
        $s4 = "wolfCrypt" ascii wide nocase
        $s5 = "wolfssl_connect" ascii wide nocase
    condition:
        2 of them
}

rule OpenSSL_LibreSSL_Library_Identification
{
    meta:
        description = "Identifies OpenSSL or LibreSSL cryptographic library usage (Informational)"
        author = "FAWS Analyzer"
        severity = "info"
        category = "crypto_library"
    strings:
        $s1 = "OpenSSL 1." ascii wide
        $s2 = "OpenSSL 3." ascii wide
        $s3 = "LibreSSL " ascii wide
        $s4 = "ERR_load_crypto_strings" ascii wide
        $s5 = "SSL_CTX_new" ascii wide
    condition:
        1 of them
}

rule GnuTLS_Library_Identification
{
    meta:
        description = "Identifies GnuTLS cryptographic library usage (Informational)"
        author = "FAWS Analyzer"
        severity = "info"
        category = "crypto_library"
    strings:
        $s1 = "gnutls_" ascii wide
        $s2 = "GNUTLS_" ascii wide
        $s3 = "GnuTLS " ascii wide
    condition:
        1 of them
}
