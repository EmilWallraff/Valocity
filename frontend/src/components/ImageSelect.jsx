import { useState, useRef, useEffect } from "react";

function ImageSelect({ items = [], sizeClass = "w-16 h-16", defaultLabel }) {
  const [selected, setSelected] = useState(() => items.find(item => item.label === defaultLabel) || items[0]);
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);

  const filteredItems = items.filter(item =>
    item.label.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = e => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    setHighlightedIndex(0);
  }, [search, isOpen]);
  

  return (
    <div className="relative w-64" ref={dropdownRef}>
      {/* Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`bg-gray-800 border border-gray-600 rounded-xl flex items-center justify-center hover:bg-gray-700 ${sizeClass}`}
      >
        <div className="w-3/4 h-3/4 flex items-center justify-center">
            <img src={selected.image} alt={selected.label} className={"rounded-md max-w-full max-h-full object-contain"} />
        </div>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 w-full bg-gray-900 border border-gray-700 rounded-xl shadow-lg z-50 max-h-80 overflow-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
          <input
            type="text"
            placeholder="Search..."
            className="w-full p-2 bg-gray-800 text-white placeholder-gray-400 border-b border-gray-700"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => {
                if (e.key === "ArrowDown") {
                e.preventDefault();
                setHighlightedIndex((prev) => Math.min(prev + 1, filteredItems.length - 1));
                } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setHighlightedIndex((prev) => Math.max(prev - 1, 0));
                } else if (e.key === "Enter") {
                if (filteredItems[highlightedIndex]) {
                    setSelected(filteredItems[highlightedIndex]);
                    setIsOpen(false);
                    setSearch("");
                }
                } else if (e.key === "Escape") {
                setIsOpen(false);
                }
            }}
            autoFocus
          />

          <ul className="divide-y divide-gray-700">
            {filteredItems.map((item, index) => (
              <li
                key={index}
                className={`flex items-center gap-3 p-3 cursor-pointer ${index === highlightedIndex ? "bg-gray-700" : "hover:bg-gray-700"}`}
                onClick={() => {
                  setSelected(item);
                  setIsOpen(false);
                  setSearch("");
                }}
              >
                <div className="w-8 h-8 flex items-center justify-center">
                    <img src={item.image} alt={item.label} className={"rounded-md max-w-full max-h-full object-contain"}/>
                </div>
                <span>{item.label}</span>
              </li>
            ))}
            {filteredItems.length === 0 && (
              <li className="p-3 text-gray-400 text-center">No matches</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ImageSelect;
 