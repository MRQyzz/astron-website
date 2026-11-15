
import { Link } from "react-router-dom";
import Navbar from "../components/layout/Navbar";

function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-astron-bg text-astron-text">
      <Navbar />

      {/* Hero Section */}
      <section className="relative flex min-h-screen items-center">
        {/* Background decoration */}
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -right-40 top-20 h-[500px] w-[500px] rounded-full bg-indigo-600/10 blur-[120px]" />
          <div className="absolute -left-40 bottom-0 h-[400px] w-[400px] rounded-full bg-blue-600/10 blur-[120px]" />
        </div>

        <div className="relative mx-auto w-full max-w-7xl px-6 pb-20 pt-32 lg:px-10">
          <div className="max-w-4xl">
            <div className="mb-8 inline-flex items-center gap-3 rounded-full border border-astron-border bg-astron-surface/70 px-4 py-2">
              <span className="h-2 w-2 rounded-full bg-astron-accent" />
              <span className="text-xs tracking-widest text-astron-muted">
                EXPLORE THE INFRARED UNIVERSE
              </span>
            </div>

            <h1 className="text-5xl font-semibold leading-tight tracking-tight sm:text-6xl lg:text-8xl">
              Discover the
              <span className="block bg-gradient-to-r from-indigo-400 to-blue-300 bg-clip-text text-transparent">
                Invisible Universe.
              </span>
            </h1>

            <p className="mt-8 max-w-2xl text-base leading-8 text-astron-muted sm:text-lg">
              Explore astronomical observations through infrared data.
              Discover celestial objects, investigate observations, and
              navigate the universe through an interactive scientific platform.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link
                to="/explorer"
                className="rounded-xl bg-astron-primary px-7 py-4 text-sm font-semibold text-white transition hover:bg-astron-accent"
              >
                Start Exploring →
              </Link>

              <a
                href="#about"
                className="rounded-xl border border-astron-border px-7 py-4 text-sm font-semibold text-astron-text transition hover:bg-astron-surface"
              >
                Learn More
              </a>
            </div>
          </div>

          <div className="mt-24 border-t border-white/10 pt-8">
            <p className="text-xs tracking-[0.3em] text-astron-muted">
              A NEW PERSPECTIVE ON THE COSMOS
            </p>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="border-t border-white/10 py-28">
        <div className="mx-auto max-w-7xl px-6 lg:px-10">
          <p className="text-sm font-medium tracking-[0.25em] text-astron-accent">
            ABOUT ASTRON
          </p>

          <h2 className="mt-5 max-w-3xl text-3xl font-semibold leading-tight sm:text-5xl">
            Turning astronomical data into meaningful exploration.
          </h2>

          <p className="mt-8 max-w-2xl leading-8 text-astron-muted">
            ASTRON provides an accessible environment for exploring
            astronomical catalogs and infrared observations. It connects
            scientific data retrieval with interactive visualization to
            support the investigation of the universe.
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section id="mission" className="border-t border-white/10 bg-astron-surface/30 py-28">
        <div className="mx-auto max-w-7xl px-6 lg:px-10">
          <p className="text-sm font-medium tracking-[0.25em] text-astron-accent">
            OUR MISSION
          </p>

          <div className="mt-6 grid gap-10 md:grid-cols-3">
            <div>
              <h3 className="text-xl font-semibold">Discover</h3>
              <p className="mt-4 leading-7 text-astron-muted">
                Search celestial objects and explore their astronomical
                catalog information.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold">Observe</h3>
              <p className="mt-4 leading-7 text-astron-muted">
                Find available infrared observations and investigate
                their associated data.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold">Explore</h3>
              <p className="mt-4 leading-7 text-astron-muted">
                Navigate astronomical observations through an interactive
                sky exploration interface.
              </p>
            </div>
          </div>

          <Link
            to="/explorer"
            className="mt-12 inline-flex rounded-xl bg-astron-primary px-7 py-4 text-sm font-semibold text-white transition hover:bg-astron-accent"
          >
            Launch ASTRON Explorer →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-3 px-6 text-sm text-astron-muted sm:flex-row lg:px-10">
          <p>ASTRON — Astronomical Observation Network</p>
          <p>Exploring the universe through data.</p>
        </div>
      </footer>
    </main>
  );
}

export default LandingPage;
