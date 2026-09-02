import React from "react";

interface PageBackgroundProps {
  image: string;
  children: React.ReactNode;
}

export default function PageBackground({
  image,
  children,
}: PageBackgroundProps) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#080a0f]">
      <div
        className="pointer-events-none fixed inset-0 z-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url(${image})`,
          opacity: 0.20,
        }}
      />

      <div className="pointer-events-none fixed inset-0 z-0 bg-black/0" />

      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}