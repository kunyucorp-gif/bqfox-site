// Scroll reveal
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if(e.isIntersecting){ e.target.classList.add('visible'); obs.unobserve(e.target) } })
}, { threshold:0.07, rootMargin:'0px 0px -40px 0px' });
document.querySelectorAll('.rv,.rv-l').forEach(el => obs.observe(el));

// Nav scroll
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => nav?.classList.toggle('scrolled', scrollY > 50), {passive:true});

// FAQ accordion
document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.closest('.faq-item');
    const open = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
    if(!open) item.classList.add('open');
  });
});

// Hamburger
const hbtn = document.getElementById('hbtn');
const mob = document.getElementById('mobMenu');
hbtn?.addEventListener('click', () => { hbtn.classList.toggle('open'); mob?.classList.toggle('open') });
document.getElementById('mobClose')?.addEventListener('click', () => { hbtn?.classList.remove('open'); mob?.classList.remove('open') });
mob?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { hbtn?.classList.remove('open'); mob?.classList.remove('open') }));

// Form
// ══ CONTACT FORM — Formspree integration ══
// Replace YOUR_FORM_ID below with your Formspree form ID
// Setup: formspree.io → New Form → copy the ID (e.g. xabcdefg)
const FORMSPREE_ID = 'myklkqrv';

document.getElementById('formSubmit')?.addEventListener('click', async () => {
  const name    = document.getElementById('fname')?.value?.trim();
  const phone   = document.getElementById('fphone')?.value?.trim();
  const email   = document.getElementById('femail')?.value?.trim();
  const service = document.getElementById('fservice')?.value;
  const message = document.getElementById('fmsg')?.value?.trim();

  if (!name || !phone) {
    alert('請填寫姓名與聯絡電話');
    return;
  }

  const btn  = document.getElementById('formSubmit');
  const span = btn.querySelector('span');
  btn.disabled = true;
  span.textContent = '傳送中…';

  // If Formspree ID not yet set, use mailto fallback
  if (FORMSPREE_ID === 'YOUR_FORM_ID') {
    const subject = encodeURIComponent(`【寶璣建設諮詢】${service || '土地諮詢'} — ${name}`);
    const body    = encodeURIComponent(
      `姓名：${name}\n聯絡電話：${phone}\n電子郵件：${email || '（未填）'}\n諮詢項目：${service || '（未選）'}\n\n問題描述：\n${message || '（未填）'}`
    );
    window.location.href = `mailto:baiqicorp888@gmail.com?subject=${subject}&body=${body}`;
    span.textContent = '✓ 開啟郵件應用程式';
    btn.style.background = 'linear-gradient(135deg,#2a7a3b,#4caf50)';
    return;
  }

  try {
    const res = await fetch(`https://formspree.io/f/${FORMSPREE_ID}`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        姓名: name,
        電話: phone,
        信箱: email   || '（未填）',
        項目: service || '（未選）',
        描述: message || '（未填）',
        _subject: `【寶璣建設諮詢】${service || '土地諮詢'} — ${name}`,
        _replyto: email || ''
      })
    });

    if (res.ok) {
      span.textContent    = '✓ 已送出，我們將盡快與您聯繫！';
      btn.style.background = 'linear-gradient(135deg,#2a7a3b,#4caf50)';
      // Clear form
      ['fname','fphone','femail','fmsg'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      const sel = document.getElementById('fservice');
      if (sel) sel.selectedIndex = 0;
    } else {
      throw new Error('送出失敗');
    }
  } catch(e) {
    span.textContent = '送出失敗，請直接來電 02-2274-6789';
    btn.disabled = false;
    btn.style.background = '';
  }
});
