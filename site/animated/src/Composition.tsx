/**
 * HargaRumah — Harjamukti Live Demo composition
 *
 * Animation timeline (30 fps, 18s = 540 frames total):
 *   0–60   : Background sky + sun rise in
 *   30–75  : Eyebrow + title fade in
 *   60–180 : CLI window scales up, command types out
 *   180–360: Output log lines stream
 *   360–420: Stats row fades up with stagger
 *   420–540: Listing cards cascade in (top 8 shown)
 */
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import data from "./data.json";

type Listing = {
  id: string;
  title: string;
  price_idr: number;
  url: string;
  land_area_m2: number | null;
  building_area_m2: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  property_type: string;
};

const META = data.metadata as {
  count: number;
  min_price: number;
  max_price: number;
  median_price: number;
  scraped_at: string;
  source: string;
};

const LISTINGS: Listing[] = (data.listings as Listing[])
  .slice()
  .sort((a, b) => a.price_idr - b.price_idr);

const DISPLAY_LISTINGS = LISTINGS.slice(0, 8);

const FPS = 30;

// ---------- helpers ----------

const fmtIDR = (n: number) => {
  if (n >= 1_000_000_000) {
    const v = n / 1_000_000_000;
    const str = v >= 10 ? v.toFixed(1) : v.toFixed(2);
    return `Rp ${str.replace(/\.?0+$/, "")} M`;
  }
  if (n >= 1_000_000) return `Rp ${(n / 1_000_000).toFixed(0)} jt`;
  return `Rp ${n.toLocaleString("id-ID")}`;
};

const isTanah = (l: Listing) =>
  l.property_type === "tanah" ||
  (!l.bedrooms && !l.bathrooms && l.land_area_m2 && !l.building_area_m2);

const escapeHtml = (s: string) =>
  String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[c] as string));

// ---------- atom: typewriter ----------

const Typewriter: React.FC<{
  text: string;
  startFrame: number;
  cps?: number;
  style?: React.CSSProperties;
  showCursor?: boolean;
  cursorStartFrame?: number;
  cursorStopFrame?: number;
}> = ({
  text,
  startFrame,
  cps = 22,
  style,
  showCursor = true,
  cursorStartFrame,
  cursorStopFrame,
}) => {
  const frame = useCurrentFrame();
  const chars = Math.max(
    0,
    Math.min(text.length, Math.floor((frame - startFrame) * (cps / FPS))),
  );
  const visible = text.slice(0, chars);
  const cs = cursorStartFrame ?? startFrame;
  const ce = cursorStopFrame ?? startFrame + Math.ceil(text.length / (cps / FPS)) + 12;
  const cursorOn = showCursor && frame >= cs && frame <= ce && Math.floor(frame / 6) % 2 === 0;
  return (
    <span style={style}>
      {visible}
      {cursorOn && (
        <span
          style={{
            display: "inline-block",
            width: "0.55em",
            height: "1em",
            background: "currentColor",
            marginLeft: 2,
            verticalAlign: "-0.12em",
          }}
        />
      )}
    </span>
  );
};

// ---------- atom: log line ----------

const LogLine: React.FC<{
  text: string;
  prefix?: string;
  prefixColor?: string;
  startFrame: number;
  durationFrames?: number;
  style?: React.CSSProperties;
}> = ({ text, prefix, prefixColor, startFrame, durationFrames = 14, style }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [startFrame, startFrame + durationFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div style={{ opacity, ...style }}>
      {prefix && <span style={{ color: prefixColor }}>{prefix}</span>}
      {text}
    </div>
  );
};

// ---------- stat card ----------

const StatCard: React.FC<{
  label: string;
  value: string;
  index: number;
  startFrame: number;
}> = ({ label, value, index, startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const delay = startFrame + index * 8;
  const scale = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 110 } });
  const y = interpolate(frame - delay, [0, 30], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const opacity = interpolate(frame - delay, [0, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        opacity,
        transform: `translateY(${y}px) scale(${0.85 + 0.15 * scale})`,
        background: "rgba(255,255,255,0.10)",
        border: "1px solid rgba(255,255,255,0.20)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderRadius: 14,
        padding: "16px 22px",
        minWidth: 0,
        display: "flex",
        flexDirection: "column",
        gap: 4,
      }}
    >
      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11,
          letterSpacing: "0.16em",
          textTransform: "uppercase",
          color: "rgba(255,248,231,0.55)",
        }}
      >
        {label}
      </span>
      <span
        style={{
          fontFamily: "var(--font-serif)",
          fontSize: 30,
          color: "var(--gold)",
          letterSpacing: "-0.01em",
          lineHeight: 1.05,
        }}
      >
        {value}
      </span>
    </div>
  );
};

// ---------- listing card ----------

