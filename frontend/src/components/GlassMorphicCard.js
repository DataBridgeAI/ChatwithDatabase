import React from 'react';

const GlassmorphicCard = ({ 
  children, 
  className = '', 
  blur = '10px', 
  background = 'rgba(255, 255, 255, 0.15)', 
  border = '1px solid rgba(255, 255, 255, 0.18)', 
  borderRadius = '16px',
  boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  padding = '30px',
  width = 'auto',
  height = 'auto',
  hoverEffect = true
}) => {
  const baseStyle = {
    backdropFilter: `blur(${blur})`,
    WebkitBackdropFilter: `blur(${blur})`,
    background,
    border,
    borderRadius,
    boxShadow,
    padding,
    width,
    height,
    transition: 'all 0.3s ease'
  };

  return (
    <div 
      className={`glassmorphic-card ${className}`} 
      style={{...baseStyle}}
    >
      {children}
    </div>
  );
};

export default GlassmorphicCard;