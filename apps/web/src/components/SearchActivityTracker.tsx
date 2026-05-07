"use client";

import { useEffect } from "react";

import { trackActivity } from "@/lib/activity";

type SearchActivityTrackerProps = {
  searchQuery?: string | null;
  filters: Record<string, string | undefined>;
  resultIds: Array<number | string>;
  resultCount: number;
  source: string;
};

export default function SearchActivityTracker({
  searchQuery,
  filters,
  resultIds,
  resultCount,
  source,
}: SearchActivityTrackerProps) {
  useEffect(() => {
    const compactFilters = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => Boolean(value)),
    );
    const impressionItems = resultIds.slice(0, 50).map((id, index) => ({
      car_id: String(id),
      position: index + 1,
    }));

    trackActivity("search", {
      source,
      searchQuery,
      filters: compactFilters,
      metadata: {
        result_count: resultCount,
        result_ids: resultIds.slice(0, 50).map(String),
      },
    });

    if (impressionItems.length) {
      trackActivity("listing_impression", {
        source,
        searchQuery,
        filters: compactFilters,
        metadata: {
          result_count: resultCount,
          items: impressionItems,
        },
      });
    }
  }, [filters, resultCount, resultIds, searchQuery, source]);

  return null;
}
