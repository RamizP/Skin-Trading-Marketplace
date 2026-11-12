import { useEffect, useRef, useState } from "react";
import type { CaseDrop, CaseReward, Entity } from "../api/types";
import { formatRarity, rarityClass } from "../utils/format";
import { ErrorNotice } from "./Feedback";
import Icon from "./Icon";
import ItemArt from "./ItemArt";
import "./CaseOpening.css";

const WINNING_INDEX = 38;
const REEL_LENGTH = 46;
const SPIN_DURATION = 6200;

function buildReel(drops: CaseDrop[], winner: Entity): Entity[] {
  const pool = drops.filter((drop) => drop.weight > 0);
  const total = pool.reduce((sum, drop) => sum + drop.weight, 0);
  const cards = Array.from({ length: REEL_LENGTH }, () => {
    let position = Math.random() * total;
    for (const drop of pool) {
      position -= drop.weight;
      if (position < 0) return drop.entity;
    }
    return pool[0]?.entity || winner;
  });
  // The other cards are scenery. Only the API response determines the reward.
  cards[WINNING_INDEX] = winner;
  return cards;
}

export default function CaseOpening({
  caseEntity,
  drops,
  reward,
  rewardEntity,
  busy,
  error,
  onComplete,
  onBack,
  onDone,
}: {
  caseEntity: Entity;
  drops: CaseDrop[];
  reward: CaseReward | null;
  rewardEntity: Entity | undefined;
  busy: boolean;
  error: string;
  onComplete: (reward: CaseReward) => void;
  onBack: () => void;
  onDone: () => void;
}) {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const dialog = root.current?.closest("dialog");
    if (dialog) dialog.scrollTop = 0;
  }, []);

  return (
    <div className="case-opening" ref={root}>
      <header className="case-opening-header">
        <div className={`case-opening-icon ${rarityClass(caseEntity)}`}>
          <ItemArt entity={caseEntity} caseItem loading="eager" />
        </div>
        <div>
          <span className="eyebrow">CASE OPENING</span>
          <h2>{caseEntity.name}</h2>
        </div>
      </header>
      {reward ? (
        <CaseReel
          drops={drops}
          reward={reward}
          winner={
            rewardEntity || {
              id: reward.entity_id,
              name: `Item #${reward.entity_id}`,
              symbol: "COLLECTIBLE",
              entity_rarity: "common",
              category_id: null,
            }
          }
          busy={busy}
          error={error}
          onComplete={onComplete}
          onBack={onBack}
          onDone={onDone}
        />
      ) : (
        <div className="case-opening-preparing" role="status">
          <div className={`case-opening-sealed ${rarityClass(caseEntity)}`}>
            <ItemArt entity={caseEntity} caseItem loading="eager" />
          </div>
          <span className="loading-spinner" aria-hidden="true" />
          <p>Opening your case…</p>
        </div>
      )}
    </div>
  );
}

