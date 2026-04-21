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
// Phase 6 (Batch 1)：精確文章 URL → 新文章
// 舊的 /f/xxx 標題，精確轉到對應的新文章（優先於關鍵字規則）
// ============================================
const ARTICLE_PRECISE_REDIRECTS = {
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
  '/f/持分土地要怎麼定價？影響價格的關鍵因素一次看': '/blog/articles/co-ownership-pricing.html',
  '/首頁/f/持分土地要怎麼定價？影響價格的關鍵因素一次看': '/blog/articles/co-ownership-pricing.html',
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
