import { request } from "./client";
import type { CaseDrop, CaseReward } from "./types";

export const getCaseDrops = (entityId: number) =>
  request<CaseDrop[]>(`/cases/${entityId}/drops`);
export const openCase = (inventoryId: number) =>
  request<CaseReward>(`/cases/${inventoryId}/open`, { method: "POST" });
export const claimFreeCase = () =>
  request<CaseReward>("/cases/free", { method: "POST" });
