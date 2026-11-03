# The Everyday Economy — unattended publishing engine

Status: implementation and offline tests complete; NOT DEPLOYED OR AUTHENTICATED.
No live articles have been generated or published by this code. This package does
not enable ChatGPT scheduled tasks. Existing tasks remain disabled.

## Publication contract

- Blog: https://everydayeconomybrief.blogspot.com/
- Fixed Blogger blog ID: `4362239129084257609`.
- Audience: general U.S. readers; original American English.
- Publish: 09:00, 12:00 and 18:00 Asia/Seoul, every day.
- Preparation opens 60 minutes before each slot and closes 10 minutes before.
- Blogger receives a future `publishDate`; the worker does not need to wake at
  the exact publication second. No guarantee of uninterrupted service is made.
- One job per slot. No automatic backfill, endless paid retries or duplicate
  posting after ambiguous API writes. Maximum three generation attempts per day
  per durable database under normal scheduled operation.
- Durable state and artifacts are retained on the server volume. Never run a
  second independent deployment or replace the volume with an empty one.
- Failed evidence review, missing images, credentials, or missed preparation
  windows stop that article. Accuracy takes priority over filling a slot.

## What is implemented

1. Fetch all existing live, draft and scheduled Blogger posts.
2. Use OpenAI Responses web search to find an economic reader question, inspect
   current news and primary evidence, and write an original article.
3. Validate structure, source URLs, at least one U.S. government primary source,
   length, and exact normalized-question duplicates.
4. Run a separate web-enabled model review and require all source URLs verified.
5. Generate an original editorial illustration with an explicit AI caption.
6. Upload the illustration to configured S3-compatible storage, verify its public
   HTTPS URL, render escaped HTML, and save research and review artifacts.
7. Insert a draft, request future publication, and re-read status and timestamp.
8. After publication, re-fetch the public article to check the article marker
   and image URL. Emit a published URL only after that check.

News photos are deliberately excluded from this first implementation. A future
licensed-photo adapter must keep per-image rights evidence and attribution. A
newspaper URL alone is not permission. Generated images never pose as documentary
photographs. Statistical charts would require a separate exact-data renderer.

The summary is placed visibly at the start of the article. This implementation
does NOT claim to set Blogger's per-post search-description or custom permalink
through an unsupported API field. Blogger controls its generated URL.

## Connections needed to activate

1. **Execution host**: one persistent Docker host with outbound access to Google,
   OpenAI and your image object storage. No local Chrome session is needed.
   Cloud hosting must be selected and any charges approved before provisioning.
2. **AI access**: an OpenAI API project key and enabled text/image models. Select
   actual model IDs available in that project in `TEXT_MODEL` and `IMAGE_MODEL`.
   Account API billing and rate limits need to be confirmed; do not assume this
   program is funded by an existing ChatGPT subscription.
3. **Google/Blogger access**: enable Blogger API v3 in a Google Cloud project,
   configure OAuth consent and a Desktop client, and grant the owner's account
   the Blogger scope. A long-lived production OAuth setup is required: external
   apps left in Testing may have short-lived refresh tokens. Review current
   Google requirements before relying on unattended access. Store credentials
   only in host secrets, never chat or source control.
4. **Images**: an S3-compatible bucket plus a public HTTPS image origin. Limit the
   key to this illustration prefix and avoid granting access to unrelated files.
   The code does not change bucket public-access policies or create credentials.

These are configuration requirements, not completed connections.

## Local authentication handoff

The owner downloads the Desktop OAuth client JSON as `client_secret.json` into
this directory, installs requirements, and runs `python authorize_google.py` on
their own computer. It opens Google's consent screen and writes
`google_credentials.env` with mode 0600. The user completes consent themselves.
Do not send that file to ChatGPT. Copy its values directly into server secrets.
If it already exists the script refuses to overwrite it.

## Deployment sequence

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
cp .env.example .env
# Fill .env privately; keep PUBLISH_ENABLED=false for integration testing.
```

The application does not load `.env` itself. Docker Compose injects it. In a shell,
export environment values using the host's secret manager before CLI use.

```sh
docker compose build
docker compose run --rm publisher python publisher.py doctor
docker compose run --rm publisher python publisher.py once
docker compose run --rm publisher python publisher.py status
```

Run `once` during a preparation window to test research, review and image hosting
without Blogger mutation. A READY row is intentionally not automatically promoted
to publishing; use a new future slot for the live scheduling test. Once credentials,
model outputs, images and persistent storage pass integration testing, set
`PUBLISH_ENABLED=true` privately and run `docker compose up -d`.

Acceptance requires one actual SCHEDULED post with the correct timestamp, followed
by a verified public article and image at the intended time. Only after that is
the unattended pipeline operationally verified.

## Monitoring and recovery

`docker compose logs --tail=100 publisher` shows status and exception classes,
without logging provider payloads or tokens. `status` shows the latest job states.
No email/Slack notification channel is configured. Configure the chosen host's
container/uptime alerting before relying on daily unattended operation.

Keep encrypted backups of the durable data volume. Do not destroy it with
`docker compose down -v`. Artifacts include article text, research and review
responses, not API secrets. They are private working records.

If a job is BLOCKED, inspect its saved article/review. Do not delete its row and
rerun a slot blindly. If it is NEEDS_RECONCILIATION, inspect Blogger drafts and
scheduled posts using the saved ID/slot marker. The worker only reconciles remote
state; it never repeats an ambiguous insert or publication call. CLAIMED/WRITTEN/
READY jobs left by a crash need operator review; availability is traded for
duplicate prevention. Use supported Blogger tools to handle any orphan draft.

## Practical limits

An independent model review reduces risk but does not prove factual correctness.
Semantic duplicate detection is prompted, not a rigorous similarity classifier;
exact-question checks alone are not sufficient for long-term editorial quality.
No plagiarism detector, revenue promise, SEO ranking guarantee, automated legal
review or licensed-photo acquisition is included. Always inspect the first live
articles and sample ongoing output. No live provider call has been tested here
because credentials are absent. Dependencies need a resolved lock file and
integration testing on the selected host before production activation.

## Official references checked during implementation

- https://developers.google.com/blogger/docs/3.0/reference/posts/publish
- https://developers.google.com/blogger/docs/3.0/reference/posts
- https://developers.openai.com/api/docs/guides/tools-web-search
- https://developers.openai.com/api/docs/guides/image-generation

Prepared November 3, 2026. This is an independent global blog; no DECHIVE branding
or unrelated schedules are introduced by the code.