const ListingCard: React.FC<{
  listing: Listing;
  index: number;
  startFrame: number;
}> = ({ listing, index, startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const delay = startFrame + index * 9;
  const y = spring({ frame: frame - delay, fps, config: { damping: 16, stiffness: 90 } });
  const opacity = interpolate(frame - delay, [0, 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pt = isTanah(listing) ? "tanah" : listing.property_type || "rumah";
  const specs: string[] = [];
  if (listing.bedrooms) specs.push(`${listing.bedrooms} KT`);
  if (listing.bathrooms) specs.push(`${listing.bathrooms} KM`);
  if (listing.land_area_m2) specs.push(`LT ${listing.land_area_m2} m²`);
  if (listing.building_area_m2) specs.push(`LB ${listing.building_area_m2} m²`);
  return (
    <div
      style={{
        opacity,
        transform: `translateY(${(1 - y) * 40}px)`,
        background: "rgba(255,255,255,0.08)",
        border: "1px solid rgba(255,255,255,0.16)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        borderRadius: 16,
        padding: "16px 18px",
        display: "flex",
        flexDirection: "column",
        gap: 10,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 12,
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            textTransform: "uppercase",
            letterSpacing: "0.16em",
            color: "rgba(255,248,231,0.55)",
            padding: "3px 7px",
            border: "1px solid rgba(255,255,255,0.20)",
            borderRadius: 4,
          }}
        >
          {escapeHtml(pt)}
        </span>
        <span
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: 20,
            color: "var(--gold)",
            letterSpacing: "-0.01em",
            lineHeight: 1.1,
            textAlign: "right",
          }}
        >
          {fmtIDR(listing.price_idr)}
        </span>
      </div>
      <h3
        style={{
          fontFamily: "var(--font-sans)",
          fontSize: 13,
          fontWeight: 500,
          lineHeight: 1.35,
          color: "var(--cream)",
          display: "-webkit-box",
          WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
        }}
      >
        {escapeHtml(listing.title)}
      </h3>
      {specs.length > 0 && (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "4px 10px",
            fontFamily: "var(--font-mono)",
            fontSize: 10.5,
            color: "rgba(255,248,231,0.7)",
            paddingTop: 8,
            borderTop: "1px solid rgba(255,255,255,0.10)",
          }}
        >
          {specs.map((s, i) => (
            <span key={i}>{s}</span>
          ))}
        </div>
      )}
    </div>
  );
};

// ---------- main composition ----------

