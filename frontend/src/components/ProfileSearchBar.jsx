import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

function ProfileSearchBar({ recents = [] }) {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";

  const [search, setSearch] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const navigate = useNavigate();
  const dropdownRef = useRef(null);

  const suggestions = recents.filter((r) =>
    r.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = () => {
    if (suggestions.length > 0) {
      const lastHashIndex = suggestions[highlightedIndex].lastIndexOf("#");
      let gameName, tagLine;
      gameName = suggestions[highlightedIndex].slice(0, lastHashIndex);
      tagLine = suggestions[highlightedIndex].slice(lastHashIndex + 1);
      navigate(`/playerprofile/${gameName}_${tagLine}`);
    } else {
      const lastHashIndex = search.lastIndexOf("#");
      let gameName, tagLine;
      gameName = search.slice(0, lastHashIndex);
      tagLine = search.slice(lastHashIndex + 1);
      navigate(`/playerprofile/${gameName}_${tagLine}`);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative w-96" ref={dropdownRef}>
      {/* Search bar */}
      <input
        type="text"
        value={search}
        onFocus={() => setIsOpen(true)}
        onChange={(e) => setSearch(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "ArrowDown") {
            e.preventDefault();
            setHighlightedIndex((prev) => Math.min(prev + 1, suggestions.length - 1));
          } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setHighlightedIndex((prev) => Math.max(prev - 1, 0));
          } else if (e.key === "Enter") {
            handleSearch();
          } else if (e.key === "Escape") {
            setIsOpen(false);
          }
        }}
        placeholder="Search profiles like: Name#EUW"
        className="w-full p-3 rounded-xl bg-element border border-element-lighter text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white"
      />

      {/* Suggestions Dropdown */}
      {isOpen && (
        <ul className="absolute w-full bg-element-dark border border-element-lighter rounded-xl mt-2 shadow-lg max-h-60 overflow-y-auto z-50">
          {suggestions.length > 0 ? (
            suggestions.map((item, index) => (
              <li
                key={index}
                className={`p-3 cursor-pointer ${index === highlightedIndex ? "bg-element-light text-brand" : "hover:bg-element-light"}`}
                onClick={() => {
                  const lastHashIndex = item.lastIndexOf("#");
                  let gameName, tagLine;
                  gameName = item.slice(0, lastHashIndex);
                  tagLine = item.slice(lastHashIndex + 1);
                  navigate(`/playerprofile/${gameName}_${tagLine}`);
                  setSearch(item);
                  setIsOpen(false);
                }}
              >
                {item}
              </li>
            ))
          ) : (
            <li className="p-3 text-gray-400 text-center">No matches</li>
          )}
        </ul>
      )}
    </div>
  );
}

export default ProfileSearchBar;
