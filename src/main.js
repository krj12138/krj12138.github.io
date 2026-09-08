import "./style.css";
import { photoGroups } from "./photos-data.js";

/* ---------- 滚动渐现 ---------- */
const revealIO = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add("in");
        revealIO.unobserve(e.target);
      }
    });
  },
  { threshold: 0.12 }
);
document.querySelectorAll(".reveal").forEach((el) => revealIO.observe(el));

/* ---------- 导航 Scrollspy ---------- */
const navLinks = [...document.querySelectorAll(".nav-links a")];
const spySections = navLinks
  .map((a) => document.querySelector(a.getAttribute("href")))
  .filter(Boolean);

const spyIO = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        const id = e.target.id;
        navLinks.forEach((a) =>
          a.classList.toggle("active", a.getAttribute("href") === "#" + id)
        );
      }
    });
  },
  { rootMargin: "-40% 0px -55% 0px" }
);
spySections.forEach((s) => spyIO.observe(s));

/* ---------- 移动端菜单 ---------- */
const navToggle = document.getElementById("navToggle");
const navLinksEl = document.getElementById("navLinks");
navToggle.addEventListener("click", () => navLinksEl.classList.toggle("open"));
navLinksEl.addEventListener("click", (e) => {
  if (e.target.tagName === "A") navLinksEl.classList.remove("open");
});

/* ---------- 摄影专辑：三列联动轮播 ----------
   参考 tour-kyrgyzstan.com/#tours：
   左侧 = 照片名列表（当前项高亮）
   中间 = 大图，前后图半透明纵向往返流动（当前图带橙框）
   右侧 = 标题 / 日期 / 组注
   点击列表切换；点击当前大图打开灯箱。
------------------------------------------------- */
const phBlocks = document.getElementById("phBlocks");
const phCount = document.getElementById("phCount");

let groupStates = []; // { idx, photos }
let total = 0;

for (const group of photoGroups) {
  total += group.photos.length;

  const block = document.createElement("div");
  block.className = "ph-block reveal";

  const left = document.createElement("div");
  left.className = "ph-left";
  const head = document.createElement("div");
  head.className = "ph-group-head";
  head.innerHTML = `
    <div class="no">${String(group.no).padStart(2, "0")} / ${String(photoGroups.length).padStart(2, "0")}</div>
    <h3>${group.title}</h3>
    <div class="en">${group.en}</div>`;
  const pick = document.createElement("div");
  pick.className = "ph-pick";
  group.photos.forEach((p, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = p.title;
    b.addEventListener("click", () => selectPhoto(group.no - 1, i));
    b.addEventListener("mouseenter", () => selectPhoto(group.no - 1, i));
    pick.appendChild(b);
  });
  left.appendChild(head);
  left.appendChild(pick);

  const stage = document.createElement("div");
  stage.className = "ph-stage";
  group.photos.forEach((p) => {
    const s = document.createElement("div");
    s.className = "ph-slide";
    s.innerHTML = `<img src="${p.src}" alt="${p.title}" loading="lazy" /><span class="frame"></span>`;
    stage.appendChild(s);
  });
  stage.addEventListener("click", () => {
    const st = groupStates[group.no - 1];
    openLightbox(group, st.idx);
  });

  const info = document.createElement("div");
  info.className = "ph-info";
  info.innerHTML = `
    <div class="t"></div>
    <div class="m"></div>
    <div class="d"><b>${String(group.no).padStart(2, "0")} ·</b> 点击大图可全屏预览</div>
    ${group.note ? `<div class="note">“${group.note}”</div>` : ""}`;

  block.appendChild(left);
  block.appendChild(stage);
  block.appendChild(info);
  phBlocks.appendChild(block);

  groupStates.push({ idx: 0, photos: group.photos });
  renderBlock(group.no - 1);
}
phCount.textContent = "Featured · " + total + " Photos";

/* 动态渲染的元素补上渐现观察 */
phBlocks.querySelectorAll(".reveal:not(.in)").forEach((el) => revealIO.observe(el));

function selectPhoto(gi, i) {
  const st = groupStates[gi];
  if (!st || i === st.idx) return;
  st.idx = i;
  renderBlock(gi);
}

function renderBlock(gi) {
  const group = photoGroups[gi];
  const st = groupStates[gi];
  const block = phBlocks.children[gi];

  const buttons = [...block.querySelectorAll(".ph-pick button")];
  buttons.forEach((b, i) => b.classList.toggle("on", i === st.idx));

  const slides = [...block.querySelectorAll(".ph-slide")];
  const n = st.photos.length;
  slides.forEach((s, i) => {
    s.classList.remove("prev", "cur", "next", "hide");
    const dist = (i - st.idx + n) % n;
    if (dist === 0) s.classList.add("cur");
    else if (dist === n - 1) s.classList.add("prev");
    else if (dist === 1) s.classList.add("next");
    else s.classList.add("hide");
  });

  const p = st.photos[st.idx];
  const t = block.querySelector(".ph-info .t");
  const m = block.querySelector(".ph-info .m");
  if (t) t.textContent = p.title;
  if (m) m.textContent = `${p.meta} · ${st.idx + 1} / ${n}`;
}

/* ---------- 灯箱 ---------- */
const lightbox = document.getElementById("lightbox");
const lbImg = document.getElementById("lbImg");
const lbTitle = document.getElementById("lbTitle");
const lbMeta = document.getElementById("lbMeta");
const lbCounter = document.getElementById("lbCounter");

let lbPhotos = [];
let lbIndex = 0;

function renderLb() {
  const p = lbPhotos[lbIndex];
  lbImg.src = p.src;
  lbImg.alt = p.title;
  lbTitle.textContent = p.title;
  lbMeta.textContent = p.meta;
  lbCounter.textContent = `${lbIndex + 1} / ${lbPhotos.length}`;
}

function openLightbox(group, i) {
  lbPhotos = group.photos;
  lbIndex = i;
  renderLb();
  lightbox.classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeLightbox() {
  lightbox.classList.remove("open");
  document.body.style.overflow = "";
}

function stepLb(d) {
  lbIndex = (lbIndex + d + lbPhotos.length) % lbPhotos.length;
  renderLb();
}

document.getElementById("lbClose").addEventListener("click", closeLightbox);
document.getElementById("lbPrev").addEventListener("click", () => stepLb(-1));
document.getElementById("lbNext").addEventListener("click", () => stepLb(1));

lightbox.addEventListener("click", (e) => {
  if (e.target === lightbox) closeLightbox();
});

document.addEventListener("keydown", (e) => {
  if (!lightbox.classList.contains("open")) return;
  if (e.key === "Escape") closeLightbox();
  if (e.key === "ArrowLeft") stepLb(-1);
  if (e.key === "ArrowRight") stepLb(1);
});
