Phase 6 Batch 1 — 9 篇 AI 重寫文章
=========================================
內容：持分/共有土地主題 9 篇完整文章

變更檔案：
  修改：
    _worker.js              新增 28 條精確文章轉址
    index.html              Phase 5B 首頁（編輯雜誌風）
    sitemap.xml             加入 9 個新文章 URL
  
  新增：
    blog/articles/co-*.html           9 篇新文章（編輯風）
    assets/editorial.css              設計系統 CSS（如已 push 可忽略）
    scripts/batch1_generator.py       文章模板生成器（未來 Batch 2-4 會用）
    scripts/batch1_update_worker.py   Worker 轉址更新腳本
    scripts/articles-content/*.json   8 份內容 JSON（將來可編輯調文字）

文章清單（9 篇）：
  01. co-rental-fenbie.html                      分別共有可以出租嗎？（之前示範篇）
  02. co-vs-joint-ownership-distinction.html     如何分辨公同共有/分別共有？（393 點擊）
  03. co-ownership-gift-guide.html               分別共有可以贈與嗎？（299 點擊）
  04. co-ownership-boundary-survey.html          持分土地可以鑑界嗎？（246 點擊）
  05. co-ownership-pricing.html                  持分土地怎麼定價？（221 點擊）
  06. co-ownership-building-house.html           持分土地能蓋房子嗎？（182 點擊）
  07. co-ownership-buy-sell-guide.html           持分土地可以買賣嗎？（111 點擊）
  08. co-ownership-partition-guide.html          共有土地分割完整攻略（102 點擊）
  09. co-ownership-inheritance.html              持分土地怎麼繼承？（82 點擊）

每篇文章具備：
  ✅ 編輯雜誌風排版（drop cap、pull quote、case study 框）
  ✅ 完整 SEO meta（title/description/keywords/og:image/canonical）
  ✅ 3 組 JSON-LD schemas（Article + FAQPage + BreadcrumbList）
  ✅ 5 題 FAQ
  ✅ 1 個化名案例（王家/李家/陳家... + 新北某地/某縣市）
  ✅ 2 個相關服務內部連結
  ✅ 文末 CTA（電話 + LINE + 服務頁）

_worker.js 的精確轉址範例：
  /f/分別共有可以出租嗎？——土地專家的淺白解說
    → /blog/articles/co-rental-fenbie.html
  /f/如何知道土地是共同共有還是分別共有？
    → /blog/articles/co-vs-joint-ownership-distinction.html
  （共 28 條，優先於既有的 KEYWORD_RULES）

部署步驟（同之前的 Phase 部署模式）：
  1. 解壓到本機 bqfox-site/ 根目錄（README 可刪）
  2. GitHub Desktop 會看到約 22 個檔案變更
  3. Commit message: feat(phase6-batch1): 9 AI articles + article-level redirects
  4. Push origin
  5. Cloudflare 1-3 分鐘自動部署
  6. 測試：訪問 https://www.bqfox.com/f/分別共有可以出租嗎？ 應自動跳到新文章

預期效果（1-3 個月）：
  - 舊 URL 精準轉址，使用者不會再被導到無關內容
  - Google 重新索引 → 9 篇文章排名逐步恢復
  - 預估恢復每月 100-200 次點擊
