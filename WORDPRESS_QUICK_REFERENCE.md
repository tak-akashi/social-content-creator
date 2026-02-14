# WordPress Playwright Integration - Quick Reference

## TL;DR - Code Snippets

### 1. Get Nonce for Cookie-Authenticated REST API
```javascript
const nonce = await page.evaluate(async () => {
  const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
  return await resp.text();
});
```

### 2. POST to REST API with Cookie Auth
```javascript
const resp = await page.evaluate(async ({nonce, data}) => {
  const resp = await fetch('/wp-json/wp/v2/pages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-WP-Nonce': nonce
    },
    body: JSON.stringify(data)
  });
  return { status: resp.status, data: await resp.json() };
}, {nonce, data});
```

### 3. Extract Plugin Install URLs
```javascript
const buttons = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.install-now')).map(b => ({
    href: b.href,
    slug: b.dataset.slug
  }));
});
```

### 4. Install and Activate Plugin
```javascript
// Click install button
await page.locator('button.install-now').first().click();

// Wait for activation button
await page.locator('a.activate-now').first().waitFor({ timeout: 30000 });

// Click activate
await page.locator('a.activate-now').first().click();
```

### 5. Update Navigation Links
```javascript
const nonce = await page.evaluate(async () => {
  const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
  return await resp.text();
});

const navContent = `<!-- wp:navigation-link {"label":"Home","url":"https://example.com/","kind":"custom"} /-->`;

await page.evaluate(async ({nonce, content}) => {
  const resp = await fetch('/wp-json/wp/v2/navigation/4', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-WP-Nonce': nonce
    },
    body: JSON.stringify({ content })
  });
  return resp.status;
}, {nonce, content: navContent});
```

---

## Key URLs by Task

| Task | URL |
|------|-----|
| Plugin Install | `/wp-admin/plugin-install.php?s=SLUG&tab=search&type=term` |
| Settings | `/wp-admin/options-general.php` |
| Reading Settings | `/wp-admin/options-reading.php` |
| Pages List | `/wp-admin/edit.php?post_type=page` |
| App Passwords | `/wp-admin/user-edit.php` |
| Site Editor | `/wp-admin/site-editor.php` |
| Navigation Editor | `/wp-admin/site-editor.php?p=%2Fnavigation` |

---

## Authentication Methods

### Cookie + Nonce (Recommended for Playwright)
```javascript
// In page.evaluate context (has cookies)
const nonce = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce').then(r => r.text());
fetch('/wp-json/wp/v2/pages', {
  headers: { 'X-WP-Nonce': nonce }
})
```

### Basic Auth (External Scripts)
```bash
curl -u "username:app_password" https://domain.com/wp-json/wp/v2/pages
```

### Never Mix
- Login password: ONLY for `/wp-login.php` and wp-admin form
- App password: ONLY for REST API
- They are different and not interchangeable

---

## Common Patterns

### Loop Through REST API Data
```javascript
const nonce = await page.evaluate(async () => {
  const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
  return await resp.text();
});

for (const item of items) {
  const result = await page.evaluate(async ({nonce, item}) => {
    const resp = await fetch('/wp-json/wp/v2/categories', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': nonce
      },
      body: JSON.stringify(item)
    });
    return { status: resp.status, data: await resp.json() };
  }, {nonce, item});

  console.log(result);
}
```

### Extract and Navigate to Install URL
```javascript
const buttons = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.install-now'))
    .map(b => b.href);
});

if (buttons.length > 0) {
  await page.goto(buttons[0]);
  await page.waitForLoadState('networkidle');
}
```

### Safe Plugin Activation
```javascript
try {
  await page.locator('a.activate-now').first().waitFor({ timeout: 30000 });
  await page.locator('a.activate-now').first().click();
  console.log('✓ Activated');
} catch(e) {
  console.log('✗ Already activated or not found');
}
```

---

## WordPress Data Structures

### Navigation Link Block Format
```javascript
// Single link
`<!-- wp:navigation-link {
  "label": "Link Text",
  "url": "https://domain.com/path/",
  "kind": "custom"
} /-->`

// Multiple links (order matters)
`<!-- wp:navigation-link {...} /-->
<!-- wp:navigation-link {...} /-->
<!-- wp:navigation-link {...} /-->`
```

### Page/Post Body Structure (REST API)
```json
{
  "title": "Page Title",
  "slug": "page-slug",
  "status": "publish",
  "content": "HTML content here"
}
```

### Category Body Structure
```json
{
  "name": "Category Name",
  "slug": "category-slug",
  "description": "Category description"
}
```

---

## Selectors and Attributes

| Element | Selector | Notes |
|---------|----------|-------|
| Plugin Install Button | `.install-now` or `button.install-now` | Has `data-slug`, `data-name` |
| Plugin Activate Link | `.activate-now` or `a.activate-now` | Appears after install completes |
| Text Matcher | `:has-text("text")` | Use with locator() |
| All Install URLs | `document.querySelectorAll('.install-now')` | Returns NodeList, access via `.href` |

---

## Debugging Tips

### Verify Nonce Works
```javascript
const nonce = await page.evaluate(async () => {
  const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
  return await resp.text();
});
console.log('Nonce length:', nonce.length); // Should be 10+ chars
```

### Check Plugin Installation Status
```javascript
const status = await page.evaluate(() => {
  const btn = document.querySelector('.activate-now');
  return btn ? 'Ready to activate' : 'Installing or unknown';
});
```

### Verify REST API Endpoint
```javascript
const test = await page.evaluate(async ({nonce}) => {
  const resp = await fetch('/wp-json/wp/v2/categories?per_page=1', {
    headers: { 'X-WP-Nonce': nonce }
  });
  return { status: resp.status, count: (await resp.json()).length };
}, {nonce});
```

---

## Gotchas Checklist

- [ ] Browser size at 1280x900 before large snapshots
- [ ] Using app password, NOT login password for REST API
- [ ] Getting nonce from `/wp-admin/admin-ajax.php?action=rest-nonce`
- [ ] All REST API calls use `'X-WP-Nonce'` header
- [ ] Navigation block content uses `<!-- wp:navigation-link {...} />` format
- [ ] Plugin install button uses `.install-now` class (CSS)
- [ ] Activation button uses `.activate-now` class
- [ ] Wait for page states with `waitForLoadState('networkidle')`
- [ ] WORDPRESS_URL should be domain root, not `/wp-admin/...`
- [ ] Use `page.evaluate` for all fetch calls (maintains cookies)

---

## Environment Setup

```bash
# .env configuration for REST API
WORDPRESS_URL=https://www.aidotters.com
WORDPRESS_USER=akatak
WORDPRESS_APP_PASSWORD=Hyq5 DPKm E2ux yvPv Whb7 vVlG

# NOT this:
WORDPRESS_URL=https://www.aidotters.com/wp-admin/index.php
WORDPRESS_APP_PASSWORD=your_login_password_here
```

---

## Session Persistence

Playwright maintains WordPress session cookies automatically, so:

1. Login once via UI or programmatically
2. All subsequent `page.evaluate` calls have authenticated cookies
3. Can immediately use REST API with nonce
4. No re-login needed within same browser session

