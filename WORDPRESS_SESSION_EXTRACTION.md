# WordPress Setup Session - Technical Extraction

Extracted from session: `3897767d-6172-4129-bd4e-2b1aaa7ee2c8`

## 1. Cookie-Authenticated REST API Calls via page.evaluate

### Pattern for Getting Nonces

```javascript
// Get nonce from wp-admin/admin-ajax.php
const nonce = await page.evaluate(async () => {
  const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
  return await resp.text();
});
```

### Pattern for Making REST API Calls with Cookie Auth

```javascript
// Using the nonce in X-WP-Nonce header for authenticated requests
const result = await page.evaluate(async ({nonce, data}) => {
  const resp = await fetch('/wp-json/wp/v2/pages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-WP-Nonce': nonce
    },
    body: JSON.stringify(data)
  });
  return { status: resp.status, data: await resp.json() };
}, {nonce, newData});
```

### Complete Example: Creating Multiple Pages via REST API

```javascript
async (page) => {
  const pages = [
    { title: "ホーム", slug: "home", content: "Home content" },
    { title: "会社概要", slug: "about", content: "About content" },
    // ... more pages
  ];

  // Get nonce first
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  const results = [];
  for (const p of pages) {
    // POST each page with nonce authentication
    const resp = await page.evaluate(async ({pageData, nonce}) => {
      const resp = await fetch('/wp-json/wp/v2/pages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-WP-Nonce': nonce
        },
        body: JSON.stringify({
          title: pageData.title,
          slug: pageData.slug,
          status: 'publish',
          content: pageData.content
        })
      });
      return { status: resp.status, data: await resp.json() };
    }, {pageData: p, nonce});

    if (resp.status === 201) {
      results.push(`✓ ${p.title}: ID=${resp.data.id}`);
    } else {
      results.push(`✗ ${p.title}: ${resp.status}`);
    }
  }
  return results.join('\n');
}
```

### Key Points on Nonce Authentication
- Endpoint: `/wp-admin/admin-ajax.php?action=rest-nonce`
- Returns plain text nonce string
- Used in header: `'X-WP-Nonce': nonce`
- This enables cookie-based authenticated REST API calls from page.evaluate
- Works because Playwright maintains WordPress session cookies

---

## 2. Plugin Installation via page.evaluate

### Pattern for Getting Plugin Install URLs from DOM

```javascript
async (page) => {
  // Navigate to plugin search results
  await page.goto('https://www.aidotters.com/wp-admin/plugin-install.php?s=wordpress-seo&tab=search&type=term');
  await page.waitForLoadState('networkidle');

  // Extract install URLs from .install-now buttons
  const buttons = await page.evaluate(() => {
    const btns = document.querySelectorAll('.install-now');
    return Array.from(btns).map(b => ({
      text: b.textContent.trim(),
      href: b.href,
      slug: b.dataset.slug,
      name: b.dataset.name
    }));
  });

  return buttons;
}
```

### Pattern for Installing and Activating Plugins

