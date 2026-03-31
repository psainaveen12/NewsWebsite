# JSON Publishing

WordPress is already REST-enabled, so the operational work is mostly credentials and workflow setup.

## Recommended Auth Model

1. Create a dedicated automation user in WordPress.
2. Generate an Application Password in `Users > Profile`.
3. Store the credential outside Git.
4. Limit the user's capabilities to the minimum publishing scope you need.

## Primary Endpoints

- `/wp-json/wp/v2/posts`
- `/wp-json/wp/v2/media`
- `/wp-json/wp/v2/categories`
- `/wp-json/wp/v2/tags`

## Example Publish Request

```bash
curl --request POST \
  --url https://www.ieltstask.com/wp-json/wp/v2/posts \
  --user "automation_user:APPLICATION_PASSWORD" \
  --header "Content-Type: application/json" \
  --data '{
    "title": "IELTS Speaking Band 8 Guide",
    "content": "<p>Full article HTML here</p>",
    "status": "publish"
  }'
```

## Operational Notes

- Always use HTTPS.
- Use Application Passwords instead of sharing a real login password.
- Test create, read, edit, and media upload flows before relying on automation.
