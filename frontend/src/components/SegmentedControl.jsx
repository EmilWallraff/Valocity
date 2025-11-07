import React, { useState } from "react";

function SegmentedControl({ items = [], defaultSelected, onChange }) {
  const [selected, setSelected] = useState(defaultSelected ?? items[0]);

  const handleSelect = (item) => {
    setSelected(item);
    if (onChange) onChange(item);
  };

  return (
    <div className="inline-flex bg-element border border-element-lighter rounded-xl overflow-hidden">
      {items.map((item) => (
        <button
          key={item}
          onClick={() => handleSelect(item)}
          className={`px-4 py-2 transition-all duration-200 ${selected === item
            ? "bg-element-lighter shadow-md"
            : "bg-element hover:bg-element-light"
          }`}
        >
          {item}
        </button>
      ))}
    </div>
  );
}

export default SegmentedControl;

