# Gerar certificados SSL para Windows
$cert = New-SelfSignedCertificate -DnsName "localhost", "127.0.0.1" -CertStoreLocation "cert:\LocalMachine\My" -NotAfter (Get-Date).AddYears(1)

# Exportar certificado
$certPath = "nginx\ssl\cert.pem"
$keyPath = "nginx\ssl\key.pem"

# Exportar certificado público
Export-Certificate -Cert $cert -FilePath "nginx\ssl\cert.crt" -Type CERT
certutil -encode "nginx\ssl\cert.crt" $certPath

# Exportar chave privada
$keyBytes = $cert.PrivateKey.Key.Export([System.Security.Cryptography.CngKeyBlobFormat]::Pkcs8PrivateBlob)
[System.IO.File]::WriteAllBytes("nginx\ssl\key.der", $keyBytes)
certutil -encode "nginx\ssl\key.der" $keyPath

Write-Host "Certificados SSL gerados com sucesso!"