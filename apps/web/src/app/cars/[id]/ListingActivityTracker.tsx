"use client";

import { useEffect } from "react";

import { trackActivity } from "@/lib/activity";

export default function ListingActivityTracker({ carId }: { carId: number }) {
  useEffect(() => {
    trackActivity("listing_view", {
      carId,
      source: "car_detail",
    });
  }, [carId]);

  return null;
}