export const HarjamuktiDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  const COMMAND = `uv run python main.py "harjamukti" --site rumah123 --min 100`;
  const LOG_LINES: { text: string; prefix?: string; prefixColor?: string; at: number }[] = [
    { text: "resolving area", prefix: "[hargarumah] ", prefixColor: "#FFD580", at: 200 },
    { text: "harjamukti", prefix: "  ", prefixColor: "rgba(255,248,231,0.5)", at: 220 },
    { text: "launching browser (CDP)", prefix: "[hargarumah] ", prefixColor: "#FFD580", at: 240 },
    { text: "rumah123  scraping 'harjamukti'", prefix: "[hargarumah] ", prefixColor: "#FFD580", at: 264 },
    { text: "rumah123  55 listings / 3 pages", prefix: "[hargarumah] ", prefixColor: "#FFD580", at: 296 },
    { text: "55 listings, 1 source", prefix: "ok  ", prefixColor: "#7CFFA8", at: 320 },
    { text: "site/data/harjamukti.json", prefix: "saved  ", prefixColor: "rgba(255,248,231,0.55)", at: 340 },
  ];

  // Title block
  const titleStart = 28;
  const titleY = interpolate(frame, [titleStart, titleStart + 50], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const titleOp = interpolate(frame, [titleStart, titleStart + 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // CLI window
  const cliStart = 50;
  const cliProgress = spring({ frame: frame - cliStart, fps, config: { damping: 18, stiffness: 100 } });
  const cliOp = interpolate(frame, [cliStart, cliStart + 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const commandFinishFrame = cliStart + 12 + Math.ceil(COMMAND.length / 22) * FPS / FPS * 1.0;
  const commandEnd = cliStart + 8 + Math.round((COMMAND.length / 22) * FPS);
  const firstLogFrame = commandEnd + 6;

  // Map LOG_LINES `at` relative to absolute timeline
  const ABS_LOGS = LOG_LINES.map((l) => ({ ...l, at: firstLogFrame + (l.at - 200) }));

  // Stats
  const statsStart = 380;
  const statsOp = interpolate(frame, [statsStart, statsStart + 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const statsY = interpolate(frame, [statsStart, statsStart + 30], [16, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Cards
  const cardsStart = 440;

  return (
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(180deg, #0B1437 0%, #1F1547 28%, #4A2D5E 56%, #8B3A62 78%, #FF8E72 100%)",
        fontFamily: "var(--font-sans)",
        color: "var(--cream)",
        overflow: "hidden",
      }}
    >
      {/* sun glow */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "78%",
          width: 1100,
          height: 1100,
          transform: "translate(-50%, -50%)",
          background: "radial-gradient(circle, rgba(255,213,128,0.55) 0%, rgba(255,142,114,0.25) 35%, transparent 65%)",
          pointerEvents: "none",
          filter: "blur(8px)",
        }}
      />

      {/* horizon line */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: "82%",
          height: 1,
          background: "linear-gradient(90deg, transparent 0%, rgba(255,213,128,0.6) 50%, transparent 100%)",
          pointerEvents: "none",
        }}
      />

      {/* title block */}
      <div
        style={{
          position: "absolute",
          top: 90,
          left: 80,
          right: 80,
          opacity: titleOp,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 18,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "rgba(255,213,128,0.85)",
            marginBottom: 16,
          }}
        >
          Live demo · {META.count} rumah dijual
        </div>
        <h1
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: 110,
            fontWeight: 400,
            lineHeight: 0.95,
            color: "var(--cream)",
            letterSpacing: "-0.02em",
          }}
        >
          Harjamukti
        </h1>
        <div
          style={{
            marginTop: 14,
            fontFamily: "var(--font-sans)",
            fontSize: 22,
            color: "rgba(255,248,231,0.7)",
          }}
        >
          Cimanggis, Depok · scraped {new Date(META.scraped_at).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}
        </div>
      </div>

      {/* CLI window */}
      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          top: 360,
          opacity: cliOp,
          transform: `scale(${0.94 + 0.06 * cliProgress})`,
          transformOrigin: "top center",
        }}
      >
        <div
          style={{
            background: "rgba(11, 20, 55, 0.55)",
            border: "1px solid rgba(255,255,255,0.18)",
            borderRadius: 16,
            backdropFilter: "blur(28px)",
            WebkitBackdropFilter: "blur(28px)",
            boxShadow: "0 24px 80px rgba(0,0,0,0.35)",
            overflow: "hidden",
          }}
        >
          {/* chrome */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "14px 18px",
              borderBottom: "1px solid rgba(255,255,255,0.10)",
              background: "rgba(255,255,255,0.04)",
            }}
          >
            <span style={{ width: 12, height: 12, borderRadius: 6, background: "#FF8E72" }} />
            <span style={{ width: 12, height: 12, borderRadius: 6, background: "#FFD580" }} />
            <span style={{ width: 12, height: 12, borderRadius: 6, background: "#7CFFA8" }} />
            <span
              style={{
                marginLeft: 16,
                fontFamily: "var(--font-mono)",
                fontSize: 13,
                color: "rgba(255,248,231,0.55)",
                letterSpacing: "0.04em",
              }}
            >
              hargarumah@terminal — main.py
            </span>
          </div>

          {/* body */}
          <div
            style={{
              padding: "22px 24px",
              fontFamily: "var(--font-mono)",
              fontSize: 18,
              lineHeight: 1.65,
              color: "rgba(255,248,231,0.85)",
            }}
          >
            <div>
              <span style={{ color: "rgba(255,213,128,0.7)" }}>$</span>{" "}
              <Typewriter
                text={COMMAND}
                startFrame={cliStart + 12}
                cps={26}
                cursorStopFrame={commandEnd}
                style={{ color: "var(--cream)" }}
              />
            </div>
            {ABS_LOGS.map((l, i) => (
              <LogLine
                key={i}
                text={l.text}
                prefix={l.prefix}
                prefixColor={l.prefixColor}
                startFrame={l.at}
              />
            ))}
            {/* blinking cursor at bottom after last log */}
            {frame > ABS_LOGS[ABS_LOGS.length - 1].at + 18 && frame < statsStart - 6 && (
              <div style={{ marginTop: 4 }}>
                <span style={{ color: "rgba(255,213,128,0.7)" }}>$</span>{" "}
                <span
                  style={{
                    display: "inline-block",
                    width: "0.55em",
                    height: "1em",
                    background: "rgba(255,248,231,0.85)",
                    verticalAlign: "-0.12em",
                    opacity: Math.floor(frame / 6) % 2 === 0 ? 1 : 0,
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* stats row */}
      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          top: 920,
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 16,
          opacity: statsOp,
          transform: `translateY(${statsY}px)`,
        }}
      >
        <StatCard label="Listing" value={String(META.count)} index={0} startFrame={statsStart} />
        <StatCard label="Harga min" value={fmtIDR(META.min_price)} index={1} startFrame={statsStart} />
        <StatCard label="Harga median" value={fmtIDR(META.median_price)} index={2} startFrame={statsStart} />
        <StatCard label="Harga max" value={fmtIDR(META.max_price)} index={3} startFrame={statsStart} />
      </div>

      {/* listing cards */}
      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          bottom: 70,
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 14,
        }}
      >
        {DISPLAY_LISTINGS.map((l, i) => (
          <ListingCard key={l.id} listing={l} index={i} startFrame={cardsStart} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
