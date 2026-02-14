# WordPress + Playwright Integration Architecture

## Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   WORDPRESS SESSION LIFECYCLE                    │
└─────────────────────────────────────────────────────────────────┘

Step 1: Initial Login
┌──────────────────────┐
│  WordPress Login     │
│  /wp-login.php       │
└──────┬───────────────┘
       │ Username + Password
       ▼
┌──────────────────────────────────────────────────────┐
│ WordPress creates session cookie (wp_logged_in_...)  │
│ Playwright maintains this cookie automatically       │
└──────────────────────────────────────────────────────┘

Step 2: REST API via page.evaluate (Cookie Auth)
┌──────────────────────────────────────────────┐
│ page.evaluate(async () => {                 │
│   fetch('/wp-admin/admin-ajax.php?          │
│          action=rest-nonce')                │
│     .then(r => r.text())                    │
│ })                                          │
└──────────────────────┬───────────────────────┘
                       │ Request has:
                       │ - Cookie: wp_logged_in_...
                       │ - Origin: localhost
                       ▼
┌──────────────────────────────────────────────┐
│ WordPress validates cookie + CSRF check      │
│ Returns nonce: "a1b2c3d4e5"                 │
└──────────────────────────────────────────────┘

Step 3: All REST API Calls (with Nonce)
┌──────────────────────────────────────────────────────┐
│ page.evaluate(async ({nonce}) => {                  │
│   fetch('/wp-json/wp/v2/pages', {                  │
│     method: 'POST',                                │
│     headers: {                                     │
│       'X-WP-Nonce': nonce,                        │
│       'Content-Type': 'application/json'          │
│     },                                            │
│     body: JSON.stringify(data)                    │
│   })                                              │
│ })                                                │
└──────────────────┬───────────────────────────────┘
                   │ Request has:
                   │ - Cookie: wp_logged_in_...
                   │ - Header: X-WP-Nonce: a1b2c...
                   │ - Body: JSON data
                   ▼
┌──────────────────────────────────────────────┐
│ WordPress validates nonce + cookie           │
│ Performs requested action (create page, etc) │
│ Returns 201 Created + JSON response          │
└──────────────────────────────────────────────┘

Key: Cookie-based auth + Nonce CSRF protection
     = Secure, cookie-persistent REST API calls
```

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLAYWRIGHT LAYER                           │
│  (Browser automation + Session management)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐        ┌──────────────────┐              │
│  │ page.navigate   │        │ page.evaluate()  │              │
│  │ wp-login.php    │        │ fetch() calls    │              │
│  │ + fill/submit   │        │ page.evaluate    │              │
│  │                 │        │ DOM extraction   │              │
│  └────────┬────────┘        └──────────┬───────┘              │
│           │                            │                      │
│           │ Login success              │ Nonce + Auth         │
│           ▼                            ▼                      │
│  ┌───────────────────────────────────────────────┐           │
│  │  Browser Cookie Storage                       │           │
│  │  wp_logged_in_abc123... = session_token       │           │
│  │  wordpress_logged_in_... = user info          │           │
│  └───────────────────────────────────────────────┘           │
│                         ▲                                     │
└─────────────────────────┼─────────────────────────────────────┘
                          │ Cookies sent
                          │ with all requests
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│                         ▼                                     │
│              WORDPRESS REST API LAYER                         │
│              (/wp-json/wp/v2/*)                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Authentication Check:                                      │
│  1. Validate cookie (user logged in?)                      │
│  2. Validate nonce (CSRF protection)                       │
│  3. Check user capabilities                                │
│                                                              │
│  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌────────┐      │
│  │  Pages   │  │Category │  │Navigation│  │ Posts  │      │
│  │ /pages   │  │ /cat... │  │ /nav...  │  │/posts  │      │
│  └──────────┘  └─────────┘  └──────────┘  └────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Database: wp_posts, wp_terms, wp_postmeta, etc       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Creating Pages

```
START: Create 5 Pages
│
├─> Get Nonce
│   fetch('/wp-admin/admin-ajax.php?action=rest-nonce')
│   └─> Response: "a1b2c3d4e5f6" (10 char token)
│
├─> For Each Page {
│   │
│   ├─> Prepare payload:
│   │   {
│   │     "title": "ホーム",
│   │     "slug": "home",
│   │     "status": "publish",
│   │     "content": "HTML content"
│   │   }
│   │
│   ├─> POST /wp-json/wp/v2/pages
│   │   Headers:
│   │     'X-WP-Nonce': 'a1b2c3d4e5f6'
│   │     'Content-Type': 'application/json'
│   │     Cookie: wp_logged_in_... (auto)
│   │
│   ├─> WordPress Processing:
│   │   1. Validate cookie (is user logged in?)
│   │   2. Validate nonce (CSRF token matches?)
│   │   3. Check capability (can user edit pages?)
│   │   4. INSERT into wp_posts table
│   │   5. Return 201 + {id: 5, link: "...", ...}
│   │
│   └─> Response: {"id": 5, "link": "https://.../home/", ...}
│
└─> END: 5 pages created in database

Timeline:
Nonce fetch:      ~50ms
Each page POST:   ~200-300ms
Total for 5:      ~1.5 seconds
```

---

## Data Flow: Installing Plugin

```
START: Install Plugin
│
├─> Navigate to plugin search
│   GET /wp-admin/plugin-install.php?s=wordpress-seo
│   └─> Renders HTML with <button class="install-now">
│
├─> Extract Install URL via page.evaluate
│   document.querySelector('.install-now').href
│   └─> "https://domain.com/wp-admin/update.php?
│          action=install-plugin&
│          plugin=wordpress-seo&
│          _wpnonce=abc123def456"
│
├─> Navigate to Install URL
│   GET /wp-admin/update.php?action=install-plugin&plugin=wordpress-seo&_wpnonce=abc123def456
│   │
│   ├─> WordPress Processes:
│   │   1. Validate nonce (_wpnonce in URL)
│   │   2. Check user is admin
│   │   3. Download plugin from wordpress.org
│   │   4. Extract to /wp-content/plugins/wordpress-seo/
│   │   5. Render activation page
│   │
│   └─> Response: HTML page with <a class="activate-now"> button
│
├─> Wait for page to load
│   page.locator('a.activate-now').waitFor()
│
├─> Click Activation Button
│   POST /wp-admin/plugins.php?action=activate&plugin=wordpress-seo/wp-seo.php
│   │
│   ├─> WordPress Processes:
│   │   1. Validate nonce
│   │   2. Load plugin file
│   │   3. Run plugin activation hooks
│   │   4. Update wp_options (active_plugins)
│   │
│   └─> Redirect: /wp-admin/plugins.php with success message
│
└─> END: Plugin installed and active

Timeline:
Search page load:    ~1 second
Extract URL:         ~10ms
Install download:    ~5-10 seconds
Activation:          ~500ms
Total:              ~10-15 seconds per plugin
```

---

## Request/Response Examples

### Getting Nonce
```
REQUEST:
GET /wp-admin/admin-ajax.php?action=rest-nonce HTTP/1.1
Host: www.aidotters.com
Cookie: wp_logged_in_abc123=user_token_xyz; ...

RESPONSE:
HTTP/1.1 200 OK
Content-Type: text/plain

a1b2c3d4e5f6
```

### Creating Page via REST API
```
REQUEST:
POST /wp-json/wp/v2/pages HTTP/1.1
Host: www.aidotters.com
Content-Type: application/json
X-WP-Nonce: a1b2c3d4e5f6
Cookie: wp_logged_in_abc123=user_token_xyz; ...

{
  "title": "ホーム",
  "slug": "home",
  "status": "publish",
  "content": "<p>Home page content</p>"
}

RESPONSE:
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 5,
  "date": "2025-02-14T12:34:56",
  "link": "https://www.aidotters.com/home/",
  "title": {"rendered": "ホーム"},
  "slug": "home",
  "status": "publish",
  ...
}
```

### Creating Category via REST API
```
REQUEST:
POST /wp-json/wp/v2/categories HTTP/1.1
Host: www.aidotters.com
Content-Type: application/json
X-WP-Nonce: a1b2c3d4e5f6

{
  "name": "AI技術",
  "slug": "ai-technology",
  "description": "AI・機械学習に関する技術記事"
}

RESPONSE:
HTTP/1.1 201 Created

{
  "id": 2,
  "name": "AI技術",
  "slug": "ai-technology",
  "taxonomy": "category",
  "description": "AI・機械学習に関する技術記事",
  "count": 0,
  ...
}
```

---

## Security Model

```
┌─────────────────────────────────────────────────┐
│         SECURITY LAYERS (WordPress)             │
└─────────────────────────────────────────────────┘

Layer 1: Authentication
├─> User login (username + password)
└─> Session cookie created and verified

Layer 2: CSRF Protection
├─> Nonce generated: one-time token
├─> Embedded in forms or returned via AJAX
└─> Validated on every action

Layer 3: Authorization / Capabilities
├─> Check if user has capability to edit pages
├─> Check if user can create categories
└─> Check if user can install plugins (admin only)

Layer 4: REST API Specific
├─> Validate nonce in X-WP-Nonce header
├─> Check user permission for endpoint
└─> Rate limiting (optional)

┌─────────────────────────────────────────────────┐
│     PLAYWRIGHT INTEGRATION PERSPECTIVE          │
└─────────────────────────────────────────────────┘

✓ Cookie persistence: Automatic (browser feature)
✓ Nonce retrieval: page.evaluate() in logged-in context
✓ Header injection: fetch() accepts custom headers
✓ CSRF: WordPress validates nonce in every request

= Secure by default, no extra config needed
```

---

## Error Handling Flow

```
Try: page.evaluate(async ({nonce}) => {
  const resp = await fetch('/wp-json/wp/v2/pages', {
    method: 'POST',
    headers: {'X-WP-Nonce': nonce},
    body: JSON.stringify(data)
  });
  return {status: resp.status, data: await resp.json()};
})

Response Cases:

Case 1: Success (201)
└─> Create page successfully
    Page ID returned, can be used in REST API

Case 2: 401 Unauthorized
├─> Nonce invalid OR
├─> Cookie not included OR
├─> User not logged in
└─> Retry: Get new nonce, or re-login

Case 3: 403 Forbidden
├─> User lacks capability (not admin for plugins)
├─> Or insufficient permissions
└─> Fallback: Use Playwright to manually perform in UI

Case 4: 400 Bad Request
├─> Invalid JSON in body
├─> Missing required fields
├─> Invalid field values
└─> Check data format, retry with corrected payload

Case 5: 500 Server Error
├─> Plugin conflict or PHP error
├─> Database issue
└─> Check WordPress error logs, retry after fix
```

---

## Plugin Installation State Machine

```
┌──────────────┐
│   Not Found  │ (plugin not downloaded yet)
└──────┬───────┘
       │ Search for plugin
       ▼
┌──────────────────────┐
│  Search Results      │ (plugin found on wp.org)
│ [Install Now] btn    │
└──────┬───────────────┘
       │ Click [Install Now]
       ▼
┌──────────────────────┐
│   Installing         │ (downloading, extracting)
│ (progress indicator) │
└──────┬───────────────┘
       │ Download + Extract complete
       ▼
┌──────────────────────┐
│  Installed           │ (plugin files in place)
│ [Activate] link      │ (but not active yet)
└──────┬───────────────┘
       │ Click [Activate]
       ▼
┌──────────────────────┐
│   Activating         │
│ (hooks running)      │
└──────┬───────────────┘
       │ Hooks complete
       ▼
┌──────────────────────┐
│   Active             │ (loaded and running)
│ [Deactivate] link    │
└──────────────────────┘

In WordPress terms:
- Files on disk: "Installed"
- In wp_options: "Active"
- Loaded in memory: "Running"

Playwright flow:
1. page.goto(install_url)  ──> Navigate to install URL with nonce
2. page.waitFor(activate)  ──> Wait for activate button
3. page.click(activate)    ──> Trigger activation
4. page.waitFor(success)   ──> Verify activation succeeded
```

---

## Navigation Block Structure

```
WordPress Block Markup (used in REST API):
┌────────────────────────────────────────────────────┐
│ <!-- wp:navigation-link {...attributes...} /-->    │
│ <!-- wp:navigation-link {...attributes...} /-->    │
│ <!-- wp:navigation-link {...attributes...} /-->    │
└────────────────────────────────────────────────────┘

Example:
┌────────────────────────────────────────────────────┐
│ <!-- wp:navigation-link {                          │
│   "label": "ホーム",                               │
│   "url": "https://aidotters.com/",                │
│   "kind": "custom"                                │
│ } /-->                                            │
│                                                    │
│ <!-- wp:navigation-link {                          │
│   "label": "会社概要",                             │
│   "url": "https://aidotters.com/about/",          │
│   "kind": "custom"                                │
│ } /-->                                            │
│                                                    │
│ <!-- wp:navigation-link {                          │
│   "label": "ブログ",                               │
│   "url": "https://aidotters.com/blog/",           │
│   "kind": "custom"                                │
│ } /-->                                            │
└────────────────────────────────────────────────────┘

REST API:
POST /wp-json/wp/v2/navigation/{ID}
Body: { "content": "...block markup..." }

Order matters: Links render in source order
Reorder: Update content with links in desired sequence
```

---

## Nonce Lifecycle

```
┌──────────────────────────────────────┐
│    NONCE GENERATION & VALIDATION     │
└──────────────────────────────────────┘

Generation:
  fetch('/wp-admin/admin-ajax.php?action=rest-nonce')
    ↓
  WordPress generates 10-char random token
  WordPress stores in temporary cache/session
    ↓
  Returns: "a1b2c3d4e5"

Validation (on each API request):
  Request includes: X-WP-Nonce: a1b2c3d4e5
    ↓
  WordPress:
    1. Look up nonce in cache
    2. Verify timestamp (nonce expires ~12 hours)
    3. Check nonce matches request
    4. Delete nonce (one-time use per action)
    ↓
  Result: Accept request or 401 Unauthorized

Implementation Detail:
  - Single nonce can be used for multiple read operations
  - Typically must regenerate for write operations
  - In practice: Get once, use for entire page.evaluate
    (works because all fetches happen before cache invalidation)

Cost:
  - Nonce generation: ~10ms per fetch
  - Caching one nonce: ~1ms validation per use
  - Total for 5 pages with 1 nonce: ~10ms + 5ms = 15ms auth
```

---

## Comparison: Different Authentication Methods

```
┌────────────────────────────────────────────────────────────┐
│     METHOD 1: Cookie + Nonce (Recommended)                │
├────────────────────────────────────────────────────────────┤
│ Used in: page.evaluate() context                          │
│ How: Auto-managed cookies + fetch with nonce header       │
│ Pros:                                                      │
│   ✓ Works in browser context                             │
│   ✓ Session management automatic                         │
│   ✓ CSRF protection built-in                             │
│   ✓ No credentials exposed in code                       │
│ Cons:                                                      │
│   ✗ Only works in page.evaluate, not external scripts    │
│   ✗ Nonce must be retrieved first                        │
│ Best for: Playwright integration                          │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│     METHOD 2: Basic Auth (Alternative)                    │
├────────────────────────────────────────────────────────────┤
│ Used in: External scripts, curl, Python httpx            │
│ How: Authorization: Basic base64(user:password)           │
│ Pros:                                                      │
│   ✓ Works anywhere (no session needed)                   │
│   ✓ Programmatic (username:password known)               │
│   ✓ Simple to implement                                  │
│ Cons:                                                      │
│   ✗ Credentials in HTTP headers                          │
│   ✗ Must use HTTPS (not HTTP)                            │
│   ✗ Cannot use with regular login password               │
│   ✗ Must use Application Password (separate)             │
│ Best for: Server-to-server, CI/CD scripts                │
└────────────────────────────────────────────────────────────┘

Hybrid Approach:
├─ Playwright: Use Method 1 (cookie + nonce)
└─ Python backend: Use Method 2 (Basic Auth with app password)
```

---

## Performance Optimization Tips

```
Sequential (Safe but Slow):
for page in pages:
  result = await fetch(create_page, page)
  // 200ms per page × 5 = 1 second

Batch in page.evaluate (Recommended):
await page.evaluate(async () => {
  const nonce = await fetch(nonce_url).then(r => r.text())
  const results = []
  for (const page of pages) {
    const result = await fetch(
      '/wp-json/wp/v2/pages',
      {headers: {'X-WP-Nonce': nonce}, body: page}
    )
    results.push(result)
  }
  return results
})
// 50ms fetch nonce + (100ms each × 5 pages) = 550ms total

Parallel (Caution - May Hit Rate Limits):
const nonce = await getNonce()
const promises = pages.map(p =>
  fetch('/wp-json/wp/v2/pages', {
    headers: {'X-WP-Nonce': nonce},
    body: p
  })
)
await Promise.all(promises)
// ~100-200ms (limited by server response time)
// WARNING: May trigger rate limiting or lock issues

Recommendation:
├─ Use batch in single page.evaluate
├─ Avoid Promise.all (WordPress not optimized for parallel writes)
└─ Nonce generation is bottleneck, minimize calls
```