```javascript
async (page) => {
  const plugins = [
    { slug: 'wordpress-seo', name: 'Yoast SEO' },
    { slug: 'contact-form-7', name: 'Contact Form 7' }
  ];

  const results = [];

  for (const plugin of plugins) {
    // Step 1: Navigate to plugin search
    await page.goto(`https://www.aidotters.com/wp-admin/plugin-install.php?s=${plugin.slug}&tab=search&type=term`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Step 2: Click install button
    const installBtn = page.locator('button.install-now').first();
    if (await installBtn.count() > 0) {
      await installBtn.click();

      // Step 3: Wait for activation button to appear
      try {
        await page.locator('a.activate-now').first().waitFor({ timeout: 30000 });

        // Step 4: Click activation button
        await page.locator('a.activate-now').first().click();
        await page.waitForLoadState('networkidle');

        results.push(`✓ ${plugin.name}: Install & Activate Complete`);
      } catch(e) {
        results.push(`△ ${plugin.name}: Installed (manual activation needed)`);
      }
    } else {
      results.push(`- ${plugin.name}: Already installed`);
    }
  }

  return results.join('\n');
}
```

### Alternative: Direct Navigation with Nonce

```javascript
async (page) => {
  // Extract .install-now buttons and get nonce
  const buttons = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.install-now')).map(b => ({
      href: b.href,
      slug: b.dataset.slug
    }));
  });

  // Navigate directly to install URL
  if (buttons.length > 0) {
    const installUrl = buttons[0].href;
    await page.goto(installUrl);
    await page.waitForLoadState('networkidle');

    // Click activate link if it appears
    const activateLink = page.locator('a:has-text("プラグインを有効化")');
    if (await activateLink.count() > 0) {
      await activateLink.click();
    }
  }
}
```

### Key Patterns
- Plugin search: `plugin-install.php?s=PLUGIN_SLUG&tab=search&type=term`
- Install button class: `.install-now`
- Button HTML attributes: `data-slug`, `data-name`
- Activate button class: `.activate-now`
- DOM selector for text: `a:has-text("プラグインを有効化")`
- Wait for activation UI: `page.locator('a.activate-now').first().waitFor({ timeout: 30000 })`

---

## 3. Navigation Block Editing via REST API

### Pattern for Getting Navigation Blocks

```javascript
async (page) => {
  // Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  // Fetch navigation blocks
  const navResult = await page.evaluate(async ({nonce}) => {
    const resp = await fetch('/wp-json/wp/v2/navigation?per_page=100', {
      headers: { 'X-WP-Nonce': nonce }
    });
    const data = await resp.json();
    return data.map(n => ({
      id: n.id,
      title: n.title.raw,
      content: n.content.raw
    }));
  }, {nonce});

  return JSON.stringify(navResult, null, 2);
}
```

### Pattern for Updating Navigation Block Content

```javascript
async (page) => {
  // Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  // Create navigation links as WordPress blocks
  const newContent = `<!-- wp:navigation-link {"label":"ホーム","url":"https://www.aidotters.com/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"会社概要","url":"https://www.aidotters.com/about/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"サービス","url":"https://www.aidotters.com/services/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"ブログ","url":"https://www.aidotters.com/blog/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"お問い合わせ","url":"https://www.aidotters.com/contact/","kind":"custom"} /-->`;

  // Update navigation
  const result = await page.evaluate(async ({nonce, newContent}) => {
    const resp = await fetch('/wp-json/wp/v2/navigation/4', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': nonce
      },
      body: JSON.stringify({ content: newContent })
    });
    return { status: resp.status, ok: resp.ok };
  }, {nonce, newContent});

  return JSON.stringify(result);
}
```

### Navigation Block Format
- WordPress navigation blocks use HTML comments: `<!-- wp:navigation-link {...} /-->`
- Each link requires: `label` (display text), `url`, `kind: "custom"`
- To reorder: Update content with links in desired order
- Endpoint: `/wp-json/wp/v2/navigation/{ID}`
- Method: `POST` with `X-WP-Nonce` header

---

## 4. WordPress Admin Selectors and Patterns

### Common Admin Page URLs
```
/wp-admin/ - Dashboard
/wp-admin/options-general.php - General Settings
/wp-admin/options-reading.php - Reading Settings (Front Page Display)
/wp-admin/edit.php - Posts List
/wp-admin/edit.php?post_type=page - Pages List
/wp-admin/edit.php?post_type=category - Categories
/wp-admin/plugin-install.php - Install Plugins
/wp-admin/plugins.php - Manage Plugins
/wp-admin/site-editor.php - Full Site Editor
/wp-admin/site-editor.php?p=%2Fnavigation - Navigation Block Editor
/wp-admin/user-edit.php - User Profile (App Passwords)
```

### Common Admin Form Selectors

#### Plugin Installation
- Search input: `input[name="s"]`
- Install button: `button.install-now`
- Button attributes: `data-slug`, `data-name`
- Activation link: `a.activate-now`

#### Settings Forms
- Using fill_form tool with combobox for dropdowns:
  ```javascript
  {
    "fields": [
      { "name": "ホームページ", "type": "combobox", "ref": "e170", "value": "ホーム" },
      { "name": "投稿ページ", "type": "combobox", "ref": "e173", "value": "ブログ" }
    ]
  }
  ```

#### Trash/Delete Actions
- Post trash URL pattern: `/wp-admin/post.php?post={ID}&action=trash&_wpnonce={NONCE}`
- Page trash URL pattern: Same as above
- Comment delete: Navigate to edit-comments.php

#### Menu Item Text Matching
- Use locator: `page.locator('a:has-text("プラグインを有効化")')`
- Or button text: `page.locator('button:has-text("今すぐインストール")')`

### WordPress-Specific Data Attributes
- Plugin slug: `.data-slug`
- Plugin name: `.data-name`
- Install links use nonce: `update.php?action=install-plugin&plugin={SLUG}&_wpnonce={NONCE}`

---

## 5. Application Password Creation

### Pattern for Creating Application Passwords

1. **Navigate to User Profile**
   ```
   /wp-admin/user-edit.php (or /wp-admin/user-edit.php?user_id=1)
   ```

2. **Find Application Passwords Section**
   ```javascript
   // Application Passwords section is typically shown in user profile
   // Look for "New Application Password" input
   // Usually requires entering an app name (e.g., "REST API")
   ```

3. **Generate Password**
   ```javascript
   // Fill in the application name input
   // Click generate button
   // WordPress displays: "Hyq5 DPKm E2ux yvPv Whb7 vVlG" (space-separated format)
   ```

4. **Retrieve Password**
   - Password format: Space-separated 4-character segments (e.g., "Hyq5 DPKm E2ux yvPv Whb7 vVlG")
   - Only displayed once at creation - must be copied immediately
   - Different from login password
   - Used for Basic Auth in REST API: `base64_encode("username:app_password")`

### Key Differences: App Password vs Login Password
- **Login Password**: Used for wp-admin interface (`/wp-login.php`)
- **Application Password**: Used for REST API calls, cannot login to wp-admin
- **REST API Auth**: Basic Auth with `Authorization: Basic {base64(user:app_password)}`

---

## 6. Gotchas and Workarounds Discovered

### Browser Sizing Issues
**Problem**: Large WordPress admin pages causing DOM parsing issues
**Solution**: Resize browser to 1280x900 or larger before taking snapshots
```javascript
// In Playwright:
await browser_resize(1280, 900);
```
**Why**: Snapshot files become very large (100KB+) when viewport is too small
**Impact**: Affects ability to parse page structure with Grep patterns

### Large Snapshot Files
**Problem**: `browser_snapshot` can return massive files (>100KB)
**Solution 1**: Use `page.evaluate` to extract specific DOM elements instead of full snapshot
```javascript
// Instead of relying on full snapshot, extract directly:
const buttons = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.install-now'))
    .map(b => ({ href: b.href, slug: b.dataset.slug }));
});
```

**Solution 2**: Parse snapshot output with grep for specific patterns
```bash
grep "install.*ref=" snapshot.txt | head -5
```

### Application Password Permissions Issue
**Problem**: Some app passwords had insufficient permissions (401 errors on REST API)
**Root Cause**: App password created with limited scope, or using login password instead of app password
**Solution**: Create fresh app password in user profile specifically for REST API
- Ensure you're using the generated **app password**, not the login password
- App password format: Space-separated, e.g., "Hyq5 DPKm E2ux yvPv Whb7 vVlG"
- Login password does NOT work for REST API, only for wp-admin

### Plugin Installation Button Locating
**Problem**: Plugin search results render all content in single long line, hard to find button
**Solution**: Use `page.evaluate` to extract button attributes from DOM
```javascript
await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.install-now'))
    .map(b => ({ href: b.href, slug: b.dataset.slug, name: b.dataset.name }));
});
```

### Navigation Wait for Activation
**Problem**: Plugin activation click doesn't always navigate, times out
**Solution**: Use `page.waitForFunction` instead of `page.waitForLoadState`
```javascript
// Wait for activation button to appear on current page
await page.waitForFunction(() => {
  const btn = document.querySelector('.activate-now');
  return btn && btn.classList.contains('activate-now');
}, { timeout: 30000 });
```

### Direct URL for Plugin Installation
**Problem**: Clicking install button sometimes fails or doesn't navigate predictably
**Solution**: Extract install URL and navigate directly
```javascript
// Extract from button href
const installUrl = button.href;  // Already includes nonce
await page.goto(installUrl);
await page.waitForLoadState('networkidle');
```
**Note**: Nonce is embedded in href, so no need to extract separately

### Cookie Authentication for REST API
**Problem**: Can't use Basic Auth in Browser (doesn't have password available)
**Solution**: Use cookie authentication via page.evaluate with nonce
```javascript
// Get nonce from admin-ajax.php
const nonce = await page.evaluate(async () => {
  const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
  return await resp.text();
});

