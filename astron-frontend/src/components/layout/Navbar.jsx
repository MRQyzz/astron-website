
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <header className="fixed top-0 z-50 w-full border-b border-white/10 bg-astron-bg/80 backdrop-blur-xl">
      <nav className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-10">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-astron-primary text-lg font-bold text-white">
            A
          </div>

          <div>
            <h1 className="text-lg font-bold tracking-[0.2em] text-white">
              ASTRON
            </h1>
            <p className="text-[9px] tracking-[0.25em] text-astron-muted">
              ASTRONOMICAL OBSERVATION NETWORK
            </p>
          </div>
        </Link>

        {/* Navigation */}
        <div className="hidden items-center gap-8 md:flex">
          <a
            href="#about"
            className="text-sm text-astron-muted transition hover:text-white"
          >
            About
          </a>

          <a
            href="#mission"
            className="text-sm text-astron-muted transition hover:text-white"
          >
            Mission
          </a>

          <Link
            to="/explorer"
            className="rounded-lg bg-astron-primary px-5 py-2.5 text-sm font-medium text-white transition hover:bg-astron-accent"
          >
            Launch Explorer
          </Link>
        </div>

        {/* Mobile navigation */}
        <Link
          to="/explorer"
          className="rounded-lg bg-astron-primary px-4 py-2 text-sm font-medium text-white md:hidden"
        >
          Explore
        </Link>
      </nav>
    </header>
  );
}

export default Navbar;
