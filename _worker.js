/**
 * 寶璣建設 bqfox-site Worker
 *
 * 職責：
 *   1. 攔截 GoDaddy 時代的舊 URL（/三七五租約解約、/f/xxx 等）
 *   2. 攔截根目錄舊命名 HTML 檔（/375-04.html、/an-01.html 等，Phase 1 dedup）
 *   3. 301 轉址到現有新站的對應頁面（/pages/xxx.html、/blog/articles/）
 *   4. 其他請求交還給 Cloudflare 的靜態資產系統
 *
 * 部署：放在 bqfox-site repo 根目錄（與 index.html 同層），推上 GitHub
 *      Cloudflare 會自動偵測 _worker.js 並啟用 JavaScript 邏輯
 *
 * 版本歷程：
 *   - Phase 0-5: 基礎建設
 *   - Phase 6 Batch 1 (2026-04-22): 9 篇持分/共有土地主題新文章
 *   - Phase 6 Batch 2 (2026-04-22): 8 篇道路用地主題新文章
 *   - Phase 6 Batch 3 (2026-04-22): 8 篇三七五+祭祀公業主題新文章
 *   - Phase 6 Batch 4a (2026-04-22): 8 篇多元主題新文章
 *   - Phase 6 Batch 4b (2026-04-22): 7 篇多元主題新文章
 *   - Phase 6 Batch 5 (2026-04-22): 15 篇 Tier 2 TOP 15 文章(收官)
 *   - Phase 7 Batch 6 (2026-04-22): 8 篇容積移轉進攻型主題群文章
 *   - Phase 7 Batch 7 (2026-04-22): 8 篇道路用地進攻型主題群文章(GEO 強化)
 *   - Phase 7 Batch 8 (2026-04-22): 8 篇公共設施保留地主題群文章(GEO + 多元分類)
 *   - Phase 7 Batch 9 (2026-04-22): 8 篇持分土地終極戰場(56,429 曝光/月)
 *   - Batch 10 (2026-04-23): 8 篇持分土地深度型(稅務/失聯/GEO/訴訟/法拍/詐騙/時效/兩岸) ← 本次更新
 */

// ============================================
// 精確對應表：舊服務類別頁 → 新服務頁
// ============================================
const EXACT_REDIRECTS = {
  // 服務頁（高流量，必定要轉）
  '/三七五租約解約': '/pages/tenancy-375.html',
  '/道路用地買賣': '/pages/road-land.html',
  '/祭祀公業': '/pages/ancestral-land.html',
  '/公同共有處理': '/pages/joint-ownership.html',
  '/公同共有': '/pages/joint-ownership.html',
  '/容積移轉代辦': '/pages/floor-area-ratio.html',
  '/持份土地買賣、租賃': '/pages/co-ownership.html',
  '/持份土地買賣': '/pages/co-ownership.html',
  '/各種持份土地買賣': '/pages/co-ownership.html',
  '/重劃地買賣': '/pages/rezoning-land.html',
  '/兩岸三地繼承': '/pages/cross-strait-inheritance.html',
  '/日據繼承': '/pages/cross-strait-inheritance.html',
  '/浮覆地復權': '/pages/road-land.html',
  '/未辦繼承': '/blog/index.html',
  '/未辦繼承處理': '/blog/index.html',
  '/地籍清理': '/blog/index.html',
  '/各種超困難案件處理': '/index.html#services',
  '/與我們聯絡': '/index.html#contact',
  '/聯絡我們': '/index.html#contact',
  '/關於我們': '/index.html#about',
  '/我們的陣容-1': '/index.html#about',
  '/首頁': '/',
};

// ============================================
// Phase 1: 根目錄重複 HTML → blog/articles/ 或 pages/
// （已同時用 meta-refresh 做 HTML fallback；此處為 server-side 301）
// ============================================
const LEGACY_FILE_REDIRECTS = {
  '/co-13.html': '/blog/articles/co-13.html',
  '/rl-13.html': '/blog/articles/rl-13.html',
  '/375-08.html': '/blog/articles/375-08.html',
  '/farm-03.html': '/blog/articles/farm-03.html',
  '/rl-15.html': '/blog/articles/rl-15.html',
  '/co-16.html': '/blog/articles/co-16.html',
  '/re-01.html': '/blog/articles/re-01.html',
  '/farm-01.html': '/blog/articles/farm-01.html',
  '/co-07.html': '/blog/articles/co-07.html',
  '/jo-03.html': '/blog/articles/jo-03.html',
  '/jo-04.html': '/blog/articles/jo-04.html',
  '/co-15.html': '/blog/articles/co-15.html',
  '/co-09.html': '/blog/articles/co-09.html',
  '/far-02.html': '/blog/articles/far-02.html',
  '/375-10.html': '/blog/articles/375-10.html',
  '/co-06.html': '/blog/articles/co-06.html',
  '/an-06.html': '/blog/articles/an-06.html',
  '/375-06.html': '/blog/articles/375-06.html',
  '/jo-05.html': '/blog/articles/jo-05.html',
  '/far-05.html': '/blog/articles/far-05.html',
  '/375-09.html': '/blog/articles/375-09.html',
  '/rl-11.html': '/blog/articles/rl-11.html',
  '/rl-14.html': '/blog/articles/rl-14.html',
  '/an-02.html': '/blog/articles/an-02.html',
  '/co-17.html': '/blog/articles/co-17.html',
  '/an-10.html': '/blog/articles/an-10.html',
  '/co-11.html': '/blog/articles/co-11.html',
  '/an-03.html': '/blog/articles/an-03.html',
  '/co-12.html': '/blog/articles/co-12.html',
  '/an-04.html': '/blog/articles/an-04.html',
  '/an-05.html': '/blog/articles/an-05.html',
  '/375-04.html': '/blog/articles/375-04.html',
  '/re-03.html': '/blog/articles/re-03.html',
  '/inh-01.html': '/blog/articles/inh-01.html',
  '/inh-03.html': '/blog/articles/inh-03.html',
  '/jo-01.html': '/blog/articles/jo-01.html',
  '/co-14.html': '/blog/articles/co-14.html',
  '/an-09.html': '/blog/articles/an-09.html',
  '/far-01.html': '/blog/articles/far-01.html',
  '/re-02.html': '/blog/articles/re-02.html',
  '/inh-04.html': '/blog/articles/inh-04.html',
  '/375-07.html': '/blog/articles/375-07.html',
  '/farm-02.html': '/blog/articles/farm-02.html',
  '/an-08.html': '/blog/articles/an-08.html',
  '/rl-09.html': '/blog/articles/rl-09.html',
  '/inh-05.html': '/blog/articles/inh-05.html',
  '/rl-10.html': '/blog/articles/rl-10.html',
  '/co-08.html': '/blog/articles/co-08.html',
  '/co-10.html': '/blog/articles/co-10.html',
  '/farm-04.html': '/blog/articles/farm-04.html',
  '/jo-02.html': '/blog/articles/jo-02.html',
  '/inh-06.html': '/blog/articles/inh-06.html',
  '/farm-05.html': '/blog/articles/farm-05.html',
  '/375-05.html': '/blog/articles/375-05.html',
  '/375-overview.html': '/blog/',
  '/road-land.html': '/',
  '/what-is-road-land.html': '/pages/road-land.html',
  '/rl-12.html': '/blog/articles/rl-12.html',
  '/an-07.html': '/blog/articles/an-07.html',
};

