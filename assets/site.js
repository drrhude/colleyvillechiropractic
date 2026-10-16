/* Jane booking links. New patients (chiro + shockwave) = treatment 80,
   existing shockwave = 85. Every other treatment goes to the main booking page. */
const JANE = {
  base: "https://colleyvillechiropractic.janeapp.com/",
  newPatient: "https://colleyvillechiropractic.janeapp.com/#/discipline/1/treatment/80",
  chiro: "https://colleyvillechiropractic.janeapp.com/#/discipline/1/treatment/80",
  shockwave: "https://colleyvillechiropractic.janeapp.com/#/discipline/1/treatment/80",
  shockwaveExisting: "https://colleyvillechiropractic.janeapp.com/#/discipline/1/treatment/85",
  special: "https://colleyvillechiropractic.janeapp.com/#/discipline/1/treatment/80",
  existing: "", neuropath: "", rehab: "", massage: "", gut: "", recovery: ""  /* empty = main booking page */
};

/* Affiliate form: paste the GHL inbound webhook URL here (Automation > Workflow > Inbound Webhook trigger). */
const AFFILIATE_WEBHOOK = "";
document.querySelectorAll("[data-jane]").forEach(a=>{
  const url = JANE[a.dataset.jane] || JANE.base;
  a.href = url; a.target = "_blank"; a.rel = "noopener";
});
/* GHL member portal link for RESET / paid content */
const PORTAL = "https://resethybridrecovery.com/";
document.querySelectorAll("[data-portal]").forEach(a=>a.href = PORTAL);

const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* Header goes solid after the hero */
const header = document.querySelector("header.site");
const onScroll = () => {
  header.classList.toggle("solid", scrollY > 40);
  dock.classList.toggle("show", scrollY > innerHeight * .7);
  spineUpdate();
};

/* Mobile menu */
const menuBtn = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
menuBtn.addEventListener("click", () => {
  const open = menuBtn.getAttribute("aria-expanded") !== "true";
  menuBtn.setAttribute("aria-expanded", open);
  menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  nav.classList.toggle("open", open);
  header.classList.add("solid");
});
nav.querySelectorAll("a").forEach(a => a.addEventListener("click", () => {
  nav.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false");
}));

/* Reveal on scroll */
const io = new IntersectionObserver(entries => entries.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}), { threshold: .15, rootMargin: "0px 0px -6% 0px" });
document.querySelectorAll(".reveal").forEach((el, i) => {
  el.style.transitionDelay = (el.parentElement.querySelectorAll(":scope > .reveal").length > 1
    ? [...el.parentElement.children].indexOf(el) * 90 : 0) + "ms";
  io.observe(el);
});

/* Spine progress */
const spine = document.querySelector(".spine");
const fill = spine ? spine.querySelector(".fill") : null;
const nodes = spine ? [...spine.querySelectorAll("a")] : [];
const targets = nodes.map(n => document.querySelector(n.getAttribute("href")));
function spineUpdate(){
  if (!spine) return;
  const max = document.documentElement.scrollHeight - innerHeight;
  const p = Math.min(1, Math.max(0, scrollY / max));
  const track = spine.querySelector(".track").offsetHeight;
  fill.style.height = (p * track) + "px";
  let current = 0;
  targets.forEach((t, i) => { if (t && t.getBoundingClientRect().top < innerHeight * .45) current = i; });
  nodes.forEach((n, i) => { n.classList.toggle("on", i <= current); n.classList.toggle("here", i === current); });
}

/* Services tabs */
const tabs = [...document.querySelectorAll('[role="tab"]')];
function select(tab){
  tabs.forEach(t => {
    const on = t === tab;
    t.setAttribute("aria-selected", on); t.tabIndex = on ? 0 : -1;
    document.getElementById(t.getAttribute("aria-controls")).classList.toggle("active", on);
  });
}
tabs.forEach((t, i) => {
  t.addEventListener("click", () => select(t));
  t.addEventListener("keydown", e => {
    const k = e.key === "ArrowDown" || e.key === "ArrowRight" ? 1 : e.key === "ArrowUp" || e.key === "ArrowLeft" ? -1 : 0;
    if (k) { e.preventDefault(); const n = tabs[(i + k + tabs.length) % tabs.length]; n.focus(); select(n); }
  });
});

/* Count up the review numbers once */
const counters = document.querySelectorAll("[data-count]");
const cio = new IntersectionObserver(entries => entries.forEach(e => {
  if (!e.isIntersecting || reduce) return;
  const el = e.target, end = parseFloat(el.dataset.count), dec = el.dataset.count.includes(".") ? 1 : 0;
  const t0 = performance.now(), dur = 1400;
  const tick = now => {
    const k = Math.min(1, (now - t0) / dur), v = end * (1 - Math.pow(1 - k, 3));
    el.textContent = v.toFixed(dec);
    if (k < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick); cio.unobserve(el);
}), { threshold: .6 });
counters.forEach(c => cio.observe(c));


/* Rotating "Care for ___" word */
const words=["Families","Athletes","Kids","Expecting Moms","Grandparents","Weekend Warriors","Everyone"];
const rot=document.querySelector(".rot-word");
if(rot){
  let wi=0;
  const showLine=()=>{ if(words[wi]==="Everyone") rot.classList.add("show"); else rot.classList.remove("show"); };
  if(!reduce) setInterval(()=>{
    rot.classList.remove("in"); rot.classList.add("out");
    setTimeout(()=>{ wi=(wi+1)%words.length; rot.textContent=words[wi]; rot.classList.remove("out"); rot.classList.add("in"); showLine(); },430);
  },2200);
  else rot.textContent="Everyone";
}
/* Stagger tiles, icons and audience chips */
document.querySelectorAll(".choices .choice").forEach((c,i)=>{
  c.style.animationDelay=(i*110)+"ms";
  c.querySelectorAll(".ico *").forEach((p,j)=>p.style.animationDelay=(300+i*110+j*90)+"ms");
});
document.querySelectorAll(".audience li").forEach((l,i)=>l.style.transitionDelay=(350+i*80)+"ms");
const tio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("in");tio.unobserve(e.target);}}),{threshold:.15});
document.querySelectorAll(".choices").forEach(c=>tio.observe(c));

