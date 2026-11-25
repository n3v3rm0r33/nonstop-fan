import json
from html import escape
from pathlib import Path
from shutil import copytree, ignore_patterns
from string import Template
from typing import Final, NotRequired, TypedDict


DEMO: Final = (
    "Демо-концепт сайту для «NON STOP». Підготовлено як пропозицію, "
    "не є офіційним сайтом. Видалимо за першим проханням."
)
BRANDBOOK: Final = "https://www.newproducts.tools/nonstop"
ARCHIVE_FILTERS: Final = (
    ("all", "Усі"),
    ("early", "Ранні випуски"),
    ("experiments", "Експерименти"),
    ("limited", "Лімітки"),
)
ARCHIVE_EXHIBITS: Final = ("night", "ultra", "anniversary")


class Product(TypedDict):
    slug: str
    name: str
    notes: str
    color: str
    series: NotRequired[str]
    asset: NotRequired[str]


class ArchiveProduct(Product):
    category: str
    formats: str
    detail: str
    source: NotRequired[str]
    source_label: NotRequired[str]


class Catalog(TypedDict):
    designs: list[Product]
    flavors: list[Product]
    limited: list[Product]
    shots: list[Product]
    archive: list[ArchiveProduct]


def can(product: Product, *, prefix: str = "", alt: str = "", lazy: bool = False) -> str:
    loading = ' loading="lazy"' if lazy else ""
    asset = escape(product.get("asset", product["slug"]))
    return f'<img src="{prefix}assets/{asset}.webp" alt="{escape(alt)}"{loading} decoding="async">'


def accent(product: Product) -> str:
    return f'--accent:{escape(product["color"])}'


def step(product: Product, index: int, total: int, heading: str) -> str:
    slug = escape(product["slug"])
    eager = heading == "h2" and index <= 2
    position = index - 1
    stop = position / max(1, total - 1)
    return f'''<div class="taste-anchor" id="taste-{slug}" style="--position:{position}"></div>
    <article class="taste-step" style="{accent(product)};--stop:{stop:.4%}" aria-labelledby="title-{slug}">
      <div class="step-inner shell">
        <div class="step-meter" aria-hidden="true">{index:02d}<span></span>{total:02d}</div>
        <div class="step-copy">
          <p class="eyebrow">{escape(product.get("series", ""))}</p>
          <{heading} id="title-{slug}">{escape(product["name"])}</{heading}>
          <p class="taste-note">{escape(product["notes"])}</p>
        </div>
        <div class="step-art" aria-hidden="true">{can(product, lazy=not eager)}</div>
      </div>
    </article>'''


def swatch(product: Product, index: int, total: int, *, show_label: bool) -> str:
    name = escape(product["name"])
    label = f"<span>{name}</span>" if show_label else '<span class="swatch-dot"></span>'
    start = max(0.0, (index - 0.5) / max(1, total - 1))
    end = min(1.0, (index + 0.5) / max(1, total - 1))
    return f'''<a href="#taste-{escape(product["slug"])}" style="{accent(product)};--from:{start:.4%};--to:{end:.4%}"
      aria-label="{name}" title="{name}">{label}</a>'''


def lineup_item(product: Product, index: int) -> str:
    return f'''<li style="{accent(product)};--position:{index}">
      <a href="#taste-{escape(product["slug"])}">{can(product, lazy=True)}<span>{escape(product["name"])}</span></a>
    </li>'''


def archive_exhibit(product: ArchiveProduct) -> str:
    return f'''<li class="archive-exhibit" style="{accent(product)}">
      <a href="archive/{escape(product["slug"])}.html">
        <div class="exhibit-window" aria-hidden="true">{can(product, lazy=True)}</div>
        <span class="exhibit-label">{escape(product["name"])}<span class="card-arrow" aria-hidden="true">↗</span></span>
      </a>
    </li>'''


