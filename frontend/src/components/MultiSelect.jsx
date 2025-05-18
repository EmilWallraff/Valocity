import { useState, useEffect, useRef } from "react";
import { Check, ChevronDown } from "lucide-react";

function MultiSelect({ items = [], label = "Select Items", fillUp = false, defaultSelected = [], onChange }) {
  const [selected, setSelected] = useState(defaultSelected);
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
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
    onChange && onChange(selected);
  }, [selected]);

  const toggleItem = (itemLabel) => {
    setSelected(prev =>
      prev.includes(itemLabel)
        ? prev.filter(label => label !== itemLabel)
        : [...prev, itemLabel]
    );
  };

  const selectAll = () => {
    setSelected(items.map(item => item.label));
  };

  const deselectAll = () => {
    setSelected([]);
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(prev => !prev)}
        className="text-white border border-element-lighter px-4 py-2 rounded-md bg-element hover:bg-element-light flex items-center gap-2"
      >
        {label}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-2 w-64 bg-gray-900 border border-gray-700 rounded-xl shadow-lg max-h-80 overflow-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full p-2 bg-gray-800 text-white placeholder-gray-400 border-b border-gray-700"
          />

          <div className="flex justify-between text-sm text-brand px-3 py-2 border-b border-gray-700">
            <button onClick={selectAll} className="hover:underline">All</button>
            <button onClick={deselectAll} className="hover:underline">None</button>
          </div>

          <ul className="divide-y divide-gray-700">
            {filteredItems.length > 0 ? (
              filteredItems.map((item, index) => (
                <li
                  key={index}
                  className="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-gray-700"
                  onClick={() => toggleItem(item.label)}
                >
                  <div className="relative w-8 h-8 flex-shrink-0">
                    <img src={item.image} alt={item.label} className="rounded-md object-contain max-w-full max-h-full" />
                  </div>
                  <span className="flex-grow">{item.label}</span>
                  {selected.includes(item.label) && <Check className="w-4 h-4 text-brand" />}
                </li>
              ))
            ) : (
              <li className="p-3 text-gray-400 text-center">No matches</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default MultiSelect;