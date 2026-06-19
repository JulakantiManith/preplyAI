import { useQuery } from "@tanstack/react-query";
import {
  getSessionHistory,
  getSessionDetail,
} from "../services/historyService";
import type { HistoryFilters } from "../services/historyService";

const SESSION_HISTORY_KEY = "session-history" as const;
const SESSION_DETAIL_KEY = "session-detail" as const;

export function useSessionHistory(page: number = 1, filters?: HistoryFilters) {
  return useQuery({
    queryKey: [SESSION_HISTORY_KEY, page, filters],
    queryFn: () => getSessionHistory(page, filters),
  });
}

export function useSessionDetail(sessionId: string) {
  return useQuery({
    queryKey: [SESSION_DETAIL_KEY, sessionId],
    queryFn: () => getSessionDetail(sessionId),
    enabled: !!sessionId,
  });
}