def archive_card(product: ArchiveProduct) -> str:
    return f'''<li class="product-card" data-category="{escape(product["category"])}" style="{accent(product)}">
      <a class="archive-card-link" href="archive/{escape(product["slug"])}.html">
        <div class="product-photo">{can(product, lazy=True)}</div>
        <div class="product-copy"><h3>{escape(product["name"])}<span class="card-arrow" aria-hidden="true">↗</span></h3>
          <p>{escape(product["notes"])}</p></div>
      </a>
    </li>'''


def render_gallery(
    template: Template,
    products: list[Product],
    *,
    nav_label: str,
    next_id: str,
    next_label: str,
    show_labels: bool = False,
    heading: str = "h3",
) -> str:
    total = len(products)
    return template.substitute(
        count=total,
        interval=f"{1 / max(1, total - 1):.4%}",
        steps="\n".join(step(product, index, total, heading) for index, product in enumerate(products, 1)),
        swatches="\n".join(
            swatch(product, index, total, show_label=show_labels) for index, product in enumerate(products)
        ),
        swatch_style=" swatches-labeled" if show_labels else "",
        nav_label=nav_label,
        next_id=next_id,
        next_label=next_label,
    )


def write_archive(src: Path, dist: Path, products: list[ArchiveProduct]) -> None:
    template = Template((src / "archive.html").read_text(encoding="utf-8"))
    archive_dir = dist / "archive"
    archive_dir.mkdir(exist_ok=True)
    for product in products:
        name = product["name"]
        page = template.substitute(
            name=escape(name),
            summary=escape(product["notes"]),
            detail=escape(product["detail"]),
            formats=escape(product["formats"]),
            accent=accent(product),
            can=can(product, prefix="../", alt=f"Паковання NON STOP {name}"),
            source=escape(product.get("source", BRANDBOOK)),
            source_label=escape(product.get("source_label", "Брендбук NON STOP")),
            demo=DEMO,
        )
        (archive_dir / f'{product["slug"]}.html').write_text(page, encoding="utf-8")


def build(root: Path) -> None:
    src, dist = root / "src", root / "dist"
    catalog: Catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    flavors = catalog["flavors"]
    archive_by_slug = {product["slug"]: product for product in catalog["archive"]}
    template = Template((src / "index.html").read_text(encoding="utf-8"))
    gallery = Template((src / "gallery.html").read_text(encoding="utf-8"))
    page = template.substitute(
        story_gallery=render_gallery(
            gallery, catalog["designs"], nav_label="Обрати рік", next_id="lineup",
            next_label="Усі смаки", show_labels=True,
        ),
        flavors_gallery=render_gallery(
            gallery, flavors, nav_label="Обрати смак", next_id="story", next_label="Історія банки", heading="h2",
        ),
        limited_gallery=render_gallery(
            gallery, catalog["limited"], nav_label="Обрати лімітку", next_id="shots", next_label="До шотів",
        ),
        shots_gallery=render_gallery(
            gallery, catalog["shots"], nav_label="Обрати шот", next_id="archive", next_label="До архіву",
            show_labels=True,
        ),
        lineup="\n".join(lineup_item(product, index) for index, product in enumerate(flavors)),
        archive_exhibits="\n".join(archive_exhibit(archive_by_slug[slug]) for slug in ARCHIVE_EXHIBITS),
        archive_inputs="\n".join(
            f'<input class="visually-hidden" type="radio" name="archive-filter" id="archive-{key}"'
            + (' checked>' if key == "all" else '>')
            for key, _ in ARCHIVE_FILTERS
        ),
        archive_filters="\n".join(f'<label for="archive-{key}">{label}</label>' for key, label in ARCHIVE_FILTERS),
        archive="\n".join(map(archive_card, catalog["archive"])),
        demo=DEMO,
    )
    copytree(src, dist, ignore=ignore_patterns("*.html"), dirs_exist_ok=True)
    (dist / "index.html").write_text(page, encoding="utf-8")
    write_archive(src, dist, catalog["archive"])


if __name__ == "__main__":
    build(Path(__file__).resolve().parent)
