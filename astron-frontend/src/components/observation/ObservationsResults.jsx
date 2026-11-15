
function ObservationResults({
  observations,
  loading,
  error,
  searchInfo,
}) {
  if (loading) {
    return (
      <div className="rounded-xl border border-astron-border bg-astron-surface p-5">
        <p className="text-sm text-astron-muted">
          Searching SPHEREx observations...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5">
        <h3 className="font-semibold text-red-400">
          Search Failed
        </h3>
        <p className="mt-2 text-sm text-astron-muted">
          {error}
        </p>
      </div>
    );
  }

  if (!searchInfo) {
    return (
      <div className="rounded-xl border border-astron-border bg-astron-surface p-5">
        <h3 className="font-semibold">SPHEREx Observations</h3>
        <p className="mt-2 text-sm text-astron-muted">
          Search a sky position to discover available observations.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-astron-border bg-astron-surface p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="font-semibold">SPHEREx Observations</h3>
          <p className="mt-1 text-xs text-astron-muted">
            Data provider: {searchInfo.provider}
          </p>
        </div>

        <span className="rounded-full bg-astron-primary/15 px-3 py-1 text-xs text-astron-accent">
          {searchInfo.result_count} Results
        </span>
      </div>

      {observations.length === 0 ? (
        <p className="mt-5 text-sm text-astron-muted">
          No observations were found in this region.
        </p>
      ) : (
        <div className="mt-5 space-y-3">
          {observations.map((observation, index) => (
            <div
              key={observation.obs_id ?? index}
              className="rounded-lg border border-astron-border p-4"
            >
              <h4 className="break-all text-sm font-semibold">
                {observation.obs_id ?? `Observation ${index + 1}`}
              </h4>

              <div className="mt-3 grid grid-cols-2 gap-3">
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
                    Data Format
                  </p>
                  <p className="mt-1 break-all text-sm">
                    {observation.access_format ?? "N/A"}
                  </p>
                </div>
              </div>

              <p className="mt-3 text-xs text-astron-muted">
                {observation.access_url
                  ? "FITS product available"
                  : "No access URL provided"}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ObservationResults;
