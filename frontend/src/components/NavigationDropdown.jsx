import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

export default function NavigationDropdown({ items = [], label = "Options", fillUp = false }) {
  const [open, setOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const dropdownRef = useRef(null);
  const timer = useRef();
  const navigate = useNavigate();


  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (open && dropdownRef.current) {
      dropdownRef.current.focus();
    }
  }, [open]);

  useEffect(() => {
    if (open) {
      setHighlightedIndex(0);
    }
  }, [open]);

  return (
    <div
      className="relative focus:outline-none focus:ring-0"
      ref={dropdownRef}
      tabIndex={0}
      onMouseEnter={() => {
        clearTimeout(timer.current);
        setOpen(true);
      }}
      onMouseLeave={() => {
        timer.current = setTimeout(() => setOpen(false), 200);
      }}
      onKeyDown={(e) => {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setHighlightedIndex((prev) => (prev + 1) % items.length);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setHighlightedIndex((prev) => (prev - 1 + items.length) % items.length);
        } else if (e.key === 'Enter') {
          navigate(items[highlightedIndex].path);
          setOpen(false);
        } else if (e.key === 'Escape') {
          setOpen(false);
        }
      }}
    >

      <span
        className="cursor-pointer text-white hover:text-brand font-bold transition"
        onClick={() => {
            if (items.length > 0) {
            navigate(items[0].path);
            setOpen(false);
            }
        }}
        onMouseEnter={() => {
            clearTimeout(timer.current);
            setOpen(true);
        }}
        >
        {label}
      </span>

      {open && (
        <div className="absolute left-1/2 -translate-x-1/2 translate-y-3 mt-2 w-64 bg-black border border-black rounded-xl shadow-lg z-50 max-h-80 overflow-auto">
          <ul className="divide-y divide-gray-700">
            {items.map((weapon, index) => (
              <li key={weapon.label}>
                <Link
                  to={weapon.path}
                  className={`flex items-center gap-3 p-3 cursor-pointer transition ${highlightedIndex === index ? 'bg-gray-700' : 'hover:bg-gray-700'}`}
                  onClick={() => setOpen(false)}
                >
                  <img
                    src={weapon.image}
                    alt={weapon.label}
                    className="w-8 h-8 rounded-md object-contain"
                  />
                  <span>{weapon.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
