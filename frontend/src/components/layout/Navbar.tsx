import { NavLink } from "react-router-dom";
import SpiderEmblem from "../common/SpiderEmblem";

const links = [
  { to: "/", label: "Analyze" },
  { to: "/community", label: "Community" },
  { to: "/campaigns", label: "Intelligence" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-navy-border bg-void/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <NavLink to="/" className="flex items-center gap-2.5">
          <SpiderEmblem className="h-6 w-6 text-spider-red" />
          <span className="font-display text-lg tracking-tight">Spider-Sense AI</span>
        </NavLink>

        <nav className="flex items-center gap-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `rounded-md px-3.5 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "text-ink-primary border-b-2 border-spider-red"
                    : "text-ink-muted hover:text-ink-primary"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