// ============================================
// Phase 6：精確文章 URL → 新文章
// 舊的 /f/xxx 標題，精確轉到對應的新文章（優先於關鍵字規則）
// ============================================
const ARTICLE_PRECISE_REDIRECTS = {
  // ===== Batch 1 持分/共有土地主題（2026-04-22） =====
  '/f/分別共有可以出租嗎？——土地專家的淺白解說': '/blog/articles/co-rental-fenbie.html',
  '/首頁/f/分別共有可以出租嗎？——土地專家的淺白解說': '/blog/articles/co-rental-fenbie.html',
  '/f/分別共有可以出租嗎？': '/blog/articles/co-rental-fenbie.html',
  '/首頁/f/分別共有可以出租嗎？': '/blog/articles/co-rental-fenbie.html',
  '/f/如何知道土地是共同共有還是分別共有？': '/blog/articles/co-vs-joint-ownership-distinction.html',
  '/首頁/f/如何知道土地是共同共有還是分別共有？': '/blog/articles/co-vs-joint-ownership-distinction.html',
  '/f/「公同共有」與「分別共有」的差別？': '/blog/articles/co-vs-joint-ownership-distinction.html',
  '/首頁/f/「公同共有」與「分別共有」的差別？': '/blog/articles/co-vs-joint-ownership-distinction.html',
  '/f/「公同共有」與「分別共有」的差別': '/blog/articles/co-vs-joint-ownership-distinction.html',
  '/首頁/f/「公同共有」與「分別共有」的差別': '/blog/articles/co-vs-joint-ownership-distinction.html',
  '/f/分別共有可以贈與嗎？': '/blog/articles/co-ownership-gift-guide.html',
  '/首頁/f/分別共有可以贈與嗎？': '/blog/articles/co-ownership-gift-guide.html',
  '/f/分別共有土地贈與': '/blog/articles/co-ownership-gift-guide.html',
  '/首頁/f/分別共有土地贈與': '/blog/articles/co-ownership-gift-guide.html',
  '/f/持分土地可以鑑界嗎？': '/blog/articles/co-ownership-boundary-survey.html',
  '/首頁/f/持分土地可以鑑界嗎？': '/blog/articles/co-ownership-boundary-survey.html',
  '/f/持分土地要怎麼定價?影響價格的關鍵因素一次看': '/blog/articles/co-ownership-pricing.html',
  '/首頁/f/持分土地要怎麼定價?影響價格的關鍵因素一次看': '/blog/articles/co-ownership-pricing.html',
  '/f/持分土地能蓋房子嗎？法規限制與申請程序解析': '/blog/articles/co-ownership-building-house.html',
  '/首頁/f/持分土地能蓋房子嗎？法規限制與申請程序解析': '/blog/articles/co-ownership-building-house.html',
  '/f/持分土地可以買賣嗎？注意事項與交易流程全解析': '/blog/articles/co-ownership-buy-sell-guide.html',
  '/首頁/f/持分土地可以買賣嗎？注意事項與交易流程全解析': '/blog/articles/co-ownership-buy-sell-guide.html',
  '/f/【超詳解懶人包】一張圖搞懂共有土地分割！專家教你避開法律陷阱': '/blog/articles/co-ownership-partition-guide.html',
  '/首頁/f/【超詳解懶人包】一張圖搞懂共有土地分割！專家教你避開法律陷阱': '/blog/articles/co-ownership-partition-guide.html',
  '/f/持分土地怎麼繼承？避免爭議的-3-個關鍵重點': '/blog/articles/co-ownership-inheritance.html',
  '/首頁/f/持分土地怎麼繼承？避免爭議的-3-個關鍵重點': '/blog/articles/co-ownership-inheritance.html',
  '/f/持分土地怎麼繼承？避免爭議的 3 個關鍵重點': '/blog/articles/co-ownership-inheritance.html',
  '/首頁/f/持分土地怎麼繼承？避免爭議的 3 個關鍵重點': '/blog/articles/co-ownership-inheritance.html',

  // ===== Batch 2 道路用地主題（2026-04-22 新增） =====
  // 1. 道路用地可以蓋房子嗎（GSC 歷史點擊 357）
  '/f/道路用地可以蓋房子嗎？資深地政專家教你破解「公共設施保留地」的5大迷思': '/blog/articles/road-land-can-build-house.html',
  '/首頁/f/道路用地可以蓋房子嗎？資深地政專家教你破解「公共設施保留地」的5大迷思': '/blog/articles/road-land-can-build-house.html',
  '/f/道路用地可以蓋房子嗎？資深地政專家教你破解公共設施保留地的5大迷思': '/blog/articles/road-land-can-build-house.html',
  '/首頁/f/道路用地可以蓋房子嗎？資深地政專家教你破解公共設施保留地的5大迷思': '/blog/articles/road-land-can-build-house.html',

  // 2. 道路用地可以圍起來嗎（GSC 歷史點擊 283）
  '/f/道路用地可以圍起來嗎？': '/blog/articles/road-land-fencing-rules.html',
  '/首頁/f/道路用地可以圍起來嗎？': '/blog/articles/road-land-fencing-rules.html',
  '/f/道路用地可以圍起來嗎': '/blog/articles/road-land-fencing-rules.html',
  '/首頁/f/道路用地可以圍起來嗎': '/blog/articles/road-land-fencing-rules.html',

  // 3. 馬路學問大!私設/既成/計畫道路差異（GSC 歷史點擊 278）
  '/f/馬路學問大！3分鐘看懂「私設既成計畫道路」差在哪裡': '/blog/articles/road-types-distinction.html',
  '/首頁/f/馬路學問大！3分鐘看懂「私設既成計畫道路」差在哪裡': '/blog/articles/road-types-distinction.html',
  '/f/馬路學問大！3分鐘看懂「私設/既成/計畫道路」差在哪裡': '/blog/articles/road-types-distinction.html',
  '/首頁/f/馬路學問大！3分鐘看懂「私設/既成/計畫道路」差在哪裡': '/blog/articles/road-types-distinction.html',

  // 4. 建地臨接未開闢計畫道路（GSC 歷史點擊 266）
  '/f/建地臨接「未開闢都市計畫道路」，可申請興建嗎？': '/blog/articles/build-near-unopened-planned-road.html',
  '/首頁/f/建地臨接「未開闢都市計畫道路」，可申請興建嗎？': '/blog/articles/build-near-unopened-planned-road.html',
  '/f/建地臨接未開闢都市計畫道路可申請興建嗎': '/blog/articles/build-near-unopened-planned-road.html',
  '/首頁/f/建地臨接未開闢都市計畫道路可申請興建嗎': '/blog/articles/build-near-unopened-planned-road.html',

  // 5. 道路用地公告現值全攻略（GSC 歷史點擊 230）
  '/f/道路用地公告現值全攻略｜看懂政府估價眉角，避免吃虧的7大重點': '/blog/articles/road-land-public-value-guide.html',
  '/首頁/f/道路用地公告現值全攻略｜看懂政府估價眉角，避免吃虧的7大重點': '/blog/articles/road-land-public-value-guide.html',
  '/f/道路用地公告現值全攻略看懂政府估價眉角避免吃虧的7大重點': '/blog/articles/road-land-public-value-guide.html',
  '/首頁/f/道路用地公告現值全攻略看懂政府估價眉角避免吃虧的7大重點': '/blog/articles/road-land-public-value-guide.html',

  // 6. 公共設施保留地完全攻略（GSC 歷史點擊 144）
  '/f/公共設施保留地完全攻略：從定義到活用一次看懂': '/blog/articles/public-facility-reserved-land-complete-guide.html',
  '/首頁/f/公共設施保留地完全攻略：從定義到活用一次看懂': '/blog/articles/public-facility-reserved-land-complete-guide.html',
  '/f/公共設施保留地完全攻略從定義到活用一次看懂': '/blog/articles/public-facility-reserved-land-complete-guide.html',
  '/首頁/f/公共設施保留地完全攻略從定義到活用一次看懂': '/blog/articles/public-facility-reserved-land-complete-guide.html',

  // 7. 道路用地抵稅終極攻略（GSC 歷史點擊 122）
  '/f/《道路用地抵稅終極攻略》——從法條解析到實戰操作的7大關鍵指南': '/blog/articles/road-land-tax-offset-guide.html',
  '/首頁/f/《道路用地抵稅終極攻略》——從法條解析到實戰操作的7大關鍵指南': '/blog/articles/road-land-tax-offset-guide.html',
  '/f/道路用地抵稅終極攻略從法條解析到實戰操作的7大關鍵指南': '/blog/articles/road-land-tax-offset-guide.html',
  '/首頁/f/道路用地抵稅終極攻略從法條解析到實戰操作的7大關鍵指南': '/blog/articles/road-land-tax-offset-guide.html',

  // 8. 公保地 vs 公設用地差異（GSC 歷史點擊 117）
  '/f/【超圖解】買地前必看！公共設施保留地-vs-公共設施用地—搞懂這3大差異才不會吃虧': '/blog/articles/reserved-vs-used-public-facility-land.html',
  '/首頁/f/【超圖解】買地前必看！公共設施保留地-vs-公共設施用地—搞懂這3大差異才不會吃虧': '/blog/articles/reserved-vs-used-public-facility-land.html',
  '/f/超圖解買地前必看公共設施保留地vs公共設施用地搞懂這3大差異才不會吃虧': '/blog/articles/reserved-vs-used-public-facility-land.html',
  '/首頁/f/超圖解買地前必看公共設施保留地vs公共設施用地搞懂這3大差異才不會吃虧': '/blog/articles/reserved-vs-used-public-facility-land.html',

  // ===== Batch 3 三七五+祭祀公業主題（2026-04-22 新增） =====
  // 1. 三七五減租廢除了嗎（GSC 歷史點擊 566 - Batch 3 最高）
  '/f/三七五減租廢除了嗎？': '/blog/articles/is-375-rent-reduction-abolished.html',
  '/首頁/f/三七五減租廢除了嗎？': '/blog/articles/is-375-rent-reduction-abolished.html',
  '/f/三七五減租廢除了嗎': '/blog/articles/is-375-rent-reduction-abolished.html',
  '/首頁/f/三七五減租廢除了嗎': '/blog/articles/is-375-rent-reduction-abolished.html',
  '/f/三七五減租已經廢除了嗎？': '/blog/articles/is-375-rent-reduction-abolished.html',
  '/首頁/f/三七五減租已經廢除了嗎？': '/blog/articles/is-375-rent-reduction-abolished.html',

  // 2. 三七五減租懶人包（GSC 歷史點擊 159）
  '/f/三七五減租懶人包：讓您輕鬆了解最新規定': '/blog/articles/375-rent-reduction-easy-guide.html',
  '/首頁/f/三七五減租懶人包：讓您輕鬆了解最新規定': '/blog/articles/375-rent-reduction-easy-guide.html',
  '/f/三七五減租懶人包讓您輕鬆了解最新規定': '/blog/articles/375-rent-reduction-easy-guide.html',
  '/首頁/f/三七五減租懶人包讓您輕鬆了解最新規定': '/blog/articles/375-rent-reduction-easy-guide.html',

  // 3. 三七五減租釋憲解析（GSC 歷史點擊 113）
  '/f/耕地三七五減租條例釋憲解析：地主收回土地的關鍵轉折': '/blog/articles/375-constitutional-interpretation.html',
  '/首頁/f/耕地三七五減租條例釋憲解析：地主收回土地的關鍵轉折': '/blog/articles/375-constitutional-interpretation.html',
  '/f/耕地三七五減租條例釋憲解析地主收回土地的關鍵轉折': '/blog/articles/375-constitutional-interpretation.html',
  '/首頁/f/耕地三七五減租條例釋憲解析地主收回土地的關鍵轉折': '/blog/articles/375-constitutional-interpretation.html',

  // 4. 三七五租約糾紛處理（GSC 歷史點擊 91）
  '/f/三七五租約糾紛處理全攻略：從調解到強制執行的完整指南': '/blog/articles/375-tenancy-dispute-guide.html',
  '/首頁/f/三七五租約糾紛處理全攻略：從調解到強制執行的完整指南': '/blog/articles/375-tenancy-dispute-guide.html',
  '/f/三七五租約糾紛處理全攻略從調解到強制執行的完整指南': '/blog/articles/375-tenancy-dispute-guide.html',
  '/首頁/f/三七五租約糾紛處理全攻略從調解到強制執行的完整指南': '/blog/articles/375-tenancy-dispute-guide.html',

  // 5. 祭祀公業與神明會土地實戰（GSC 歷史點擊 79）
  '/f/搞懂祭祀公業與神明會土地的實戰指南': '/blog/articles/ancestral-land-shrine-guide.html',
  '/首頁/f/搞懂祭祀公業與神明會土地的實戰指南': '/blog/articles/ancestral-land-shrine-guide.html',

  // 6. 祭祀公業土地標售全攻略（GSC 歷史點擊 74）
  '/f/《祭祀公業土地標售全攻略》——從法條解密到實戰操作的7大關鍵步驟': '/blog/articles/ancestral-land-auction-guide.html',
  '/首頁/f/《祭祀公業土地標售全攻略》——從法條解密到實戰操作的7大關鍵步驟': '/blog/articles/ancestral-land-auction-guide.html',
  '/f/祭祀公業土地標售全攻略從法條解密到實戰操作的7大關鍵步驟': '/blog/articles/ancestral-land-auction-guide.html',
  '/首頁/f/祭祀公業土地標售全攻略從法條解密到實戰操作的7大關鍵步驟': '/blog/articles/ancestral-land-auction-guide.html',

  // 7. 祭祀公業完全解鎖手冊（GSC 歷史點擊 47）
  '/f/《祭祀公業完全解鎖手冊》——從百年祖產到現代管理的5大關鍵策略': '/blog/articles/ancestral-land-complete-manual.html',
  '/首頁/f/《祭祀公業完全解鎖手冊》——從百年祖產到現代管理的5大關鍵策略': '/blog/articles/ancestral-land-complete-manual.html',
  '/f/祭祀公業完全解鎖手冊從百年祖產到現代管理的5大關鍵策略': '/blog/articles/ancestral-land-complete-manual.html',
  '/首頁/f/祭祀公業完全解鎖手冊從百年祖產到現代管理的5大關鍵策略': '/blog/articles/ancestral-land-complete-manual.html',

  // 8. 神明會土地交易解密（GSC 歷史點擊 44）
  '/f/神明會土地交易解密': '/blog/articles/shrine-association-land-trading.html',
  '/首頁/f/神明會土地交易解密': '/blog/articles/shrine-association-land-trading.html',

  // ===== Batch 4a 多元主題（2026-04-22 新增） =====
  // 1. 農地解除套繪管制（GSC 歷史點擊 274）
  '/f/農地解除套繪管制全攻略｜20年土地開發專家教你搞懂關鍵步驟': '/blog/articles/farm-land-annex-release-guide.html',
  '/首頁/f/農地解除套繪管制全攻略｜20年土地開發專家教你搞懂關鍵步驟': '/blog/articles/farm-land-annex-release-guide.html',
  '/f/農地解除套繪管制全攻略20年土地開發專家教你搞懂關鍵步驟': '/blog/articles/farm-land-annex-release-guide.html',

  // 2. 什麼土地可以蓋民宿（GSC 歷史點擊 263）
  '/f/什麼樣的土地可以用來蓋民宿？': '/blog/articles/which-land-for-bnb.html',
  '/首頁/f/什麼樣的土地可以用來蓋民宿？': '/blog/articles/which-land-for-bnb.html',
  '/f/什麼樣的土地可以用來蓋民宿': '/blog/articles/which-land-for-bnb.html',
  '/首頁/f/什麼樣的土地可以用來蓋民宿': '/blog/articles/which-land-for-bnb.html',

  // 3. 繼承農地補稅指南（GSC 歷史點擊 247）
  '/f/繼承農地補稅指南｜搞懂這些規定免花冤枉錢（2025最新版）': '/blog/articles/inherit-farm-land-tax-guide.html',
  '/首頁/f/繼承農地補稅指南｜搞懂這些規定免花冤枉錢（2025最新版）': '/blog/articles/inherit-farm-land-tax-guide.html',
  '/f/繼承農地補稅指南搞懂這些規定免花冤枉錢2025最新版': '/blog/articles/inherit-farm-land-tax-guide.html',

  // 4. 未保存登記建物（GSC 歷史點擊 220）
  '/f/未保存登記建物是什麼？會被拆嗎？專家帶你一次看懂所有權與補登流程': '/blog/articles/unregistered-building.html',
  '/首頁/f/未保存登記建物是什麼？會被拆嗎？專家帶你一次看懂所有權與補登流程': '/blog/articles/unregistered-building.html',
  '/f/未保存登記建物是什麼會被拆嗎專家帶你一次看懂所有權與補登流程': '/blog/articles/unregistered-building.html',

  // 5. 長輩土地詐騙（GSC 歷史點擊 202）
  '/f/長輩名下土地最易出事？詐騙怎樣下手你知道嗎？': '/blog/articles/elder-land-fraud-prevention.html',
  '/首頁/f/長輩名下土地最易出事？詐騙怎樣下手你知道嗎？': '/blog/articles/elder-land-fraud-prevention.html',
  '/f/長輩名下土地最易出事詐騙怎樣下手你知道嗎': '/blog/articles/elder-land-fraud-prevention.html',

  // 6. 農地農舍移轉懶人包（GSC 歷史點擊 194）
  '/f/農地農舍移轉懶人包｜帶您看懂關鍵眉角': '/blog/articles/farm-land-house-transfer-guide.html',
  '/首頁/f/農地農舍移轉懶人包｜帶您看懂關鍵眉角': '/blog/articles/farm-land-house-transfer-guide.html',
  '/f/農地農舍移轉懶人包帶您看懂關鍵眉角': '/blog/articles/farm-land-house-transfer-guide.html',

  // 7. 地價稅調漲全解析(GSC 歷史點擊 152）
  '/f/地價稅調漲全解析：六種情境看懂你的稅單為何變貴': '/blog/articles/land-value-tax-increase.html',
  '/首頁/f/地價稅調漲全解析：六種情境看懂你的稅單為何變貴': '/blog/articles/land-value-tax-increase.html',
  '/f/地價稅調漲全解析六種情境看懂你的稅單為何變貴': '/blog/articles/land-value-tax-increase.html',

  // 8. 贈與農地給子女（GSC 歷史點擊 136）
  '/f/贈與農地給子女：直接贈與和信託有什麼不同？怎樣才能免繳贈與稅？': '/blog/articles/gift-farm-land-to-children.html',
  '/首頁/f/贈與農地給子女：直接贈與和信託有什麼不同？怎樣才能免繳贈與稅？': '/blog/articles/gift-farm-land-to-children.html',
  '/f/贈與農地給子女直接贈與和信託有什麼不同怎樣才能免繳贈與稅': '/blog/articles/gift-farm-land-to-children.html',

  // ===== Batch 4b 多元主題 後半 7 篇（2026-04-22 新增） =====
  // 1. 查土地所有人（GSC 歷史點擊 121）
  '/f/三分鐘教你查清楚：土地真正的所有人是誰': '/blog/articles/land-owner-lookup-guide.html',
  '/首頁/f/三分鐘教你查清楚：土地真正的所有人是誰': '/blog/articles/land-owner-lookup-guide.html',
  '/f/三分鐘教你查清楚土地真正的所有人是誰': '/blog/articles/land-owner-lookup-guide.html',

  // 2. 都市計畫綠地（GSC 歷史點擊 108）
  '/f/都市計畫綠地是什麼？完整解析綠地土地使用限制、可用範圍與違規風險！': '/blog/articles/urban-green-land-guide.html',
  '/首頁/f/都市計畫綠地是什麼？完整解析綠地土地使用限制、可用範圍與違規風險！': '/blog/articles/urban-green-land-guide.html',
  '/f/都市計畫綠地是什麼完整解析綠地土地使用限制可用範圍與違規風險': '/blog/articles/urban-green-land-guide.html',

  // 3. 既成道路地主權利（GSC 歷史點擊 98）
  '/f/既成道路地主權利全解析｜私人土地變「公用路」後，你該知道的真相！！': '/blog/articles/existing-road-landowner-rights.html',
  '/首頁/f/既成道路地主權利全解析｜私人土地變「公用路」後，你該知道的真相！！': '/blog/articles/existing-road-landowner-rights.html',
  '/f/既成道路地主權利全解析私人土地變公用路後你該知道的真相': '/blog/articles/existing-road-landowner-rights.html',

  // 4. 土地增值稅免徵（GSC 歷史點擊 91）
  '/f/土地增值稅免徵範圍全解析：輕鬆搞懂哪些情況不用繳稅': '/blog/articles/land-value-increment-tax-exemption.html',
  '/首頁/f/土地增值稅免徵範圍全解析：輕鬆搞懂哪些情況不用繳稅': '/blog/articles/land-value-increment-tax-exemption.html',
  '/f/土地增值稅免徵範圍全解析輕鬆搞懂哪些情況不用繳稅': '/blog/articles/land-value-increment-tax-exemption.html',

  // 5. 法定空地（GSC 歷史點擊 90）
  '/f/認識法定空地：建築用地中不可忽略的隱形規定': '/blog/articles/statutory-open-space.html',
  '/首頁/f/認識法定空地：建築用地中不可忽略的隱形規定': '/blog/articles/statutory-open-space.html',
  '/f/認識法定空地建築用地中不可忽略的隱形規定': '/blog/articles/statutory-open-space.html',

  // 6. 地上權移轉登記（GSC 歷史點擊 89）
  '/f/地上權移轉登記全攻略：從基礎概念到實務操作一次搞懂': '/blog/articles/land-superficies-transfer.html',
  '/首頁/f/地上權移轉登記全攻略：從基礎概念到實務操作一次搞懂': '/blog/articles/land-superficies-transfer.html',
  '/f/地上權移轉登記全攻略從基礎概念到實務操作一次搞懂': '/blog/articles/land-superficies-transfer.html',

  // 7. 持分土地強制分割（GSC 歷史點擊 85）
  '/f/持分土地能強制分割嗎？法院裁定的可能結果分析': '/blog/articles/co-ownership-forced-partition.html',
  '/首頁/f/持分土地能強制分割嗎？法院裁定的可能結果分析': '/blog/articles/co-ownership-forced-partition.html',
  '/f/持分土地能強制分割嗎法院裁定的可能結果分析': '/blog/articles/co-ownership-forced-partition.html',

  // ===== Batch 5 Tier 2 TOP 15（2026-04-22 新增,Phase 6 最終篇） =====
  // 1. 分別共有買賣(82)
  '/f/土地分別共有買賣解決方式': '/blog/articles/fenbie-co-ownership-sale-solutions.html',
  '/首頁/f/土地分別共有買賣解決方式': '/blog/articles/fenbie-co-ownership-sale-solutions.html',

  // 2. 神明名義土地(82)
  '/f/關於「神明名義土地」的疑難雜症': '/blog/articles/shrine-name-land-issues.html',
  '/首頁/f/關於「神明名義土地」的疑難雜症': '/blog/articles/shrine-name-land-issues.html',
  '/f/關於神明名義土地的疑難雜症': '/blog/articles/shrine-name-land-issues.html',

  // 3. 持分土地怎麼賣(81)
  '/f/持分土地怎麼賣最划算？自售-vs-找投資客的優缺點': '/blog/articles/partial-land-best-selling-strategy.html',
  '/首頁/f/持分土地怎麼賣最划算？自售-vs-找投資客的優缺點': '/blog/articles/partial-land-best-selling-strategy.html',
  '/f/持分土地怎麼賣最划算自售vs找投資客的優缺點': '/blog/articles/partial-land-best-selling-strategy.html',

  // 4. 持分土地抵押貸款(81)
  '/f/持分土地可以抵押貸款嗎？銀行放貸條件解析': '/blog/articles/partial-land-mortgage-loan.html',
  '/首頁/f/持分土地可以抵押貸款嗎？銀行放貸條件解析': '/blog/articles/partial-land-mortgage-loan.html',
  '/f/持分土地可以抵押貸款嗎銀行放貸條件解析': '/blog/articles/partial-land-mortgage-loan.html',

  // 5. 人人都能買農地(79)
  '/f/人人都能買農地，不只是農民的專利': '/blog/articles/anyone-can-buy-farm-land.html',
  '/首頁/f/人人都能買農地，不只是農民的專利': '/blog/articles/anyone-can-buy-farm-land.html',
  '/f/人人都能買農地不只是農民的專利': '/blog/articles/anyone-can-buy-farm-land.html',

  // 6. 道路用地公告現值查詢(79)
  '/f/道路用地公告現值怎麼查？地政專家教你3分鐘搞懂查詢訣竅5大實戰案例': '/blog/articles/road-land-value-lookup-guide.html',
  '/首頁/f/道路用地公告現值怎麼查？地政專家教你3分鐘搞懂查詢訣竅5大實戰案例': '/blog/articles/road-land-value-lookup-guide.html',
  '/f/道路用地公告現值怎麼查地政專家教你3分鐘搞懂查詢訣竅5大實戰案例': '/blog/articles/road-land-value-lookup-guide.html',

  // 7. 分管契約(77)
  '/f/分管契約、分管決定到底是什麼？教你用簡單方式搞懂持分土地的管理': '/blog/articles/partition-agreement-guide.html',
  '/首頁/f/分管契約、分管決定到底是什麼？教你用簡單方式搞懂持分土地的管理': '/blog/articles/partition-agreement-guide.html',
  '/f/分管契約分管決定到底是什麼教你用簡單方式搞懂持分土地的管理': '/blog/articles/partition-agreement-guide.html',

  // 8. 買方詐騙新招(77)
  '/f/買方詐騙新招：假買家、真詐騙，如何識破？': '/blog/articles/fake-buyer-fraud-tactics.html',
  '/首頁/f/買方詐騙新招：假買家、真詐騙，如何識破？': '/blog/articles/fake-buyer-fraud-tactics.html',
  '/f/買方詐騙新招假買家真詐騙如何識破': '/blog/articles/fake-buyer-fraud-tactics.html',

  // 9. 土地被查封(73)
  '/f/土地被查封竟不知情？防範法院拍賣詐騙有撇步': '/blog/articles/land-seizure-fraud-prevention.html',
  '/首頁/f/土地被查封竟不知情？防範法院拍賣詐騙有撇步': '/blog/articles/land-seizure-fraud-prevention.html',
  '/f/土地被查封竟不知情防範法院拍賣詐騙有撇步': '/blog/articles/land-seizure-fraud-prevention.html',

  // 10. 道路用地停車場(72)
  '/f/道路用地可以做停車場嗎？': '/blog/articles/road-land-as-parking-lot.html',
  '/首頁/f/道路用地可以做停車場嗎？': '/blog/articles/road-land-as-parking-lot.html',
  '/f/道路用地可以做停車場嗎': '/blog/articles/road-land-as-parking-lot.html',

  // 11. 親戚詐騙(66)
  '/f/親戚也會騙？揭秘假委託書賣地手法': '/blog/articles/relative-fraud-fake-authorization.html',
  '/首頁/f/親戚也會騙？揭秘假委託書賣地手法': '/blog/articles/relative-fraud-fake-authorization.html',
  '/f/親戚也會騙揭秘假委託書賣地手法': '/blog/articles/relative-fraud-fake-authorization.html',

  // 12. 低價收購詐騙(65)
  '/f/聲稱「低價收購土地」的是詐騙嗎？這樣判斷最安全': '/blog/articles/low-price-offer-fraud-warning.html',
  '/首頁/f/聲稱「低價收購土地」的是詐騙嗎？這樣判斷最安全': '/blog/articles/low-price-offer-fraud-warning.html',
  '/f/聲稱低價收購土地的是詐騙嗎這樣判斷最安全': '/blog/articles/low-price-offer-fraud-warning.html',

  // 13. 非都市計畫道路用地(58)
  '/f/非都市計畫之道路用地': '/blog/articles/non-urban-road-land.html',
  '/首頁/f/非都市計畫之道路用地': '/blog/articles/non-urban-road-land.html',

  // 14. 繼承農地免遺產稅(56)
  '/f/繼承農地符合哪些條件可免課遺產稅？': '/blog/articles/inherit-farm-land-estate-tax-exemption.html',
  '/首頁/f/繼承農地符合哪些條件可免課遺產稅？': '/blog/articles/inherit-farm-land-estate-tax-exemption.html',
  '/f/繼承農地符合哪些條件可免課遺產稅': '/blog/articles/inherit-farm-land-estate-tax-exemption.html',

  // 15. 地籍清理代為標售(56)
  '/f/地籍清理代為標售懶人包｜一次搞懂政府幫你賣土地的流程': '/blog/articles/cadastral-cleanup-auction-guide.html',
  '/首頁/f/地籍清理代為標售懶人包｜一次搞懂政府幫你賣土地的流程': '/blog/articles/cadastral-cleanup-auction-guide.html',
  '/f/地籍清理代為標售懶人包一次搞懂政府幫你賣土地的流程': '/blog/articles/cadastral-cleanup-auction-guide.html',

  // ===== Batch 10 持分土地深度型(2026-04-23 新增 8 篇)=====
  // 1. 持分土地稅務完整試算
  '/f/持分土地賣掉要繳多少稅': '/blog/articles/partial-land-tax-complete-calculation.html',
  '/首頁/f/持分土地賣掉要繳多少稅': '/blog/articles/partial-land-tax-complete-calculation.html',
  '/f/持分土地稅怎麼算': '/blog/articles/partial-land-tax-complete-calculation.html',

  // 2. 共有人失聯 4 解方
  '/f/共有人失聯怎麼辦': '/blog/articles/partial-land-disappeared-owner-solutions.html',
  '/首頁/f/共有人失聯怎麼辦': '/blog/articles/partial-land-disappeared-owner-solutions.html',
  '/f/持分土地共有人找不到': '/blog/articles/partial-land-disappeared-owner-solutions.html',

  // 3. 雙北 GEO 行情
  '/f/雙北持分土地行情': '/blog/articles/partial-land-taipei-newtaipei-market-2026.html',
  '/首頁/f/雙北持分土地行情': '/blog/articles/partial-land-taipei-newtaipei-market-2026.html',
  '/f/台北持分土地價格': '/blog/articles/partial-land-taipei-newtaipei-market-2026.html',

  // 4. 土地被占用訴訟
  '/f/持分土地被占用怎麼辦': '/blog/articles/partial-land-occupied-lawsuit-sop.html',
  '/首頁/f/持分土地被占用怎麼辦': '/blog/articles/partial-land-occupied-lawsuit-sop.html',
  '/f/土地被占用訴訟': '/blog/articles/partial-land-occupied-lawsuit-sop.html',

  // 5. 法院拍賣完整指南
  '/f/持分土地法院拍賣': '/blog/articles/partial-land-court-auction-guide.html',
  '/首頁/f/持分土地法院拍賣': '/blog/articles/partial-land-court-auction-guide.html',
  '/f/持分土地法拍': '/blog/articles/partial-land-court-auction-guide.html',

  // 6. 詐騙 7 大手法
  '/f/持分土地詐騙': '/blog/articles/partial-land-scam-7-patterns-alert.html',
  '/首頁/f/持分土地詐騙': '/blog/articles/partial-land-scam-7-patterns-alert.html',
  '/f/土地買賣詐騙手法': '/blog/articles/partial-land-scam-7-patterns-alert.html',

  // 7. 優先購買權 15 天時效
  '/f/優先購買權時效': '/blog/articles/partial-land-priority-right-timeline-expiry.html',
  '/首頁/f/優先購買權時效': '/blog/articles/partial-land-priority-right-timeline-expiry.html',
  '/f/優先購買權15天': '/blog/articles/partial-land-priority-right-timeline-expiry.html',

  // 8. 兩岸三地繼承持分
  '/f/兩岸繼承持分土地': '/blog/articles/partial-land-cross-strait-inheritance-process.html',
  '/首頁/f/兩岸繼承持分土地': '/blog/articles/partial-land-cross-strait-inheritance-process.html',
  '/f/陸配繼承台灣土地': '/blog/articles/partial-land-cross-strait-inheritance-process.html',
};

