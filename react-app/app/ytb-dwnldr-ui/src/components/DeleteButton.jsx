// DeleteButton.jsx
import React from "react";


export const StyleDelete = {
    display: "inline-flex",
    alignItems: "center",
    cursor: "pointer",
    padding: "5px",
    borderRadius: "4px",
    transition: "background-color 0.2s",
    width: "fit-content",
    userSelect: "none", // prevent text selection on click-drag
  }
export const DeleteButton = ({ onClick }) => {
  return (
    <div
      id="delete-button"
      style={StyleDelete}
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter') onClick(); }}
      role="button"
      tabIndex={0}
      aria-label="Delete"
    >
      <img src="/delete.svg" alt="Delete" width={25} />
    </div>
  );
};

