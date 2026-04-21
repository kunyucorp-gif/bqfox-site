/**
 * 寶璣建設 bqfox-site Worker
 *
 * 職責：
 *   1. 攔截 GoDaddy 時代的舊 URL（/三七五租約解約、/f/xxx 等）
 *   2. 301 轉址到現有新站的對應頁面（/pages/xxx.html）
 *   3. 其他請求交還給 Cloudflare 的靜態資產系統
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

  // 2. 文章頁格式：/f/[標題] 或 /首頁/f/[標題]
  let articleTitle = null;
  if (path.startsWith('/首頁/f/')) {
    articleTitle = path.slice('/首頁/f/'.length);
  } else if (path.startsWith('/f/')) {
    articleTitle = path.slice('/f/'.length);
  }

  if (articleTitle) {
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
