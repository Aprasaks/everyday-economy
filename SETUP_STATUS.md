# Deployment status — 2026-11-03

## Verified complete
- Blogger settings and five policy/information pages configured separately in Blogger.
- Google Cloud project: everyday-economy (445838671801).
- Blogger API enabled.
- OAuth consent app: The Everyday Economy Publisher, External, Production.
- Desktop OAuth client: Everyday Economy Publisher - Initial Authorization.
- Consent scope https://www.googleapis.com/auth/blogger saved and verified after reload.
- Homepage and privacy policy point to https://everydayeconomybrief.blogspot.com/ and /p/privacy-policy.html; authorized domain everydayeconomybrief.blogspot.com saved and verified after reload.

## Not complete — publisher is NOT running
- OAuth client JSON download was requested; successful local download has not been verified. Do not create replacement credentials without checking the downloaded JSON first.
- Blogger OAuth authorization and refresh token are not installed.
- OpenAI API key and explicit text/image model choices are not configured.
- No always-on host or persistent image bucket has been selected or provisioned.
- No live end-to-end draft, image, scheduled publication, or reconciliation test has passed.
- PUBLISH_ENABLED must remain false until configuration and live verification are complete.

## Operating rules
- Asia/Seoul slots: 09:00 primary, 12:00 and 18:00 expansion.
- Independent U.S. English economics/living-cost blog; verify original sources.
- Use original generated images or assets with documented reuse rights. Do not copy newspaper photographs without permission.
- Never commit OAuth JSON, refresh tokens, API keys, credentials.env, or production .env. Supply secrets only through the selected host's secure secret configuration.
- Existing ChatGPT schedules were disabled; no new ChatGPT scheduled tasks were created for this publisher.
