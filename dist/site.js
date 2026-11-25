const featured = document.querySelectorAll(".archive-exhibit a");
const archiveCards = document.querySelectorAll(".archive-card-link");
const featuredLinks = new Set(Array.from(featured, (link) => link.href));
for (const card of archiveCards) {
  if (featuredLinks.has(card.href)) card.closest(".product-card").classList.add("featured-in-archive");
}

const [firstCan, secondCan] = document.querySelectorAll(".flavors .step-art img");
if (firstCan) {
  firstCan.fetchPriority = "high";
  if (secondCan) secondCan.loading = "lazy";
}

for (const art of document.querySelectorAll(".step-art")) {
  const step = art.closest(".taste-step");
  const title = step.querySelector("h2, h3").textContent;
  let description = "Банка NON STOP " + title + " 500 мл";
  if (step.closest(".story")) description = "Банка NON STOP Original 500 мл, дизайн " + title + " року";
  if (step.closest(".limited") && title !== "S.T.A.L.K.E.R.") {
    description = "Банка NON STOP S.T.A.L.K.E.R. " + title + " 500 мл";
  }
  if (step.closest(".shots")) description = "Пляшечка NON STOP Shot " + title + " 60 мл";

  art.querySelector("img").alt = description;
  art.removeAttribute("aria-hidden");
}

const entryPhoto = document.querySelector(".entry-photo img");
if (entryPhoto) {
  const title = document.querySelector("#entry-title").textContent;
  entryPhoto.alt = title === "Shot 50 мл"
    ? "Пляшечка NON STOP Shot 50 мл, випуск 2011 року"
    : "Банка NON STOP " + title + " 500 мл";
}

const header = document.querySelector(".site-header");
const galleries = Array.from(document.querySelectorAll(".gallery"), (gallery) => {
  const choices = Array.from(gallery.querySelectorAll(".swatches a"), (link) => ({
    link,
    anchor: document.getElementById(link.hash.slice(1)),
  }));
  return { gallery, choices, current: null };
});

function updateChoices() {
  const headerEdge = header.getBoundingClientRect().bottom;
  for (const state of galleries) {
    const { top, bottom } = state.gallery.getBoundingClientRect();
    if (state.current && (top > window.innerHeight || bottom < headerEdge)) continue;

    let nearest = state.choices[0];
    let distance = Infinity;
    for (const choice of state.choices) {
      const offset = Math.abs(choice.anchor.getBoundingClientRect().top - headerEdge);
      if (offset < distance) {
        nearest = choice;
        distance = offset;
      }
    }

    if (state.current === nearest.link) continue;
    state.current?.removeAttribute("aria-current");
    state.current = nearest.link;
    state.current.setAttribute("aria-current", "true");
  }
}

if (galleries.length) {
  let frame = 0;
  const scheduleChoices = () => {
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      updateChoices();
    });
  };

  window.addEventListener("scroll", scheduleChoices, { passive: true });
  window.addEventListener("resize", scheduleChoices);
  window.addEventListener("pageshow", scheduleChoices);
  updateChoices();
}
