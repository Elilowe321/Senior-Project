import React from 'react';

const ProgressCircle = ({ size, progress, strokeWidth, circleColor = "#d9edfe" }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;
  
  const progressColor = progress > 75 ? 'url(#greenGradient)' : 'url(#redYellowGradient)';

  return (
    <svg width={size} height={size}>
      <defs>
        <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: "#00ff00", stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: "#006400", stopOpacity: 1 }} />
        </linearGradient>
        <linearGradient id="redYellowGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: "#ff0000", stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: "#ffff00", stopOpacity: 1 }} />
        </linearGradient>
      </defs>
      <circle
        stroke={circleColor}
        fill="transparent"
        strokeWidth={strokeWidth}
        r={radius}
        cx={size / 2}
        cy={size / 2}
      />
      <circle
        stroke={progressColor}
        fill="transparent"
        strokeWidth={strokeWidth}
        r={radius}
        cx={size / 2}
        cy={size / 2}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.35s' }}
      />
      <text
        x="50%"
        y="50%"
        dominantBaseline="middle"
        textAnchor="middle"
        fontSize={size * 0.2}
        fill="#c5f1ff"
      >
        {`${progress}%`}
      </text>
    </svg>
  );
};

export default ProgressCircle;
