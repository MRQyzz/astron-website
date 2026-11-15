
import { useEffect, useRef, useState } from "react";
import A from "aladin-lite";

function SkyMap({ onPositionSelect }) {
  const containerRef = useRef(null);
  const aladinRef = useRef(null);
  const onPositionSelectRef = useRef(onPositionSelect);

  const [status, setStatus] = useState("loading");

  // Keep callback current without rebuilding the map.
  useEffect(() => {
    onPositionSelectRef.current = onPositionSelect;
  }, [onPositionSelect]);

  useEffect(() => {
    let cancelled = false;

    async function initializeAladin() {
      try {
        await A.init

        if (cancelled || !containerRef.current) return;

        const aladin = A.aladin(
          containerRef.current,
          {
            survey: "https://stpubdata.s3.us-east-1.amazonaws.com/mast/skybackgrounds/DSSColor",
            target: "83.35 21.68",
            fov: 5,
            cooFrame: "ICRS",
            showCooGridControl: true,
            showLayersControl: true,
            showFullscreenControl: true,
            showReticle: true,
            showCooGrid: false,
            reticleColor: "#818cf8",
            backgroundColor: "#09090b",
          }
        );

        aladinRef.current = aladin;

        // Read sky coordinates when the user clicks the map.
        aladin.on("click", (position) => {
          if (
            position &&
            Number.isFinite(position.ra) &&
            Number.isFinite(position.dec)
          ) {
            onPositionSelectRef.current?.({
              ra: position.ra,
              dec: position.dec,
            });
          }
        });

        setStatus("ready");
      } catch (error) {
        // console.error("Aladin initialization failed:", error);
        // setStatus("error");
        console.error("Aladin initialization failed:", error);
        console.error("Error message:", error?.message);
        console.error("Aladin namespace:", window.A);
        setStatus("error");
      }
    }

    initializeAladin();

    return () => {
      cancelled = true;

      if (aladinRef.current) {
        aladinRef.current.destroy?.();
        aladinRef.current = null;
      }
    };
  }, []);

  return (
    <div className="relative h-full min-h-[420px] w-full overflow-hidden rounded-xl">
      {status === "loading" && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-astron-surface text-sm text-astron-muted">
          Loading astronomical sky map...
        </div>
      )}

      {status === "error" && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-astron-surface p-6 text-center text-sm text-red-400">
          Failed to initialize Aladin Lite. Check your internet connection
          and browser console.
        </div>
      )}

      <div
        ref={containerRef}
        className="h-full min-h-[420px] w-full"
      />
    </div>
  );
}

export default SkyMap;
