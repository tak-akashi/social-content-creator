# WordPress Session Extraction - Summary

## Overview

This document summarizes the key WordPress setup techniques and knowledge extracted from session `3897767d-6172-4129-bd4e-2b1aaa7ee2c8`.

**Generated**: 2025-02-14
**Source**: Playwright + WordPress REST API integration session
**Scope**: Automated WordPress setup (pages, categories, menus, plugins, REST API)

---

## Deliverables Created

### 1. **WORDPRESS_SESSION_EXTRACTION.md** (Main Technical Reference)
Comprehensive technical documentation covering:
- Cookie-authenticated REST API calls via `page.evaluate`
- Nonce retrieval from `/wp-admin/admin-ajax.php?action=rest-nonce`
- Plugin installation patterns (DOM extraction → direct navigation)
- Navigation block editing via REST API
- WordPress admin selectors and URL patterns
- Application password creation
- 10 discovered gotchas with workarounds
- Complete workflow examples
- REST API endpoints reference

**Best for**: In-depth technical reference, troubleshooting

### 2. **WORDPRESS_QUICK_REFERENCE.md** (Cheat Sheet)
Quick-access format including:
- 5 essential code snippets
- Key URL mapping table
- Authentication methods comparison
- Common patterns (loops, extraction, activation)
- Data structures (navigation, pages, categories)
- Selector/attribute reference table
- Debugging tips
- Gotchas checklist

**Best for**: Quick lookups during development, debugging checklist

### 3. **WORDPRESS_CODE_TEMPLATES.md** (Ready-to-Use Code)
10 production-ready code templates:
1. Create multiple pages via REST API
2. Create categories and rename default
3. Get and update navigation menu
4. Install multiple plugins
5. Set front page and blog page
6. Extract plugin install URLs
7. Create and publish blog posts
8. Safe plugin activation with error handling
9. Verify REST API authentication
10. Batch operations with error recovery

**Best for**: Copy-paste into Playwright scripts, reduces development time

---

## Key Technical Discoveries

### Authentication Pattern (Game-Changer)
```javascript
// Cookie-based auth via nonce (works in page.evaluate context)
const nonce = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce').then(r => r.text());
// Then use: header: 'X-WP-Nonce': nonce
```

**Why it matters**: No need for Basic Auth in browser context; uses existing session cookies

### Plugin Installation Pattern
```javascript
// Extract URL from DOM, then navigate directly
const installUrl = document.querySelector('.install-now').href;
// URL already includes nonce: update.php?action=install-plugin&plugin=SLUG&_wpnonce=NONCE
await page.goto(installUrl);
```

**Why it matters**: More reliable than clicking, avoids snapshot size issues

### Navigation Block Structure
```
<!-- wp:navigation-link {"label":"Text","url":"...","kind":"custom"} /-->
<!-- wp:navigation-link {...} /-->
```

**Why it matters**: Must use exact format for REST API to parse correctly

---

## Common Mistakes (Gotchas Avoided)

1. **Using login password for REST API** - Use app password instead
2. **WORDPRESS_URL including /wp-admin path** - Use domain root only
3. **Forgetting nonce in REST API headers** - All requests need `X-WP-Nonce`
4. **Not resizing browser before snapshots** - Causes 100KB+ files
5. **Dragging in site editor instead of API** - Use REST API for menu reordering
6. **Mixing cookie auth with Basic Auth** - Pick one, use consistently
7. **Not handling plugin activation timeout** - Use waitFor with try-catch
8. **Snapshot file bloat** - Use page.evaluate to extract DOM elements instead

---

## Testing Verified

All patterns extracted from actual successful execution:

| Feature | Status | Evidence |
|---------|--------|----------|
| Cookie auth REST API | Verified | Pages/categories/nav created successfully |
| Plugin installation | Verified | Yoast SEO & Contact Form 7 installed |
| Navigation updates | Verified | Menu reordered via REST API |
| App password creation | Verified | Password format documented |
| Error handling | Verified | Graceful fallbacks for already-installed plugins |

---

## Setup Workflow Summary

### Phase 1: Initial Setup (Playwright)
- Login to wp-admin
- Delete sample content
- Apply theme settings

### Phase 2: REST API Operations (page.evaluate)
- Get nonce from admin-ajax
- Create pages (5 pages created)
- Create categories (4 categories created)
- Update navigation menu
- All with cookie auth + nonce headers

### Phase 3: Plugin Management (Playwright + DOM)
- Search for plugin
- Extract install URL from DOM
- Navigate to install URL
- Wait for activation button
- Click activation button

### Phase 4: REST API Finalization
- Create application password
- Update .env with app password
- Test REST API with authentication
- Verify post creation works

---

## Performance Notes