/* Highlight today's hours */
const today = new Date().getDay();
document.querySelector(`.hours tr[data-day="${today}"]`)?.classList.add("today");

/* Hide video if it fails to load so the gradient poster shows */
const vid = document.querySelector(".hero video");
if (vid) { vid.addEventListener("error", () => vid.remove(), true); if (reduce) { vid.removeAttribute("autoplay"); vid.pause(); } }

const dock = document.querySelector(".dock");
addEventListener("scroll", onScroll, { passive: true });
addEventListener("resize", spineUpdate);
onScroll();

/* FAQ accordions: animate open/close */
document.querySelectorAll(".faq details").forEach(d=>{
  const sum=d.querySelector("summary"), body=d.querySelector(".a");
  sum.addEventListener("click",e=>{
    if(reduce) return;
    e.preventDefault();
    if(d.open){
      const h=body.scrollHeight; body.style.height=h+"px";
      requestAnimationFrame(()=>{body.style.height="0px";});
      body.addEventListener("transitionend",()=>{d.open=false;body.style.height="";},{once:true});
    } else {
      d.open=true; const h=body.scrollHeight; body.style.height="0px";
      requestAnimationFrame(()=>{body.style.height=h+"px";});
      body.addEventListener("transitionend",()=>{body.style.height="";},{once:true});
    }
  });
});

/* Services dropdown: click/tap to toggle, hover on desktop, Esc and outside click close */
document.querySelectorAll(".has-menu").forEach(m=>{
  const btn=m.querySelector("button");
  const set=o=>{m.classList.toggle("open",o);btn.setAttribute("aria-expanded",o);};
  const desk=matchMedia("(min-width:981px) and (hover:hover)");
  btn.addEventListener("click",e=>{e.stopPropagation();set(desk.matches?true:!m.classList.contains("open"));});
  let t; m.addEventListener("mouseenter",()=>{if(desk.matches){clearTimeout(t);set(true);}});
  m.addEventListener("mouseleave",()=>{if(desk.matches){t=setTimeout(()=>set(false),180);}});
  document.addEventListener("click",e=>{if(!m.contains(e.target))set(false);});
  document.addEventListener("keydown",e=>{if(e.key==="Escape"){set(false);btn.focus();}});
});

/* Partner form: validate, send to GHL webhook, show confirmation */
const pform = document.getElementById("affiliate-form");
if (pform) {
  const msg = pform.querySelector(".form-msg");
  pform.addEventListener("input", e => e.target.classList.remove("bad"));
  pform.addEventListener("submit", async e => {
    e.preventDefault();
    let firstBad = null;
    pform.querySelectorAll("[required]").forEach(f => {
      const bad = f.type === "checkbox" ? !f.checked : !f.value.trim() || (f.type === "email" && !/^\S+@\S+\.\S+$/.test(f.value));
      f.classList.toggle("bad", bad); if (bad && !firstBad) firstBad = f;
    });
    if (firstBad) { msg.className = "form-msg err"; msg.textContent = "Please fill in the highlighted fields."; firstBad.focus(); return; }
    if (pform.company_url.value) return; /* spam trap */
    const fd = new FormData(pform);
    fd.set("interests", fd.getAll("interests").join(", "));
    fd.delete("company_url"); fd.set("source", "Website partner form"); fd.set("page", location.href);
    const btn = pform.querySelector("button"); btn.disabled = true; btn.textContent = "Sending...";
    try {
      if (!AFFILIATE_WEBHOOK) throw new Error("no webhook");
      await fetch(AFFILIATE_WEBHOOK, { method: "POST", mode: "no-cors", body: new URLSearchParams(fd) });
      pform.classList.add("done");
      pform.innerHTML = '<svg class="done-mark" viewBox="0 0 72 72" fill="none" stroke="#4A5040" stroke-width="2.5" aria-hidden="true"><circle cx="36" cy="36" r="34"/><path d="M23 37l9 9 17-19"/></svg><h3>Thanks, we got it.</h3><p style="color:var(--muted);max-width:36ch">We\'ll reach out within two business days. Questions sooner? Call or text (817) 420-7696.</p>';
    } catch (err) {
      btn.disabled = false; btn.textContent = "Send Application";
      msg.className = "form-msg err";
      msg.innerHTML = 'Something went wrong sending your application. Please call or text <a href="tel:+18174207696">(817) 420-7696</a>.';
    }
  });
}