// Use nonce in subsequent requests
headers: { 'X-WP-Nonce': nonce }
```
**Key**: This works because Playwright maintains logged-in session cookies

### Timeout Handling for Long Operations
**Problem**: Page navigation during plugin installation can timeout
**Solution 1**: Increase timeout on waitForLoadState
```javascript
await page.waitForLoadState('networkidle', { timeout: 60000 });
```

**Solution 2**: Use waitForTimeout to add explicit delays
```javascript
await page.waitForTimeout(3000);  // Wait 3 seconds
```

**Solution 3**: Catch timeout errors gracefully
```javascript
try {
  await page.locator('a.activate-now').first().waitFor({ timeout: 30000 });
  // Click it
} catch(e) {
  // Already installed or activation optional
}
```

### Environment Variable Setup
**Problem**: WORDPRESS_URL had wrong path (included `/wp-admin/index.php`)
**Solution**: Use base domain only for REST API
```
# Correct
WORDPRESS_URL=https://www.aidotters.com

# Incorrect
WORDPRESS_URL=https://www.aidotters.com/wp-admin/index.php
```
**Impact**: REST API endpoint must be at domain root: `/wp-json/wp/v2`

### Navigation Menu Reordering
**Problem**: Drag-and-drop in site editor is difficult with Playwright
**Solution**: Edit navigation content directly via REST API
```javascript
// Instead of dragging, update content with links in desired order
const newContent = `<!-- wp:navigation-link {...} /-->
<!-- wp:navigation-link {...} /-->`;
await fetch('/wp-json/wp/v2/navigation/4', {
  method: 'POST',
  headers: { 'X-WP-Nonce': nonce },
  body: JSON.stringify({ content: newContent })
});
```

---

## 7. Complete Workflow Example: End-to-End Setup

```javascript
// Task: Create pages, setup navigation, and categories via REST API

