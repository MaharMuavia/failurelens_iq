# No Secrets Policy

Do not commit secrets.

Never commit:

- `.env`
- Azure keys or connection strings
- OpenAI API keys
- SAS tokens
- Private certificates
- Exported cloud credentials
- Production API keys

Use these templates instead:

- `.env.demo`
- `.env.example`
- `.env.azure.example`

CI checks that `.env` is not committed. Review diffs before pushing.