function CaseReel({
  drops,
  reward,
  winner,
  busy,
  error,
  onComplete,
  onBack,
  onDone,
}: {
  drops: CaseDrop[];
  reward: CaseReward;
  winner: Entity;
  busy: boolean;
  error: string;
  onComplete: (reward: CaseReward) => void;
  onBack: () => void;
  onDone: () => void;
}) {
  const [cards] = useState(() => buildReel(drops, winner));
  const [revealed, setRevealed] = useState(false);
  const viewport = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const finish = useRef<(() => void) | null>(null);
  const completed = useRef(onComplete);
  const settled = useRef(false);

  useEffect(() => {
    completed.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    const windowElement = viewport.current;
    const strip = track.current;
    if (!windowElement || !strip) return;
    const first = strip.children[3] as HTMLElement;
    const winningCard = strip.children[WINNING_INDEX] as HTMLElement;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let animation: Animation | null = null;
    let finished = settled.current;

    function offset(card: HTMLElement) {
      return (
        windowElement!.clientWidth / 2 - card.offsetLeft - card.offsetWidth / 2
      );
    }
    function complete() {
      if (finished) return;
      finished = true;
      settled.current = true;
      animation?.cancel();
      strip!.style.transform = `translateX(${offset(winningCard)}px)`;
      setRevealed(true);
      completed.current(reward);
    }
    function positionReel() {
      if (finished) {
        strip!.style.transform = `translateX(${offset(winningCard)}px)`;
        return;
      }
      const elapsed = Number(animation?.currentTime || 0);
      animation?.cancel();
      strip!.style.transform = `translateX(${offset(first)}px)`;
      if (reducedMotion.matches) {
        complete();
        return;
      }
      animation = strip!.animate(
        [
          { transform: `translateX(${offset(first)}px)` },
          { transform: `translateX(${offset(winningCard)}px)` },
        ],
        {
          duration: SPIN_DURATION,
          easing: "cubic-bezier(0.12, 0.8, 0.18, 1)",
          fill: "forwards",
        },
      );
      animation.currentTime = elapsed;
      animation.onfinish = complete;
    }

    finish.current = complete;
    positionReel();
    const resize = new ResizeObserver(positionReel);
    resize.observe(windowElement);
    const motionChanged = () => {
      if (reducedMotion.matches) complete();
    };
    reducedMotion.addEventListener("change", motionChanged);
    return () => {
      resize.disconnect();
      reducedMotion.removeEventListener("change", motionChanged);
      animation?.cancel();
      finish.current = null;
    };
  }, [reward]);

  return (
    <section
      className={`case-reel ${revealed ? `is-revealed ${rarityClass(winner)}` : ""}`}
      aria-label="Case opening reel"
      data-state={revealed ? "revealed" : "spinning"}
    >
      <div className="case-reel-caption" role="status">
        <span className="case-reel-indicator" />
        {revealed
          ? "A new addition to your collection."
          : "Let's see what you get."}
      </div>
      <div className="case-reel-frame">
        <div className="case-reel-pointer" aria-hidden="true" />
        <div className="case-reel-viewport" ref={viewport} aria-hidden="true">
          <div className="case-reel-track" ref={track}>
            {cards.map((entity, index) => (
              <div
                key={index}
                className={`case-reel-card ${rarityClass(entity)} ${revealed && index === WINNING_INDEX ? "is-winner" : ""}`}
                data-entity-id={entity.id}
              >
                <span className="case-reel-rarity">
                  <span className="rarity-dot" />
                  {formatRarity(entity.entity_rarity)}
                </span>
                <ItemArt entity={entity} loading="eager" />
                <span className="case-reel-symbol">{entity.symbol}</span>
                <strong>{entity.name}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>
      {revealed ? (
        <>
          <div
            className={`reward-reveal case-opening-reward ${rarityClass(winner)}`}
            role="status"
          >
            <span className="eyebrow">
              <Icon name="spark" size={15} />
              YOU UNBOXED
            </span>
            <ItemArt entity={winner} loading="eager" />
            <h3>{winner.name}</h3>
            <p className="case-opening-wear">{reward.entity_wear}</p>
            <span className="small-muted">Added to your inventory</span>
          </div>
          {error && <ErrorNotice message={error} />}
          <div className="case-opening-buttons">
            <button
              className="button button-secondary"
              disabled={busy}
              onClick={onBack}
            >
              <Icon name="back" size={16} />
              Back to case
            </button>
            <button
              className="button button-primary"
              disabled={busy}
              onClick={onDone}
            >
              {busy ? "Updating inventory…" : "Done"}
              <Icon name="check" size={16} />
            </button>
          </div>
        </>
      ) : (
        <div className="case-opening-footer">
          <span className="small-muted">Opening your case…</span>
          <button
            className="button button-quiet"
            onClick={() => finish.current?.()}
          >
            Reveal now
            <Icon name="arrow" size={15} />
          </button>
        </div>
      )}
    </section>
  );
}
