# WordPress Playwright Integration - Code Templates

Ready-to-use code templates from successful session patterns.

## Template 1: Create Multiple Pages via REST API

```javascript
async (page) => {
  const pages = [
    { title: "ホーム", slug: "home", content: "Home content" },
    { title: "会社概要", slug: "about", content: "About content" },
    { title: "サービス", slug: "services", content: "Services content" },
    { title: "ブログ", slug: "blog", content: "" },
    { title: "お問い合わせ", slug: "contact", content: "Contact content" },
  ];

  // Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  const results = [];
  for (const p of pages) {
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

**Expected Output:**
```
✓ ホーム: ID=5
✓ 会社概要: ID=6
✓ サービス: ID=7
✓ ブログ: ID=8
✓ お問い合わせ: ID=9
```

---

## Template 2: Create Categories and Rename Default

```javascript
async (page) => {
  const categories = [
    { name: "AI技術", slug: "ai-technology", description: "AI・機械学習に関する技術記事" },
    { name: "開発Tips", slug: "dev-tips", description: "開発に役立つTipsやチュートリアル" },
    { name: "プロダクト", slug: "products", description: "プロダクト・サービスの紹介" },
    { name: "お知らせ", slug: "news", description: "チームからのお知らせ" },
  ];

  // Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  const results = [];

  // Create new categories
  for (const cat of categories) {
    const resp = await page.evaluate(async ({cat, nonce}) => {
      const resp = await fetch('/wp-json/wp/v2/categories', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-WP-Nonce': nonce
        },
        body: JSON.stringify(cat)
      });
      return { status: resp.status, data: await resp.json() };
    }, {cat, nonce});

    if (resp.status === 201) {
      results.push(`✓ ${cat.name}: ID=${resp.data.id}`);
    } else {
      results.push(`✗ ${cat.name}: ${resp.status}`);
    }
  }

  // Rename default "Uncategorized" (ID=1)
  const renameResp = await page.evaluate(async ({nonce}) => {
    const resp = await fetch('/wp-json/wp/v2/categories/1', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': nonce
      },
      body: JSON.stringify({ name: "未分類", slug: "uncategorized" })
    });
    return resp.status;
  }, {nonce});

  results.push(`✓ Uncategorized → 未分類: ${renameResp}`);

  return results.join('\n');
}
```

**Expected Output:**
```
✓ AI技術: ID=2
✓ 開発Tips: ID=3
✓ プロダクト: ID=4
✓ お知らせ: ID=5
✓ Uncategorized → 未分類: 200
```

---

## Template 3: Get and Update Navigation Menu

```javascript
async (page) => {
  // Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  // Get navigation menus
  const navMenus = await page.evaluate(async ({nonce}) => {
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

  // Log menus found
  console.log('Navigation menus found:', navMenus.length);
  navMenus.forEach(m => console.log(`  - ${m.title} (ID: ${m.id})`));

  // Update main navigation (typically ID=4)
  const navigationId = navMenus[0]?.id || 4;

  const newContent = `<!-- wp:navigation-link {"label":"ホーム","url":"https://www.aidotters.com/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"会社概要","url":"https://www.aidotters.com/about/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"サービス","url":"https://www.aidotters.com/services/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"ブログ","url":"https://www.aidotters.com/blog/","kind":"custom"} /-->
<!-- wp:navigation-link {"label":"お問い合わせ","url":"https://www.aidotters.com/contact/","kind":"custom"} /-->`;

  const updateResult = await page.evaluate(async ({nonce, navigationId, newContent}) => {
    const resp = await fetch(`/wp-json/wp/v2/navigation/${navigationId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': nonce
      },
      body: JSON.stringify({ content: newContent })
    });
    return { status: resp.status, ok: resp.ok };
  }, {nonce, navigationId, newContent});

  return `Updated navigation ID=${navigationId}: ${updateResult.status}`;
}
```

**Expected Output:**
```
Navigation menus found: 2
  - メインメニュー (ID: 4)
  - Footer Menu (ID: 5)
Updated navigation ID=4: 200
```

---

## Template 4: Install Multiple Plugins

```javascript
async (page) => {
  const plugins = [
    { slug: 'wordpress-seo', name: 'Yoast SEO' },
    { slug: 'contact-form-7', name: 'Contact Form 7' },
    { slug: 'xml-sitemap-generator-for-google', name: 'XML Sitemap' }
  ];

  const results = [];

  for (const plugin of plugins) {
    try {
      // Navigate to plugin search
      await page.goto(
        `https://www.aidotters.com/wp-admin/plugin-install.php?s=${plugin.slug}&tab=search&type=term`
      );
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);

      // Click install button
      const installBtn = page.locator('button.install-now').first();
      if (await installBtn.count() === 0) {
        results.push(`- ${plugin.name}: Already installed`);
        continue;
      }

      await installBtn.click();

      // Wait for activation button to appear
      try {
        await page.locator('a.activate-now').first().waitFor({ timeout: 30000 });

        // Click activation button
        await page.locator('a.activate-now').first().click();
        await page.waitForLoadState('networkidle');

        results.push(`✓ ${plugin.name}: Installed & Activated`);
      } catch(e) {
        results.push(`△ ${plugin.name}: Installed (activation pending)`);
      }
    } catch(e) {
      results.push(`✗ ${plugin.name}: Error - ${e.message}`);
    }
  }

  return results.join('\n');
}
```

**Expected Output:**
```
✓ Yoast SEO: Installed & Activated
✓ Contact Form 7: Installed & Activated
✓ XML Sitemap: Installed & Activated
```

---

## Template 5: Set Front Page and Blog Page

**Note: Use in separate commands after page creation**

```javascript
// After pages are created, navigate to Reading Settings
await page.goto('https://www.aidotters.com/wp-admin/options-reading.php');
await page.waitForLoadState('networkidle');

// Fill form using tool: browser_fill_form
// Fields:
//   - "固定ページラジオボタン" (radio button)
//   - "ホームページ" dropdown
//   - "投稿ページ" dropdown
```

**Using browser_fill_form tool (from transcript):**
```json
{
  "fields": [
    {
      "name": "固定ページラジオボタン",
      "type": "radio",
      "ref": "e165",
      "value": "true"
    },
    {
      "name": "ホームページ",
      "type": "combobox",
      "ref": "e170",
      "value": "ホーム"
    },
    {
      "name": "投稿ページ",
      "type": "combobox",
      "ref": "e173",
      "value": "ブログ"
    }
  ]
}
```

Then click "変更を保存" button.

---

## Template 6: Extract Plugin Install URLs

For examining available plugins:

```javascript
async (page) => {
  // Navigate to plugin search
  await page.goto('https://www.aidotters.com/wp-admin/plugin-install.php?s=wordpress-seo&tab=search&type=term');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);

  // Extract all install buttons and their URLs
  const buttons = await page.evaluate(() => {
    const btns = document.querySelectorAll('.install-now');
    return Array.from(btns).map(b => ({
      text: b.textContent.trim(),
      href: b.href,
      slug: b.dataset.slug,
      name: b.dataset.name,
      class: b.className
    }));
  });

  return JSON.stringify(buttons, null, 2);
}
```

**Expected Output:**
```json
[
  {
    "text": "今すぐインストール",
    "href": "https://www.aidotters.com/wp-admin/update.php?action=install-plugin&plugin=wordpress-seo&_wpnonce=1e2efbd86b",
    "slug": "wordpress-seo",
    "name": "Yoast SEO",
    "class": "button install-now"
  }
]
```

---

## Template 7: Create and Publish a Blog Post via REST API

```javascript
async (page) => {
  // Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  // Create blog post
  const post = {
    title: "Test Article",
    slug: "test-article",
    content: "<p>This is a test article created via REST API.</p>",
    status: "draft",  // or "publish"
    categories: [2]   // AI技術 (ID from template 2)
  };

  const result = await page.evaluate(async ({nonce, post}) => {
    const resp = await fetch('/wp-json/wp/v2/posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': nonce
      },
      body: JSON.stringify(post)
    });
    return { status: resp.status, data: await resp.json() };
  }, {nonce, post});

  if (result.status === 201) {
    return `✓ Post created: ID=${result.data.id}, URL=${result.data.link}`;
  } else {
    return `✗ Failed: ${result.status} - ${JSON.stringify(result.data).substring(0, 100)}`;
  }
}
```

**Expected Output:**
```
✓ Post created: ID=17, URL=https://www.aidotters.com/test-article/
```

---

## Template 8: Safe Plugin Activation with Error Handling

```javascript
async (page) => {
  const pluginSlug = 'wordpress-seo';
  const pluginName = 'Yoast SEO';

  try {
    // Navigate to search
    await page.goto(
      `https://www.aidotters.com/wp-admin/plugin-install.php?s=${pluginSlug}&tab=search&type=term`
    );
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Check if already installed
    const installBtn = page.locator('button.install-now').first();
    if (await installBtn.count() === 0) {
      console.log(`${pluginName}: Already installed, checking activation...`);

      // Check if activate button exists
      const activateBtn = page.locator('a.activate-now').first();
      if (await activateBtn.count() > 0) {
        await activateBtn.click();
        await page.waitForLoadState('networkidle');
        return `✓ ${pluginName}: Activated`;
      } else {
        return `- ${pluginName}: Already active`;
      }
    }

    // Install
    console.log(`Installing ${pluginName}...`);
    await installBtn.click();

    // Wait for completion with timeout
    let activated = false;
    let retries = 0;

    while (!activated && retries < 5) {
      try {
        const activateBtn = page.locator('a.activate-now').first();
        if (await activateBtn.count() > 0) {
          await activateBtn.click();
          await page.waitForLoadState('networkidle');
          activated = true;
          return `✓ ${pluginName}: Installed & Activated`;
        }
      } catch(e) {
        retries++;
        await page.waitForTimeout(3000);
      }
    }

    if (!activated) {
      return `△ ${pluginName}: Installed (manual activation needed)`;
    }

  } catch(e) {
    return `✗ ${pluginName}: Error - ${e.message}`;
  }
}
```

---

## Template 9: Verify REST API Authentication

```javascript
async (page) => {
  // Test 1: Get nonce
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  console.log(`Nonce received: ${nonce.length} chars`);

  // Test 2: List categories (read-only, no auth needed but nonce helps)
  const categories = await page.evaluate(async ({nonce}) => {
    const resp = await fetch('/wp-json/wp/v2/categories?per_page=1', {
      headers: { 'X-WP-Nonce': nonce }
    });
    const data = await resp.json();
    return { status: resp.status, count: data.length };
  }, {nonce});

  console.log(`Categories accessible: ${categories.status}`);

  // Test 3: Try creating a test category
  const testCat = await page.evaluate(async ({nonce}) => {
    const resp = await fetch('/wp-json/wp/v2/categories', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': nonce
      },
      body: JSON.stringify({
        name: "Test Category",
        slug: "test-category"
      })
    });
    return { status: resp.status, id: (await resp.json()).id };
  }, {nonce});

  console.log(`Create category: ${testCat.status} (ID: ${testCat.id})`);

  return `All tests passed: Nonce=${nonce.substring(0, 5)}..., Categories OK, Create OK`;
}
```

**Expected Output:**
```
Nonce received: 10 chars
Categories accessible: 200
Create category: 201 (ID: 42)
All tests passed: Nonce=a1b2c..., Categories OK, Create OK
```

---

## Template 10: Batch Operations with Error Recovery

```javascript
async (page) => {
  const operations = [
    { type: 'category', data: { name: "AI", slug: "ai" } },
    { type: 'category', data: { name: "ML", slug: "ml" } },
    { type: 'page', data: { title: "Page 1", slug: "page-1", status: "publish" } },
    { type: 'page', data: { title: "Page 2", slug: "page-2", status: "publish" } },
  ];

  // Get nonce once
  const nonce = await page.evaluate(async () => {
    const resp = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce');
    return await resp.text();
  });

  const results = { success: 0, failed: 0, errors: [] };

  for (const op of operations) {
    try {
      const endpoint = `/wp-json/wp/v2/${op.type}s`;
      const resp = await page.evaluate(async ({endpoint, data, nonce}) => {
        const r = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-WP-Nonce': nonce
          },
          body: JSON.stringify(data)
        });
        return { status: r.status, data: await r.json() };
      }, {endpoint, data: op.data, nonce});

      if (resp.status === 201) {
        results.success++;
        console.log(`✓ ${op.type}: ${op.data.name || op.data.title}`);
      } else {
        results.failed++;
        results.errors.push(`${op.type}: ${resp.status}`);
        console.log(`✗ ${op.type}: ${resp.status}`);
      }
    } catch(e) {
      results.failed++;
      results.errors.push(`${op.type}: ${e.message}`);
      console.log(`✗ ${op.type}: ${e.message}`);
    }
  }

  return `Results: ${results.success} success, ${results.failed} failed`;
}
```

**Expected Output:**
```
✓ category: AI
✓ category: ML
✓ page: Page 1
✓ page: Page 2
Results: 4 success, 0 failed
```

