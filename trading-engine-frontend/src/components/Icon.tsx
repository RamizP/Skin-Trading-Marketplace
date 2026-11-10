import type { CSSProperties } from "react";

const paths = {
  market: "M3 10l9-7 9 7M5 9v11h14V9M9 20v-7h6v7",
  inventory: "M3 7l9-4 9 4v10l-9 4-9-4V7zm0 0l9 5 9-5M12 12v9",
  orders: "M7 3h10v4H7zM5 5H3v16h18V5h-2M7 11h10M7 15h7",
  case: "M8 6V3h8v3M3 7h18v14H3V7zm0 5h18M10 10h4v5h-4z",
  search: "M21 21l-5-5M18 10a8 8 0 11-16 0 8 8 0 0116 0z",
  arrow: "M5 12h14m-6-6l6 6-6 6",
  chevron: "M9 5l7 7-7 7",
  back: "M19 12H5m6-6l-6 6 6 6",
  close: "M6 6l12 12M6 18L18 6",
  plus: "M12 5v14M5 12h14",
  wallet: "M20 8V5H5a2 2 0 010-4h13M4 3v16a2 2 0 002 2h14V8H5M20 12h-6v5h6",
  logout: "M9 5H3v14h6M13 7l5 5-5 5M8 12h13",
  refresh: "M20 7v5h-5M4 17v-5h5M5 7a8 8 0 0113-2l2 3M4 16l2 3a8 8 0 0013-2",
  check: "M5 12l4 4L20 5",
  shield: "M12 2l9 4v6c0 5-9 10-9 10S3 17 3 12V6l9-4zm-5 10l3 3 7-7",
  bolt: "M13 2L4 14h7l-1 8 10-12h-7l0-8z",
  grid: "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z",
  list: "M8 6h13M8 12h13M8 18h13M3 6h1M3 12h1M3 18h1",
  lock: "M5 10h14v11H5zM8 10V6a4 4 0 018 0v4M12 14v3",
  info: "M12 10v7M12 6v1M22 12a10 10 0 11-20 0 10 10 0 0120 0z",
  globe:
    "M22 12a10 10 0 11-20 0 10 10 0 0120 0zM2 12h20M12 2a20 20 0 010 20 20 20 0 010-20z",
  spark: "M12 2l3 7 7 3-7 3-3 7-3-7-7-3 7-3 3-7z",
  menu: "M3 6h18M3 12h18M3 18h18",
  eye: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zm13 0a3 3 0 11-6 0 3 3 0 016 0z",
} as const;

export type IconName = keyof typeof paths;
export default function Icon({
  name,
  size = 20,
  style,
}: {
  name: IconName;
  size?: number;
  style?: CSSProperties;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={style}
    >
      <path d={paths[name]} />
    </svg>
  );
}
