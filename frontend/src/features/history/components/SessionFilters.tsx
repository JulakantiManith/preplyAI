import type { HistoryFilters } from "../services/historyService";

interface SessionFiltersProps {
  filters: HistoryFilters;
  onFiltersChange: (filters: HistoryFilters) => void;
}

export function SessionFilters({ filters, onFiltersChange }: SessionFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border bg-card p-4 shadow-sm">
      {/* Session Type Filter */}
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="session-type-filter"
          className="text-sm font-medium text-foreground"
        >
          Session Type
        </label>
        <select
          id="session-type-filter"
          value={filters.sessionType || ""}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              sessionType: e.target.value || undefined,
            })
          }
          className="h-9 rounded-md border border-input bg-background px-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        >
          <option value="">All Types</option>
          <option value="interview">Interview</option>
          <option value="presentation">Presentation</option>
        </select>
      </div>

      {/* Start Date Filter */}
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="start-date-filter"
          className="text-sm font-medium text-foreground"
        >
          From
        </label>
        <input
          id="start-date-filter"
          type="date"
          value={filters.startDate || ""}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              startDate: e.target.value || undefined,
            })
          }
          className="h-9 rounded-md border border-input bg-background px-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        />
      </div>

      {/* End Date Filter */}
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="end-date-filter"
          className="text-sm font-medium text-foreground"
        >
          To
        </label>
        <input
          id="end-date-filter"
          type="date"
          value={filters.endDate || ""}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              endDate: e.target.value || undefined,
            })
          }
          className="h-9 rounded-md border border-input bg-background px-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        />
      </div>

      {/* Clear Filters */}
      {(filters.sessionType || filters.startDate || filters.endDate) && (
        <button
          onClick={() => onFiltersChange({})}
          className="h-9 rounded-md px-3 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