// ============================================
// 關鍵字分類規則：依文章標題自動分派到最相關頁面
// 順序重要：特異性高的放前面
// ============================================
const KEYWORD_RULES = [
  // 三七五租約
  {
    keywords: ['三七五', '375', '減租', '佃農', '耕地租佃'],
    target: '/pages/tenancy-375.html',
  },
  // 容積移轉
  {
    keywords: ['容積移轉', '容積率', '送出基地', '接受基地', '容積代金'],
    target: '/pages/floor-area-ratio.html',
  },
  // 公同共有（注意：要比「持分/共有」先檢查）
  {
    keywords: ['公同共有', '派下員'],
    target: '/pages/joint-ownership.html',
  },
  // 祭祀公業
  {
    keywords: ['祭祀公業', '神明會', '祭田'],
    target: '/pages/ancestral-land.html',
  },
  // 持分
  {
    keywords: ['持分', '分別共有', '持份', '應有部分', '鑑界'],
    target: '/pages/co-ownership.html',
  },
  // 重劃
  {
    keywords: ['重劃', '區段徵收'],
    target: '/pages/rezoning-land.html',
  },
  // 兩岸繼承
  {
    keywords: ['兩岸', '大陸繼承', '日據繼承', '日治', '港澳'],
    target: '/pages/cross-strait-inheritance.html',
  },
  // 道路用地
  {
    keywords: [
      '道路用地', '既成道路', '計畫道路', '公設保留地', '公共設施保留地',
      '馬路', '巷道', '公告現值', '徵收', '容積獎勵', '私設道路',
      '都市計畫道路', '浮覆地',
    ],
    target: '/pages/road-land.html',
  },
  // 農地 / 繼承 / 地籍 / 稅務 → blog 首頁
  {
    keywords: ['農地', '農舍', '自地自建', '未辦繼承', '逾期繼承'],
    target: '/blog/index.html',
  },
  {
    keywords: ['地籍清理', '未保存登記', '地上權', '建築套繪'],
    target: '/blog/index.html',
  },
  {
    keywords: ['地價稅', '贈與稅', '遺產稅', '土地稅', '節稅'],
    target: '/blog/index.html',
  },
  // 一般共有、土地買賣、建物類
  {
    keywords: ['共有', '土地買賣', '過戶', '蓋房子', '蓋民宿', '建地', '綠地'],
    target: '/pages/co-ownership.html',
  },
];

