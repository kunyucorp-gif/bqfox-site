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
document.getElementById('formSubmit')?.addEventListener('click', () => {
  const n = document.getElementById('fname')?.value?.trim();
  const p = document.getElementById('fphone')?.value?.trim();
  if(!n || !p){ alert('請填寫姓名與聯絡電話'); return; }
  const btn = document.getElementById('formSubmit');
  btn.querySelector('span').textContent = '✓ 已送出，我們將盡快與您聯繫';
  btn.disabled = true; btn.style.background = 'linear-gradient(135deg,#2a7a3b,#4caf50)';
});
