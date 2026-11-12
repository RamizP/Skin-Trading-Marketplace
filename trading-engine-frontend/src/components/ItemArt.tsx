import { useId, useState } from "react";
import type { Entity } from "../api/types";

export default function ItemArt({
  entity,
  caseItem = false,
  className = "",
  loading = "lazy",
}: {
  entity?: Entity;
  caseItem?: boolean;
  className?: string;
  loading?: "eager" | "lazy";
}) {
  const [failedUrl, setFailedUrl] = useState("");
  const gradient = useId();
  const url = entity?.image_url;
  if (url && failedUrl !== url) {
    return (
      <img
        className={`item-art ${className}`}
        src={url}
        alt={entity.name}
        loading={loading}
        onError={() => setFailedUrl(url)}
      />
    );
  }
  return (
    <svg
      className={`item-art fallback-art ${className}`}
      viewBox="0 0 360 220"
      role="img"
      aria-label={entity?.name || "Collectible artwork"}
    >
      <defs>
        <linearGradient id={gradient} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="currentColor" />
          <stop offset="1" stopColor="#353943" />
        </linearGradient>
      </defs>
      {caseItem ? (
        <g transform="rotate(-9 180 110)">
          <path
            d="M113 62V43h133v19"
            fill="none"
            stroke="#94999c"
            strokeWidth="10"
          />
          <path
            d="M63 72l32-19h198l22 19-24 112H80z"
            fill={`url(#${gradient})`}
            stroke="#797f87"
            strokeWidth="3"
          />
          <path d="M63 72h252l-9 39H72z" fill="#c7a564" opacity=".4" />
          <path
            d="M100 111v58m161-58v58M160 96h45v40h-45z"
            stroke="#14181d"
            strokeWidth="9"
          />
          <path d="M172 108h22v14h-22z" fill="#eece8e" />
          <path
            d="M107 148h29m-29 9h21"
            stroke="#f9dfac"
            strokeWidth="3"
            opacity=".5"
          />
        </g>
      ) : (
        <g transform="rotate(-19 180 110)">
          <path
            d="M32 99h55l12-18h107l7 9h95v13h-98l-8 23h-37l-8 49h-23l8-49h-22l-17-15H69l-33 24z"
            fill={`url(#${gradient})`}
            stroke="#9ca1aa"
            strokeWidth="2"
          />
          <path
            d="M176 125l9 44h29l-16-44M94 82l4-16h27v15M244 82v8m36-8v8M307 90h23v12h-23"
            fill="#626974"
            stroke="#8a909b"
            strokeWidth="2"
          />
          <path
            d="M105 94h81m-62 15h58M225 97h68M43 105l25 0"
            stroke="#f5f1e5"
            strokeWidth="3"
            opacity=".55"
          />
        </g>
      )}
    </svg>
  );
}
