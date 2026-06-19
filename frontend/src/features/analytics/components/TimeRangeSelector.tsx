import type { TimeRange } from "../services/analyticsService";

interface TimeRangeSelectorProps {
  value: TimeRange;
  onChange: (range: TimeRange) => void;
}

const TIME_RANGE_OPTIONS: { value: TimeRange; label: string }[] = [
  { value: "daily", label: "Today" },
  { value: "weekly", label: "This Week" },
  { value: "monthly", label: "1 Month" },
  { value: "3months", label: "3 Months" },
  { value: "yearly", label: "1 Year" },
];

export function TimeRangeSelector({ value, onChange }: TimeRangeSelectorProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as TimeRange)}
      className="rounded-md border bg-background px-3 py-1.5 text-sm font-medium text-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-ring"
    >
      {TIME_RANGE_OPTIONS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
