
import { useState } from "react";
import SkyMap from "../components/sky-map/SkyMap";
import { Link } from "react-router-dom";
import {
  Search,
  Telescope,
  Database,
  Orbit,
  LoaderCircle,
  AlertCircle,
  Satellite,
} from "lucide-react";

import { searchObservations } from "../services/observations";

function ExplorerPage() {
  // Selected position from Aladin Lite
  const [selectedPosition, setSelectedPosition] = useState(null);

  // Coordinate search inputs
  const [coordinates, setCoordinates] = useState({
    ra: "",
    dec: "",
    radius: "0.5",
  });

  // Observation search states
  const [observations, setObservations] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [searchInfo, setSearchInfo] = useState(null);

  // Handle position selected from sky map
  function handlePositionSelect(position) {
    setSelectedPosition(position);

    setCoordinates((previous) => ({
      ...previous,
      ra: position.ra.toFixed(6),
      dec: position.dec.toFixed(6),
    }));
  }

  // Handle coordinate input changes
  function handleCoordinateChange(event) {
    const { name, value } = event.target;

    setCoordinates((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  // Search observations through FastAPI
  async function handleCoordinateSearch(event) {
    event.preventDefault();

    const { ra, dec, radius } = coordinates;

    if (ra === "" || dec === "" || radius === "") {
      setSearchError("Please complete all coordinate fields.");
      return;
    }

    const raValue = Number(ra);
    const decValue = Number(dec);
    const radiusValue = Number(radius);

    if (
      !Number.isFinite(raValue) ||
      !Number.isFinite(decValue) ||
      !Number.isFinite(radiusValue) ||
      raValue < 0 ||
      raValue >= 360 ||
      decValue < -90 ||
      decValue > 90 ||
      radiusValue <= 0 ||
      radiusValue > 180
    ) {
      setSearchError("Invalid coordinates or search radius.");
      return;
    }

    setSearchLoading(true);
    setSearchError("");
    setObservations([]);
    setSearchInfo(null);

    try {
      const response = await searchObservations({
        ra: raValue,
        dec: decValue,
        radius: radiusValue,
      });

      setObservations(response.results ?? []);
      setSearchInfo(response);
    } catch (error) {
      setSearchError(error.message || "Unable to search observations.");
    } finally {
      setSearchLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-astron-bg text-astron-text">

      {/* Top Navigation */}
      <header className="flex h-16 items-center justify-between border-b border-astron-border px-6">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-astron-primary font-bold">
            A
          </div>

          <span className="font-bold tracking-[0.2em]">
            ASTRON
          </span>
        </Link>

        <div className="flex items-center gap-2 text-sm text-astron-muted">
          <Orbit size={16} />
          <span>Sky Explorer</span>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="grid min-h-[calc(100vh-4rem)] lg:grid-cols-[320px_1fr]">

        {/* Search Sidebar */}
        <aside className="border-b border-astron-border p-6 lg:border-b-0 lg:border-r">

          <div className="mb-8">
            <div className="mb-3 flex items-center gap-2">
              <Search size={18} className="text-astron-accent" />
              <h2 className="font-semibold">Search Sky</h2>
            </div>

            <p className="text-sm leading-6 text-astron-muted">
              Search for celestial objects or explore a region using sky
              coordinates.
            </p>
          </div>

          {/* Object Search */}
          <div className="space-y-3">
            <label className="text-sm font-medium">
              Object Name
            </label>

            <input
              type="text"
              placeholder="e.g. Orion Nebula"
              className="w-full rounded-lg border border-astron-border bg-astron-surface px-4 py-3 text-sm outline-none transition placeholder:text-astron-muted focus:border-astron-primary"
            />

            <button
              type="button"
              disabled
              className="flex w-full cursor-not-allowed items-center justify-center gap-2 rounded-lg bg-astron-primary/50 px-4 py-3 text-sm font-semibold opacity-60"
            >
              <Search size={16} />
              Search Object
            </button>

            <p className="text-xs text-astron-muted">
              Object catalog search is not available yet.
            </p>
          </div>

          {/* Coordinate Search */}
          <form
            onSubmit={handleCoordinateSearch}
            className="mt-8 border-t border-astron-border pt-6"
          >
            <h3 className="mb-4 text-sm font-semibold">
              Coordinate Search
            </h3>

            <div className="space-y-3">

              <div>
                <label className="mb-2 block text-xs text-astron-muted">
                  Right Ascension (RA)
                </label>

                <input
                  type="number"
                  name="ra"
                  value={coordinates.ra}
                  onChange={handleCoordinateChange}
                  placeholder="0 – 360°"
                  min="0"
                  max="359.999999"
                  step="any"
                  required
                  className="w-full rounded-lg border border-astron-border bg-astron-surface px-4 py-3 text-sm outline-none focus:border-astron-primary"
                />
              </div>

              <div>
                <label className="mb-2 block text-xs text-astron-muted">
                  Declination (Dec)
                </label>

                <input
                  type="number"
                  name="dec"
                  value={coordinates.dec}
                  onChange={handleCoordinateChange}
                  placeholder="-90 – 90°"
                  min="-90"
                  max="90"
                  step="any"
                  required
                  className="w-full rounded-lg border border-astron-border bg-astron-surface px-4 py-3 text-sm outline-none focus:border-astron-primary"
                />
              </div>

              <div>
                <label className="mb-2 block text-xs text-astron-muted">
                  Search Radius (degrees)
                </label>

                <input
                  type="number"
                  name="radius"
                  value={coordinates.radius}
                  onChange={handleCoordinateChange}
                  placeholder="Search radius"
                  min="0.001"
                  max="180"
                  step="any"
                  required
                  className="w-full rounded-lg border border-astron-border bg-astron-surface px-4 py-3 text-sm outline-none focus:border-astron-primary"
                />
              </div>

              <button
                type="submit"
                disabled={searchLoading}
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-astron-border px-4 py-3 text-sm font-medium transition hover:bg-astron-surface disabled:cursor-not-allowed disabled:opacity-50"
              >
                {searchLoading ? (
                  <>
                    <LoaderCircle size={16} className="animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search size={16} />
                    Search Coordinates
                  </>
                )}
              </button>
            </div>
          </form>
        </aside>

        {/* Main Content */}
        <section className="flex min-w-0 flex-col p-6">

          {/* Workspace Heading */}
          <div className="mb-6">
            <p className="text-xs tracking-[0.25em] text-astron-accent">
              ASTRONOMICAL WORKSPACE
            </p>

            <h1 className="mt-2 text-2xl font-semibold">
              Sky Explorer
            </h1>

            <p className="mt-2 text-sm text-astron-muted">
              Navigate and investigate the infrared universe.
            </p>
          </div>

          {/* Sky Map */}
          <div className="flex min-h-[420px] flex-col overflow-hidden rounded-xl border border-astron-border bg-astron-surface">
            <div className="flex items-center justify-between border-b border-astron-border px-4 py-3">
              <div>
                <h2 className="text-sm font-semibold">
                  Sky Map
                </h2>

                <p className="text-xs text-astron-muted">
                  Click anywhere to select a sky position
                </p>
              </div>

              <span className="text-xs text-astron-muted">
                ICRS
              </span>
            </div>

            <div className="flex-1">
              <SkyMap onPositionSelect={handlePositionSelect} />
            </div>
          </div>

          {/* Selected Position */}
          <div className="mt-4 rounded-xl border border-astron-border bg-astron-surface p-4">
            <h3 className="text-sm font-semibold">
              Selected Position
            </h3>

            {selectedPosition ? (
              <div className="mt-3 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-astron-muted">
                    Right Ascension
                  </p>

                  <p className="mt-1 font-mono text-sm">
                    {selectedPosition.ra.toFixed(6)}°
                  </p>
                </div>

                <div>
                  <p className="text-xs text-astron-muted">
                    Declination
                  </p>

                  <p className="mt-1 font-mono text-sm">
                    {selectedPosition.dec.toFixed(6)}°
                  </p>
                </div>
              </div>
            ) : (
              <p className="mt-2 text-sm text-astron-muted">
                No position selected. Click on the sky map.
              </p>
            )}
          </div>

          {/* Catalog Results */}
          <div className="mt-6 rounded-xl border border-astron-border bg-astron-surface p-5">
            <Database size={20} className="text-astron-accent" />

            <h3 className="mt-4 font-semibold">
              Catalog Results
            </h3>

            <p className="mt-2 text-sm text-astron-muted">
              Celestial object information from astronomical catalogs.
            </p>

            <p className="mt-3 text-xs text-astron-muted">
              Catalog integration is currently under development.
            </p>
          </div>

          {/* SPHEREx Observation Results */}
          <div className="mt-6 rounded-xl border border-astron-border bg-astron-surface p-5">

            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <Telescope size={20} className="text-astron-accent" />

                <div>
                  <h3 className="font-semibold">
                    SPHEREx Observations
                  </h3>

                  <p className="text-xs text-astron-muted">
                    Observation data from IRSA
                  </p>
                </div>
              </div>

              {searchInfo && (
                <span className="rounded-full bg-astron-primary/15 px-3 py-1 text-xs text-astron-accent">
                  {searchInfo.result_count} Results
                </span>
              )}
            </div>

            {/* Initial State */}
            {!searchLoading && !searchError && !searchInfo && (
              <p className="mt-5 text-sm text-astron-muted">
                Select a sky position or enter coordinates to search
                available SPHEREx observations.
              </p>
            )}

            {/* Loading State */}
            {searchLoading && (
              <div className="mt-6 flex items-center gap-3 text-sm text-astron-muted">
                <LoaderCircle
                  size={18}
                  className="animate-spin text-astron-accent"
                />

                Searching IRSA observation archive...
              </div>
            )}

            {/* Error State */}
            {!searchLoading && searchError && (
              <div className="mt-5 flex items-start gap-3 rounded-lg border border-red-500/30 bg-red-500/5 p-4">
                <AlertCircle
                  size={18}
                  className="mt-0.5 shrink-0 text-red-400"
                />

                <div>
                  <h4 className="text-sm font-semibold text-red-400">
                    Search Failed
                  </h4>

                  <p className="mt-1 text-sm text-astron-muted">
                    {searchError}
                  </p>
                </div>
              </div>
            )}

            {/* Empty Results */}
            {!searchLoading &&
              !searchError &&
              searchInfo &&
              observations.length === 0 && (
                <div className="mt-6 rounded-lg border border-astron-border p-5 text-center">
                  <Satellite
                    size={24}
                    className="mx-auto text-astron-muted"
                  />

                  <p className="mt-3 text-sm font-medium">
                    No observations found
                  </p>

                  <p className="mt-1 text-xs text-astron-muted">
                    Try another position or increase the search radius.
                  </p>
                </div>
              )}

            {/* Observation List */}
            {!searchLoading &&
              !searchError &&
              observations.length > 0 && (
                <div className="mt-5 space-y-3">

                  {observations.map((observation, index) => (
                    <div
                      key={observation.obs_id ?? index}
                      className="rounded-lg border border-astron-border p-4 transition hover:bg-astron-surface-hover"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="text-xs text-astron-muted">
                            Observation ID
                          </p>

                          <h4 className="mt-1 break-all text-sm font-semibold">
                            {observation.obs_id ??
                              `Observation ${index + 1}`}
                          </h4>
                        </div>

                        <span className="rounded-md border border-astron-border px-2 py-1 text-xs text-astron-muted">
                          {observation.access_format ?? "Unknown format"}
                        </span>
                      </div>

                      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                          <p className="text-xs text-astron-muted">
                            Collection
                          </p>

                          <p className="mt-1 break-all text-sm">
                            {observation.obs_collection ?? "N/A"}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs text-astron-muted">
                            Instrument
                          </p>

                          <p className="mt-1 break-all text-sm">
                            {observation.instrument_name ?? "N/A"}
                          </p>
                        </div>
                      </div>

                      <div className="mt-4 flex items-center justify-between border-t border-astron-border pt-3">
                        <span className="text-xs text-astron-muted">
                          {observation.access_url
                            ? "FITS product available"
                            : "No product URL available"}
                        </span>

                        <span className="text-xs text-astron-accent">
                          IRSA
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

            {/* Search Metadata */}
            {searchInfo && (
              <div className="mt-5 border-t border-astron-border pt-4">
                <p className="text-xs text-astron-muted">
                  Search center: RA{" "}
                  {searchInfo.search_parameters.ra.toFixed(4)}°,
                  Dec{" "}
                  {searchInfo.search_parameters.dec.toFixed(4)}°
                  {" · "}
                  Radius: {searchInfo.search_parameters.radius}°
                </p>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export default ExplorerPage;
