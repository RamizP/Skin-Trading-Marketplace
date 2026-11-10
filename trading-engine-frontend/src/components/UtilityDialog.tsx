import { useState } from "react";
import type { FormEvent } from "react";
import { chargeBalance } from "../api/auth";
import { createEntity } from "../api/entities";
import { chargeInventory } from "../api/inventory";
import type { Category, Entity } from "../api/types";
import {
  formatRarity,
  getErrorMessage,
  isCase,
  moneyInput,
  rarities,
  wearOptions,
} from "../utils/format";
import { ErrorNotice } from "./Feedback";
import Icon from "./Icon";
import Modal from "./Modal";

export default function UtilityDialog({
  kind,
  catalog,
  categories,
  onClose,
  onChanged,
}: {
  kind: "funds" | "inventory" | "catalog";
  catalog: Entity[];
  categories: Category[];
  onClose: () => void;
  onChanged: (message?: string) => Promise<void>;
}) {
  const [amount, setAmount] = useState("50.00");
  const [entityId, setEntityId] = useState(catalog[0]?.id || 0);
  const [wear, setWear] = useState("Field-Tested");
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("");
  const [image, setImage] = useState("");
  const [categoryId, setCategoryId] = useState(categories[0]?.id || 0);
  const [rarity, setRarity] = useState("common");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const selectedEntity = catalog.find((entity) => entity.id === entityId);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setError("");
    setBusy(true);
    try {
      if (kind === "funds") await chargeBalance(moneyInput(amount));
      else if (kind === "inventory") {
        if (!selectedEntity)
          throw new Error("Choose an item from the catalog first.");
        await chargeInventory(
          entityId,
          isCase(selectedEntity, categories) ? "NONE" : wear,
        );
      } else {
        if (!categoryId)
          throw new Error(
            "Create a category in the API before adding an item.",
          );
        await createEntity({
          name: name.trim(),
          symbol: symbol.trim(),
          image_url: image.trim() || null,
          category_id: categoryId,
          entity_rarity: rarity,
        });
      }
      await onChanged(
        kind === "funds"
          ? "Test funds added to your wallet."
          : kind === "inventory"
            ? "Test item added to your inventory."
            : "Item added to the catalog.",
      );
      onClose();
    } catch (reason) {
      setError(getErrorMessage(reason));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal
      title={
        kind === "funds"
          ? "A little trading power."
          : kind === "inventory"
            ? "Try something new."
            : "Add a collectible."
      }
      onClose={onClose}
      busy={busy}
    >
      <form className="stack-form" onSubmit={submit}>
        <p className="dialog-description">
          {kind === "funds"
            ? "Add test USD to explore buying and selling. This is a sandbox: no payment information or real money is involved."
            : kind === "inventory"
              ? "Add a catalog item to try listing, trading, or opening a case. This uses the API’s test-inventory endpoint."
              : "Publish an item in the exchange catalog. Only administrator accounts can create collectibles."}
        </p>
        {error && <ErrorNotice message={error} />}
        {kind === "funds" && (
          <>
            <div className="amount-presets">
              {["10.00", "50.00", "100.00"].map((value) => (
                <button
                  type="button"
                  className={amount === value ? "selected" : ""}
                  onClick={() => setAmount(value)}
                  key={value}
                >
                  ${Number(value)}
                </button>
              ))}
            </div>
            <label>
              Amount (test USD)
              <input
                autoFocus
                type="number"
                min="0.01"
                step="0.01"
                required
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
              />
            </label>
          </>
        )}
        {kind === "inventory" && (
          <>
            <label>
              Collectible
              <select
                aria-label="Collectible"
                value={entityId}
                onChange={(event) => setEntityId(Number(event.target.value))}
                disabled={!catalog.length}
              >
                {catalog.map((entity) => (
                  <option key={entity.id} value={entity.id}>
                    {entity.symbol} · {entity.name}
                  </option>
                ))}
              </select>
            </label>
            {selectedEntity && !isCase(selectedEntity, categories) && (
              <label>
                Condition
                <select
                  aria-label="Condition"
                  value={wear}
                  onChange={(event) => setWear(event.target.value)}
                >
                  {wearOptions.slice(1).map((value) => (
                    <option key={value}>{value}</option>
                  ))}
                </select>
              </label>
            )}
            {!catalog.length && (
              <p className="inline-note">
                The catalog is empty. An administrator needs to add an item
                first.
              </p>
            )}
          </>
        )}
        {kind === "catalog" && (
          <>
            <label>
              Item name
              <input
                required
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Asiimov"
              />
            </label>
            <label>
              Symbol / weapon
              <input
                required
                value={symbol}
                onChange={(event) => setSymbol(event.target.value)}
                placeholder="AK-47"
              />
            </label>
            <div className="form-columns">
              <label>
                Category
                <select
                  value={categoryId}
                  onChange={(event) =>
                    setCategoryId(Number(event.target.value))
                  }
                >
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Rarity
                <select
                  value={rarity}
                  onChange={(event) => setRarity(event.target.value)}
                >
                  {rarities.map((value) => (
                    <option key={value} value={value}>
                      {formatRarity(value)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label>
              Image URL (optional)
              <input
                type="url"
                value={image}
                onChange={(event) => setImage(event.target.value)}
                placeholder="https://…"
              />
            </label>
          </>
        )}
        <button
          className="button button-primary button-full"
          disabled={
            busy ||
            (kind === "inventory" && !catalog.length) ||
            (kind === "catalog" && !categories.length)
          }
        >
          {busy
            ? "Saving…"
            : kind === "funds"
              ? "Add test funds"
              : kind === "inventory"
                ? "Add to inventory"
                : "Create catalog item"}
          <Icon name="plus" size={16} />
        </button>
      </form>
    </Modal>
  );
}
