import React from "react";

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        maxWidth: "960px",
        margin: "0 auto",
        padding: "16px",
        backgroundColor: "#f5f5f5",
        borderRadius: "12px",
      }}
    >
      {children}
    </div>
  );
}

export default Layout;
