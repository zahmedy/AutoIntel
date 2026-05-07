"use client";

import { trackActivity } from "@/lib/activity";

type ContactActionsProps = {
  carId: number;
  emailUrl?: string | null;
  smsUrl?: string | null;
  whatsappUrl?: string | null;
};

export default function ContactActions({ carId, emailUrl, smsUrl, whatsappUrl }: ContactActionsProps) {
  function trackContactClick(channel: string) {
    trackActivity("contact_click", {
      carId,
      source: "car_detail",
      metadata: { channel },
    });
  }

  return (
    <div className="contact-actions compact-contact-actions">
      {emailUrl && (
        <a href={emailUrl} className="btn btn-secondary" onClick={() => trackContactClick("email")}>
          Email
        </a>
      )}
      {smsUrl && (
        <a href={smsUrl} className="btn btn-secondary" onClick={() => trackContactClick("sms")}>
          Text
        </a>
      )}
      {whatsappUrl && (
        <a
          href={whatsappUrl}
          target="_blank"
          rel="noreferrer"
          className="btn btn-secondary"
          onClick={() => trackContactClick("whatsapp")}
        >
          WhatsApp
        </a>
      )}
    </div>
  );
}