/**
 * 依路徑判斷轉址目標
 * @param {string} pathname - 解碼後的 URL 路徑
 * @returns {string|null} - 目標新路徑；若不需轉址回傳 null
 */
function getRedirectTarget(pathname) {
  // 去掉結尾的 /（根路徑除外）
  const path = pathname.length > 1 ? pathname.replace(/\/+$/, '') : pathname;

  // 1. 精確對應表
  if (EXACT_REDIRECTS[path]) {
    return EXACT_REDIRECTS[path];
  }

  // 1.5. 根目錄舊命名 HTML 檔（Phase 1 deduplication）
  if (LEGACY_FILE_REDIRECTS[path]) {
    return LEGACY_FILE_REDIRECTS[path];
  }

  // 2. 文章頁格式：/f/[標題] 或 /首頁/f/[標題]
  let articleTitle = null;
  if (path.startsWith('/首頁/f/')) {
    articleTitle = path.slice('/首頁/f/'.length);
  } else if (path.startsWith('/f/')) {
    articleTitle = path.slice('/f/'.length);
  }

  if (articleTitle) {
    // 先檢查精確文章對應（Phase 6）
    if (ARTICLE_PRECISE_REDIRECTS[path]) {
      return ARTICLE_PRECISE_REDIRECTS[path];
    }
    // 依關鍵字判定
    for (const rule of KEYWORD_RULES) {
      for (const kw of rule.keywords) {
        if (articleTitle.includes(kw)) {
          return rule.target;
        }
      }
    }
    // 文章但無法分類 → blog 首頁
    return '/blog/index.html';
  }

  // 3. 不是已知舊 URL 格式，不轉址
  return null;
}

/**
 * Worker 主入口
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // decodeURIComponent 會把 URL 裡的 %E3%80%... 轉回中文，方便比對
    let pathname;
    try {
      pathname = decodeURIComponent(url.pathname);
    } catch {
      // 如果 decode 失敗（URL 編碼壞掉），直接用原始路徑
      pathname = url.pathname;
    }

    // 判斷是否需要 301
    const target = getRedirectTarget(pathname);

    if (target) {
      // 建立新 URL（保留 query string 和 hash）
      const newUrl = new URL(target, url.origin);
      if (url.search) newUrl.search = url.search;

      return Response.redirect(newUrl.toString(), 301);
    }

    // 不需要轉址，交給 Cloudflare 靜態資產系統處理
    // env.ASSETS 是 Cloudflare Static Assets 綁定
    return env.ASSETS.fetch(request);
  },
};
