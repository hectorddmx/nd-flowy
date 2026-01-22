# WorkFlowy API Keys

## Overview

WorkFlowy provides API keys for programmatic access to your account data. API keys are used for authentication when making requests to the WorkFlowy REST API.

## Getting Your API Key

1. Log in to your WorkFlowy account
2. Navigate to [beta.workflowy.com/api-key/](https://beta.workflowy.com/api-key/)
3. Your API key will be displayed (masked by default)
4. Click **Show** to reveal the full key
5. Click **Copy** to copy the key to your clipboard

## Important Notes

- **API keys do not expire** - Once generated, your key remains valid until deleted
- **Keep your key secret** - Do not share your API key with others, as it provides full access to your account
- **One key per account** - Each account has a single API key

## Using Your API Key

Include the API key in the `Authorization` header of your HTTP requests:

```
Authorization: Bearer YOUR_API_KEY
```

### Example Request

```bash
curl https://workflowy.com/api/v1/nodes-export \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Managing Your API Key

### Viewing Your Key

1. Go to [beta.workflowy.com/api-key/](https://beta.workflowy.com/api-key/)
2. Click **Show** to reveal the masked key

### Copying Your Key

1. Go to [beta.workflowy.com/api-key/](https://beta.workflowy.com/api-key/)
2. Click the **Copy** button to copy the key to your clipboard

### Deleting Your Key

If you need to revoke access or regenerate your key:

1. Go to [beta.workflowy.com/api-key/](https://beta.workflowy.com/api-key/)
2. Click **Delete API key**
3. A new key will be generated when you visit the page again

**Warning:** Deleting your API key will immediately invalidate any applications using the old key.

## Security Best Practices

- Store API keys in environment variables, not in code
- Never commit API keys to version control
- Use `.gitignore` to exclude files containing secrets
- Rotate keys periodically if you suspect they may have been compromised
- Use the minimum necessary permissions for your use case

## For This Project

This project expects the API key to be stored in `mise.local.toml`:

```toml
[env]
WF_API_KEY = "your-api-key-here"
```

The key is automatically loaded when using `mise exec --` commands.

## Support

For API-related issues, contact [support@workflowy.com](mailto:support@workflowy.com)

## See Also

- [WorkFlowy API Reference](./readme.md) - Full API documentation
- [About WorkFlowy](./about.md) - General information about WorkFlowy
