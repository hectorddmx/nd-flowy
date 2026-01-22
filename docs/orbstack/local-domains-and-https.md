# OrbStack Local Domains and HTTPS

OrbStack automatically provides local domain names and HTTPS for all containers with zero configuration.

## Local Domain Names

Every container gets a `.orb.local` domain automatically:

| Container Type | Domain Pattern |
|----------------|----------------|
| Single container | `container-name.orb.local` |
| Docker Compose | `service.project.orb.local` |
| Linux machines | `machine-name.orb.local` |

### Examples

```
# Dev container named "musing_boyd"
https://musing_boyd.orb.local

# Compose service "app" in project "myproject"
https://app.myproject.orb.local
```

### No Port Numbers Required

OrbStack automatically detects web server ports, so you don't need to remember `localhost:8000`. Just use the domain name.

### Wildcard Subdomains

Default domains work as wildcards - `*.container.orb.local` resolves to the container automatically.

## Automatic HTTPS

OrbStack provides secure HTTPS for all container domains with:

- **Automatic certificate generation** - No manual setup required
- **Local CA** - Certificates are trusted by your Mac automatically
- **Reverse proxy** - Handles TLS termination transparently

### First-Time Setup

1. Visit [https://orb.local](https://orb.local) in your browser
2. OrbStack will prompt to install the root certificate
3. Accept the prompt - this is a one-time setup
4. All `.orb.local` domains now work with HTTPS

### Security

OrbStack's implementation is secure:

- Root CA private key is stored encrypted in macOS Keychain
- Access is restricted to OrbStack via code signatures
- Keys are only decrypted temporarily when needed
- More secure than tools like `mkcert` that store unencrypted keys

## Custom Domains

Add custom domains using Docker labels:

```bash
# Command line
docker run --rm -l dev.orbstack.domains=myapp.local nginx

# docker-compose.yml
services:
  app:
    labels:
      - dev.orbstack.domains=myapp.local,api.local
```

Wildcard domains are supported: `*.myapp.local`

## Useful Labels

| Label | Purpose |
|-------|---------|
| `dev.orbstack.domains` | Custom domain names (comma-separated) |
| `dev.orbstack.http-port` | Override auto-detected HTTP port |
| `dev.orbstack.https-port` | Override auto-detected HTTPS port |
| `dev.orbstack.add-ca-certificates` | Set to `false` to disable CA injection |

## Container Index

Visit [https://orb.local](https://orb.local) to see links to all running containers.

## Firefox Users

Firefox 119 and earlier ignores macOS system certificates by default. To fix:

1. Open `about:config`
2. Set `security.enterprise_roots.enabled` to `true`
3. No restart required

## Troubleshooting

### Domains not resolving

Ensure "Direct IP access" is enabled in OrbStack Settings → Network.

### Container-to-container HTTPS

Containers can communicate via `.orb.local` domains. OrbStack automatically injects the root CA certificate into containers.

## References

- [Container Domain Names - OrbStack Docs](https://docs.orbstack.dev/docker/domains)
- [HTTPS for Containers - OrbStack Docs](https://docs.orbstack.dev/features/https)
- [Container Networking - OrbStack Docs](https://docs.orbstack.dev/docker/network)