async (page) => {
  // Step 1: Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  // Step 2: Create pages
  const pages = [
    { title: "ホーム", slug: "home", content: "Home" },
    { title: "ブログ", slug: "blog", content: "" }
  ];

  for (const page of pages) {
    await page.evaluate(async ({p, nonce}) => {
      const resp = await fetch('/wp-json/wp/v2/pages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-WP-Nonce': nonce
        },
        body: JSON.stringify({
          title: p.title,
          slug: p.slug,
          status: 'publish',
          content: p.content
        })
      });
      return resp.json();
    }, {p: page, nonce});
  }

  // Step 3: Create categories
  const categories = [
    { name: "AI技術", slug: "ai-technology" },
    { name: "開発Tips", slug: "dev-tips" }
  ];

  for (const cat of categories) {
    await page.evaluate(async ({c, nonce}) => {
      const resp = await fetch('/wp-json/wp/v2/categories', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-WP-Nonce': nonce
        },
        body: JSON.stringify(c)
      });
      return resp.json();
    }, {c: cat, nonce});
  }

  // Step 4: Update navigation
  const navContent = `<!-- wp:navigation-link {"label":"ホーム","url":"https://domain.com/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"ブログ","url":"https://domain.com/blog/","kind":"custom"} /-->`;

  await page.evaluate(async ({nonce, content}) => {
    const resp = await fetch('/wp-json/wp/v2/navigation/4', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': nonce
      },
      body: JSON.stringify({ content })
    });
    return resp.json();
  }, {nonce, content: navContent});

  return "Setup complete";
}
```

---

## 8. REST API Endpoints Used

### Categories
```
GET  /wp-json/wp/v2/categories
POST /wp-json/wp/v2/categories
POST /wp-json/wp/v2/categories/{ID}
```

### Pages
```
GET  /wp-json/wp/v2/pages
POST /wp-json/wp/v2/pages
```

### Navigation (Block)
```
GET  /wp-json/wp/v2/navigation
GET  /wp-json/wp/v2/navigation/{ID}?context=edit
POST /wp-json/wp/v2/navigation/{ID}
```

### Nonce (for cookie auth)
```
GET  /wp-admin/admin-ajax.php?action=rest-nonce
```

### All endpoints require
- Header: `'X-WP-Nonce': {nonce_value}`
- Cookie: Automatically maintained by Playwright session
- No Basic Auth needed when using cookie auth + nonce

