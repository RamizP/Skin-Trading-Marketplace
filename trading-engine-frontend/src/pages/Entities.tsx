import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import type { Category, Entity, MarketEntity, User, View } from "../api/types";
import { EmptyState, SkeletonCards } from "../components/Feedback";
import Icon from "../components/Icon";
import ItemArt from "../components/ItemArt";
import {
  categoryName,
  formatCurrency,
  formatRarity,
  isCase,
  rarities,
  rarityClass,
} from "../utils/format";

export default function Entities({
  catalog,
  market,
  categories,
  casesOnly,
  loading,
  user,
  onOpen,
  onNavigate,
  onCreate,
  caseOffer,
}: {
  catalog: Entity[];
  market: MarketEntity[];
  categories: Category[];
  casesOnly: boolean;
  loading: boolean;
  user: User | null;
  onOpen: (entity: Entity) => void;
  onNavigate: (view: View) => void;
  onCreate: () => void;
  caseOffer?: ReactNode;
}) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [rarity, setRarity] = useState("all");
  const [sort, setSort] = useState("price-low");
  const [listedOnly, setListedOnly] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const shortcut = (event: KeyboardEvent) => {
      const target = event.target;
      if (event.key !== "/" || event.ctrlKey || event.metaKey || event.altKey)
        return;
      if (
        target instanceof HTMLElement &&
        target.closest(
          "input, textarea, select, [contenteditable='true'], dialog",
        )
      )
        return;
      event.preventDefault();
      searchRef.current?.focus();
    };
    window.addEventListener("keydown", shortcut);
    return () => window.removeEventListener("keydown", shortcut);
  }, []);
  const priceMap = useMemo(
    () => new Map(market.map((row) => [row.entity.id, row.lowest_price])),
    [market],
  );
  const available = casesOnly
    ? catalog.filter((entity) => isCase(entity, categories))
    : catalog;
  const visible = available
    .filter((entity) => {
      const query =
        `${entity.name} ${entity.symbol} ${categoryName(entity, categories)}`.toLowerCase();
      return (
        query.includes(search.toLowerCase()) &&
        (category === "all" || entity.category_id === Number(category)) &&
        (rarity === "all" || entity.entity_rarity === rarity) &&
        (!listedOnly || priceMap.has(entity.id))
      );
    })
    .sort((a, b) => {
      if (sort === "name") return a.name.localeCompare(b.name);
      if (sort === "rarity")
        return (
          rarities.indexOf(b.entity_rarity) - rarities.indexOf(a.entity_rarity)
        );
      const aPrice = priceMap.get(a.id);
      const bPrice = priceMap.get(b.id);
      if (aPrice == null) return bPrice == null ? a.id - b.id : 1;
      if (bPrice == null) return -1;
      return sort === "price-high"
        ? Number(bPrice) - Number(aPrice)
        : Number(aPrice) - Number(bPrice);
    });
  const featured = [...market].sort(
    (a, b) =>
      rarities.indexOf(b.entity.entity_rarity) -
      rarities.indexOf(a.entity.entity_rarity),
  )[0];
  function reset() {
    setSearch("");
    setCategory("all");
    setRarity("all");
    setListedOnly(false);
  }

  return (
    <section className="page-enter">
      <div className={`market-hero ${casesOnly ? "case-hero" : ""}`}>
        <div className="hero-grid" aria-hidden="true" />
        <div className="hero-copy">
          <span className="eyebrow">
            <span className="orange-line" />
            {casesOnly
              ? "A LITTLE MYSTERY. A NEW FAVORITE."
              : "THE PLAYER’S EXCHANGE"}
          </span>
          <h1>
            {casesOnly ? (
              <>
                Good things
                <br />
                come in <em>cases.</em>
              </>
            ) : (
              <>
                Your next upgrade
                <br />
                starts <em>here.</em>
              </>
            )}
          </h1>
          <p>
            {casesOnly
              ? "Discover the contents. Collect a case. Open it whenever the moment feels right."
              : "Discover standout skins, build your collection, and find your next trade. Your inventory. Your rules."}
          </p>
          <div className="hero-actions">
            <button
              className="button button-primary"
              onClick={() =>
                casesOnly
                  ? onNavigate("inventory")
                  : document
                      .getElementById("catalog")
                      ?.scrollIntoView({ behavior: "smooth", block: "start" })
              }
            >
              {casesOnly ? "Go to my inventory" : "Explore the market"}
              <Icon name="arrow" size={17} />
            </button>
            <button
              className="button button-quiet"
              onClick={() => onNavigate(casesOnly ? "market" : "cases")}
            >
              {casesOnly ? "Browse marketplace" : "Discover cases"}
              <Icon name={casesOnly ? "market" : "case"} size={17} />
            </button>
          </div>
        </div>
        <div
          className={`hero-art ${featured ? rarityClass(featured.entity) : "rarity-legendary"}`}
        >
          <div className="hero-orbit orbit-one" />
          <div className="hero-orbit orbit-two" />
          <span className="hero-cross cross-one">+</span>
          <span className="hero-cross cross-two">+</span>
          <span className="hero-index">
            {casesOnly ? "UNBOX / DISCOVER" : "CURATED / COLLECTIBLES"}
          </span>
          <ItemArt
            entity={casesOnly ? available[0] : featured?.entity}
            caseItem={casesOnly}
          />
          {!casesOnly && featured && (
            <button
              className="hero-featured"
              onClick={() => onOpen(featured.entity)}
            >
              <span className="rarity-dot" />
              <span>
                <small>IN THE SPOTLIGHT</small>
                <strong>{featured.entity.name}</strong>
              </span>
              <b>{formatCurrency(featured.lowest_price)}</b>
              <Icon name="arrow" size={16} />
            </button>
          )}
          {casesOnly && (
            <span className="hero-case-tag">
              <Icon name="case" size={16} /> Open a possibility.
            </span>
          )}
        </div>
      </div>
      {caseOffer}
      <div className="market-facts">
        <div>
          <Icon name="grid" />
          <span>
            <strong>{loading ? "—" : catalog.length}</strong> collectibles to
            discover
          </span>
        </div>
        <div>
          <Icon name="bolt" />
          <span>
            <strong>{loading ? "—" : market.length}</strong> item types listed
          </span>
        </div>
        <div>
          <Icon name="shield" />
          <span>
            Your collection. <strong>Your control.</strong>
          </span>
        </div>
        <div className="facts-last">
          <span className="status-dot" />
          Prices from the exchange API
        </div>
      </div>
      <div className="section-heading" id="catalog">
        <div>
          <span className="eyebrow">FIND YOUR NEXT FAVORITE</span>
          <h2>
            {casesOnly ? "The case collection" : "The marketplace"}
            <span className="count-badge">{available.length}</span>
          </h2>
        </div>
        {user?.role === "admin" ? (
          <button className="button button-secondary" onClick={onCreate}>
            <Icon name="plus" size={16} />
            New catalog item
          </button>
        ) : (
          <span className="section-aside">Small details. Big difference.</span>
        )}
      </div>
      <div className="catalog-toolbar">
        <label className="search-field">
          <Icon name="search" size={18} />
          <input
            ref={searchRef}
            aria-label="Search items"
            placeholder={
              casesOnly
                ? "Search cases…"
                : "Search skins, weapons, collectibles…"
            }
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <kbd>/</kbd>
        </label>
        <label className="sort-select">
          <span>Sort by</span>
          <select
            aria-label="Sort items"
            value={sort}
            onChange={(event) => setSort(event.target.value)}
          >
            <option value="price-low">Price: low to high</option>
            <option value="price-high">Price: high to low</option>
            <option value="rarity">Rarity</option>
            <option value="name">Name: A–Z</option>
          </select>
        </label>
      </div>
      {!casesOnly && (
        <div
          className="category-tabs"
          role="group"
          aria-label="Item categories"
        >
          <button
            className={category === "all" ? "active" : ""}
            onClick={() => setCategory("all")}
          >
            All items
          </button>
          {categories
            .filter((entry) =>
              catalog.some((entity) => entity.category_id === entry.id),
            )
            .map((entry) => (
              <button
                key={entry.id}
                className={category === String(entry.id) ? "active" : ""}
                onClick={() => setCategory(String(entry.id))}
              >
                {entry.name}
              </button>
            ))}
        </div>
      )}
      <div className="catalog-layout">
        <aside className="filters-panel">
          <label className="mobile-rarity-filter">
            Rarity
            <select
              aria-label="Filter by rarity"
              value={rarity}
              onChange={(event) => setRarity(event.target.value)}
            >
              <option value="all">All rarities</option>
              {rarities.map((value) => (
                <option key={value} value={value}>
                  {formatRarity(value)}
                </option>
              ))}
            </select>
          </label>
          <div className="filter-heading">
            <strong>Filters</strong>
            <button className="text-button" onClick={reset}>
              Reset
            </button>
          </div>
          <span className="filter-label">AVAILABILITY</span>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={listedOnly}
              onChange={(event) => setListedOnly(event.target.checked)}
            />
            Listed on market
            <span>
              {available.filter((entity) => priceMap.has(entity.id)).length}
            </span>
          </label>
          <div className="filter-divider" />
          <span className="filter-label">RARITY</span>
          <button
            className={`rarity-filter ${rarity === "all" ? "selected" : ""}`}
            onClick={() => setRarity("all")}
          >
            <span className="filter-radio" />
            All rarities
          </button>
          {rarities.map((value) => (
            <button
              key={value}
              className={`rarity-filter rarity-${value} ${rarity === value ? "selected" : ""}`}
              onClick={() => setRarity(value)}
            >
              <span className="rarity-dot" />
              <span>{formatRarity(value)}</span>
              <small>
                {
                  available.filter((entity) => entity.entity_rarity === value)
                    .length
                }
              </small>
            </button>
          ))}
          <div className="filter-note">
            <Icon name="info" size={16} />
            <p>Prices are in test USD. No real-money purchases.</p>
          </div>
        </aside>
        <div className="catalog-results">
          <div className="results-heading">
            <p>
              <strong>{visible.length}</strong> items found
            </p>
            <span>
              <Icon name="grid" size={14} /> Collection view
            </span>
          </div>
          {loading ? (
            <SkeletonCards />
          ) : visible.length === 0 ? (
            <EmptyState
              title="Nothing here. Yet."
              text={
                available.length
                  ? "Try a different search or clear your filters."
                  : "Items will appear here when they are added to the API catalog."
              }
              icon={casesOnly ? "case" : "search"}
              action={available.length ? "Clear filters" : undefined}
              onAction={reset}
            />
          ) : (
            <div className="item-grid">
              {visible.map((entity) => (
                <button
                  key={entity.id}
                  className={`item-card ${rarityClass(entity)}`}
                  onClick={() => onOpen(entity)}
                  aria-label={`Inspect ${entity.name}`}
                >
                  <div className="item-card-top">
                    <span>{categoryName(entity, categories)}</span>
                    <Icon
                      name={isCase(entity, categories) ? "case" : "arrow"}
                      size={15}
                    />
                  </div>
                  <div className="card-art">
                    <ItemArt
                      entity={entity}
                      caseItem={isCase(entity, categories)}
                    />
                    <span className="art-floor" />
                  </div>
                  <div className="item-card-copy">
                    <span className="item-symbol">{entity.symbol}</span>
                    <h3>{entity.name}</h3>
                    <span className="item-rarity">
                      <span className="rarity-dot" />
                      {formatRarity(entity.entity_rarity)}
                    </span>
                    <div className="item-card-footer">
                      <div>
                        <small>
                          {priceMap.has(entity.id)
                            ? "STARTING AT"
                            : "MARKET STATUS"}
                        </small>
                        <strong
                          className={!priceMap.has(entity.id) ? "unlisted" : ""}
                        >
                          {priceMap.has(entity.id)
                            ? formatCurrency(priceMap.get(entity.id))
                            : "No listings"}
                        </strong>
                      </div>
                      <span className="card-arrow">
                        <Icon name="arrow" size={18} />
                      </span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
