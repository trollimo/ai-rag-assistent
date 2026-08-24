"use client";

import { useEffect, useRef, useState } from "react";

export type MascotState = "idle" | "thinking" | "happy";

const DEFAULT_SIZE = 84;

export default function Mascot({ state }: { state: MascotState }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("mascotPos");
    if (stored) {
      try {
        setPos(JSON.parse(stored));
        return;
      } catch {
        /* fall through to default */
      }
    }
    setPos({ x: window.innerWidth - DEFAULT_SIZE - 24, y: window.innerHeight - DEFAULT_SIZE - 24 });
  }, []);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      setPos({
        x: Math.min(window.innerWidth - DEFAULT_SIZE, Math.max(0, e.clientX - DEFAULT_SIZE / 2)),
        y: Math.min(window.innerHeight - DEFAULT_SIZE, Math.max(0, e.clientY - DEFAULT_SIZE / 2)),
      });
    };
    const onUp = () => {
      if (!dragging.current) return;
      dragging.current = false;
      if (wrapRef.current) wrapRef.current.style.cursor = "grab";
      setPos((p) => {
        if (p) localStorage.setItem("mascotPos", JSON.stringify(p));
        return p;
      });
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, []);

  if (!pos) return null;

  return (
    <div
      ref={wrapRef}
      onMouseDown={() => {
        dragging.current = true;
        if (wrapRef.current) wrapRef.current.style.cursor = "grabbing";
      }}
      title="Архивариус"
      style={{
        position: "fixed",
        left: pos.x,
        top: pos.y,
        width: DEFAULT_SIZE,
        height: DEFAULT_SIZE,
        cursor: "grab",
        zIndex: 40,
        userSelect: "none",
      }}
    >
      <div className="mascot-float" style={{ width: "100%", height: "100%" }}>
        <svg width={DEFAULT_SIZE} height={DEFAULT_SIZE} viewBox="0 0 160 160">
          <rect x="30" y="24" width="100" height="104" rx="8" fill="#F1EFE8" stroke="#D3D1C7" strokeWidth="1" />
          <line x1="44" y1="36" x2="116" y2="36" stroke="#B4B2A9" strokeWidth="2.5" strokeLinecap="round" opacity="0.8" />
          <line x1="44" y1="44" x2="104" y2="44" stroke="#B4B2A9" strokeWidth="2.5" strokeLinecap="round" opacity="0.8" />
          <line x1="44" y1="52" x2="96" y2="52" stroke="#B4B2A9" strokeWidth="2.5" strokeLinecap="round" opacity="0.8" />
          <line x1="80" y1="24" x2="80" y2="128" stroke="#B4B2A9" strokeWidth="1" opacity="0.4" strokeDasharray="2 3" />

          <g className="mascot-sway" style={{ transformOrigin: "80px 16px" }}>
            <path d="M72 12 L72 50 L80 42 L88 50 L88 12 Z" fill="#BA7517" />
          </g>

          <ellipse cx="46" cy="132" rx="7" ry="4" fill="#0F6E56" />
          <ellipse cx="114" cy="132" rx="7" ry="4" fill="#0F6E56" />
          <ellipse cx="80" cy="140" rx="44" ry="6" fill="#04342C" opacity="0.16" />

          <rect x="118" y="66" width="3" height="58" fill="#0F6E56" />
          <rect x="122" y="68" width="3" height="54" fill="#085041" />

          <rect x="30" y="58" width="100" height="70" rx="7" fill="#1D9E75" stroke="#085041" strokeWidth="1.5" />
          <rect x="31" y="61" width="17" height="64" rx="6" fill="#0F6E56" />
          <ellipse cx="70" cy="76" rx="20" ry="10" fill="#5DCAA5" opacity="0.4" />

          <path d="M130 58 L130 74 L114 58 Z" fill="#BA7517" opacity="0.85" />
          <path d="M130 128 L130 112 L114 128 Z" fill="#BA7517" opacity="0.85" />

          {state === "idle" && (
            <g>
              <circle className="mascot-blink" cx="66" cy="96" r="12" fill="#FFFFFF" />
              <circle className="mascot-blink" cx="98" cy="96" r="12" fill="#FFFFFF" />
              <circle className="mascot-blink" cx="66" cy="96" r="5" fill="#04342C" />
              <circle className="mascot-blink" cx="98" cy="96" r="5" fill="#04342C" />
            </g>
          )}

          {state === "thinking" && (
            <g>
              <circle cx="66" cy="96" r="12" fill="#FFFFFF" />
              <circle cx="98" cy="96" r="12" fill="#FFFFFF" />
              <circle cx="69" cy="91" r="5" fill="#04342C" />
              <circle cx="101" cy="91" r="5" fill="#04342C" />
              <path d="M56 82 Q66 76 76 82" fill="none" stroke="#04342C" strokeWidth="2" strokeLinecap="round" />
              <g className="mascot-dot-pulse">
                <circle cx="118" cy="34" r="3.5" fill="#F1EFE8" />
                <circle cx="128" cy="27" r="3" fill="#F1EFE8" style={{ animationDelay: ".15s" }} />
                <circle cx="136" cy="18" r="2.5" fill="#F1EFE8" style={{ animationDelay: ".3s" }} />
              </g>
            </g>
          )}

          {state === "happy" && (
            <g>
              <path d="M58 98 Q66 88 74 98" fill="none" stroke="#04342C" strokeWidth="3" strokeLinecap="round" />
              <path d="M90 98 Q98 88 106 98" fill="none" stroke="#04342C" strokeWidth="3" strokeLinecap="round" />
              <ellipse cx="60" cy="108" rx="6" ry="3.5" fill="#F0997B" opacity="0.6" />
              <ellipse cx="104" cy="108" rx="6" ry="3.5" fill="#F0997B" opacity="0.6" />
              <circle cx="138" cy="30" r="13" fill="#639922" />
              <path d="M132 30 L137 35 L145 25" fill="none" stroke="#EAF3DE" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </g>
          )}
        </svg>
      </div>

      <style jsx>{`
        .mascot-float {
          animation: mascot-bob 3s ease-in-out infinite;
        }
        @keyframes mascot-bob {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        .mascot-blink {
          animation: mascot-blink 4.5s ease-in-out infinite;
          transform-origin: center;
        }
        @keyframes mascot-blink {
          0%, 92%, 100% { transform: scaleY(1); }
          96% { transform: scaleY(0.1); }
        }
        .mascot-sway {
          animation: mascot-sway 2.6s ease-in-out infinite;
        }
        @keyframes mascot-sway {
          0%, 100% { transform: rotate(-4deg); }
          50% { transform: rotate(4deg); }
        }
        .mascot-dot-pulse circle {
          animation: mascot-pulse 1.2s ease-in-out infinite;
        }
        @keyframes mascot-pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