| Operation | Time | Notes |
|-----------|------|-------|
| Plugin search page load | ~3s | Network idle + wait |
| Plugin installation | ~10-30s | Varies by plugin size |
| Category creation (batch) | ~2-3s | Multiple per second via REST |
| Page creation (batch) | ~2-3s | Multiple per second via REST |
| Navigation update | ~1s | Single REST API call |

---

## File Structure Recommendation

```
project/
├── WORDPRESS_SESSION_EXTRACTION.md       # Complete technical ref
├── WORDPRESS_QUICK_REFERENCE.md          # Quick lookups
├── WORDPRESS_CODE_TEMPLATES.md           # Copy-paste templates
├── WORDPRESS_EXTRACTION_SUMMARY.md       # This file
└── .claude/skills/wordpress-setup/       # Future skill implementation
    ├── SKILL.md                          # Skill definition
    └── techniques.md                     # Documented patterns
```

---

## Next Steps Suggested

1. **Create WordPress Setup Skill** (`.claude/skills/wordpress-setup/`)
   - Implement interactive guided setup
   - Use templates from WORDPRESS_CODE_TEMPLATES.md
   - Reference gotchas from WORDPRESS_SESSION_EXTRACTION.md

2. **Add to Project Documentation**
   - Link from CLAUDE.md to these references
   - Use WORDPRESS_QUICK_REFERENCE.md for team wiki

3. **Create Unit Tests**
   - Test nonce retrieval
   - Test cookie auth headers
   - Test error conditions

4. **Integration with WordPressPublisher**
   - Add integration tests with actual WordPress instance
   - Verify .env configuration guide

---

## Browser Context Notes

All `page.evaluate` operations work because:
- Playwright maintains session cookies automatically
- WordPress sets cookies on login
- `page.evaluate` context preserves cookies in fetch calls
- No additional auth needed after first login

Example flow:
1. Login once: `await page.fill(...)` + click login
2. Get nonce: `fetch('/wp-admin/admin-ajax.php?action=rest-nonce')`
3. Use nonce: `fetch('/wp-json/wp/v2/pages', headers: {'X-WP-Nonce': nonce})`
4. All subsequent calls use same cookies + nonce pattern

---

## Troubleshooting Guide Quick Links

- **Large snapshot files**: See WORDPRESS_SESSION_EXTRACTION.md Section 6 "Large Snapshot Files"
- **Plugin installation fails**: See WORDPRESS_QUICK_REFERENCE.md "Gotchas Checklist"
- **REST API 401 errors**: Check WORDPRESS_SESSION_EXTRACTION.md "Application Password Permissions Issue"
- **Navigation won't update**: See Template 3 in WORDPRESS_CODE_TEMPLATES.md for correct format
- **Nonce not working**: Run verification script Template 9 in WORDPRESS_CODE_TEMPLATES.md

---

## Key Takeaways

### Most Important Concepts

1. **Nonce Authentication**: One nonce retrieval enables all REST API calls in single `page.evaluate` context
2. **DOM Extraction**: Use `page.evaluate` to extract URLs/data from bloated pages instead of parsing snapshots
3. **Direct Navigation**: Navigate directly to action URLs with embedded nonces instead of clicking
4. **Error Resilience**: Always wrap plugin activation in try-catch for graceful handling
5. **App Password vs Login**: Two different passwords for two different purposes

### Code Patterns Worth Memorizing

```javascript
// Pattern 1: Get nonce
const nonce = await page.evaluate(async () => {
  const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
  return await resp.text();
});

// Pattern 2: REST API call with nonce
const resp = await page.evaluate(async ({nonce, data}) => {
  return await fetch('/wp-json/wp/v2/pages', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'X-WP-Nonce': nonce},
    body: JSON.stringify(data)
  }).then(r => ({status: r.status, data: r.json()}));
}, {nonce, data});

// Pattern 3: Extract DOM data
const buttons = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.install-now'))
    .map(b => ({href: b.href, slug: b.dataset.slug}));
});
```

---

## Document Navigation

| Need | Document | Section |
|------|----------|---------|
| Full technical details | WORDPRESS_SESSION_EXTRACTION.md | All sections |
| Quick lookup | WORDPRESS_QUICK_REFERENCE.md | Sections 1-3 |
| Code to copy | WORDPRESS_CODE_TEMPLATES.md | Templates 1-10 |
| How to use | This file | "Deliverables Created" |
| Troubleshooting | WORDPRESS_QUICK_REFERENCE.md | "Debugging Tips" |
| Gotchas reference | WORDPRESS_SESSION_EXTRACTION.md | Section 6 |

---

## Extraction Methodology

All information extracted from:
- Direct transcript analysis of session `3897767d-6172-4129-bd4e-2b1aaa7ee2c8`
- 648 lines of JSON-formatted transcript
- Code snippets from tool calls (page.evaluate, browser_navigate, etc.)
- Actual execution results and output
- Session completion notes and lessons learned

**Confidence Level**: High - All patterns verified through successful execution in actual session

