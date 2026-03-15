import { useState, useEffect } from "react";

// Types
export type ClickType = "left" | "right" | "middle";

export interface LiveClick {
  id: string;
  timestamp: Date;
  type: ClickType;
  x: number;
  y: number;
}

export interface HourlyStat {
  hour: string;
  clicks: number;
}

export interface DailyStat {
  date: string;
  total: number;
  left: number;
  right: number;
  middle: number;
  activeMin: number;
  pauseMin: number;
}

export interface AppStats {
  totalClicksToday: number;
  activeTimeMin: number;
  pauseTimeMin: number;
  clicksPerHour: number;
  clickDistribution: { name: string; value: number; color: string }[];
  hourlyData: HourlyStat[];
  weeklyData: DailyStat[];
  liveFeed: LiveClick[];
  status: "active" | "pause";
  uptimeMin: number;
}

// Initial Mock Data
const INITIAL_WEEKLY_DATA: DailyStat[] = [
  { date: "Seg", total: 1102, left: 750, right: 300, middle: 52, activeMin: 245, pauseMin: 60 },
  { date: "Ter", total: 1450, left: 900, right: 450, middle: 100, activeMin: 310, pauseMin: 45 },
  { date: "Qua", total: 890, left: 600, right: 250, middle: 40, activeMin: 180, pauseMin: 120 },
  { date: "Qui", total: 1670, left: 1100, right: 480, middle: 90, activeMin: 360, pauseMin: 30 },
  { date: "Sex", total: 1340, left: 850, right: 400, middle: 90, activeMin: 290, pauseMin: 50 },
  { date: "Sáb", total: 450, left: 300, right: 120, middle: 30, activeMin: 90, pauseMin: 200 },
  { date: "Dom", total: 1247, left: 810, right: 349, middle: 88, activeMin: 272, pauseMin: 75 },
];

const INITIAL_HOURLY_DATA: HourlyStat[] = Array.from({ length: 24 }).map((_, i) => {
  // Create a realistic bell curve for a workday
  const isWorkHour = i >= 9 && i <= 18;
  const isLunch = i === 12 || i === 13;
  let baseClicks = 0;
  
  if (isWorkHour) {
    baseClicks = isLunch ? 40 : 150 + Math.random() * 100;
  } else if (i > 18 && i < 23) {
    baseClicks = Math.random() * 50; // Evening casual usage
  }

  return {
    hour: `${i.toString().padStart(2, '0')}h`,
    clicks: Math.floor(baseClicks),
  };
});

export function useClickPulse() {
  const [stats, setStats] = useState<AppStats>({
    totalClicksToday: 1247,
    activeTimeMin: 272, // 4h 32m
    pauseTimeMin: 75,   // 1h 15m
    clicksPerHour: 275,
    clickDistribution: [
      { name: "Esquerdo", value: 65, color: "hsl(var(--info))" },
      { name: "Direito", value: 28, color: "hsl(var(--destructive))" },
      { name: "Meio", value: 7, color: "hsl(var(--warning))" },
    ],
    hourlyData: INITIAL_HOURLY_DATA,
    weeklyData: INITIAL_WEEKLY_DATA,
    liveFeed: [],
    status: "active",
    uptimeMin: 342,
  });

  // Simulate real-time activity
  useEffect(() => {
    const interval = setInterval(() => {
      // 70% chance to simulate a click every second
      if (Math.random() > 0.3) {
        const rand = Math.random();
        let type: ClickType = "left";
        if (rand > 0.9) type = "middle";
        else if (rand > 0.65) type = "right";

        const newClick: LiveClick = {
          id: Math.random().toString(36).substring(7),
          timestamp: new Date(),
          type,
          x: Math.floor(Math.random() * 1920),
          y: Math.floor(Math.random() * 1080),
        };

        setStats(prev => {
          // Keep last 50 clicks in feed
          const newFeed = [newClick, ...prev.liveFeed].slice(0, 50);
          
          return {
            ...prev,
            totalClicksToday: prev.totalClicksToday + 1,
            liveFeed: newFeed,
            status: "active",
          };
        });
      } else {
        // Occasional simulated pause logic (just visual flip)
        if (Math.random() > 0.95) {
           setStats(prev => ({ ...prev, status: prev.status === "active" ? "pause" : "active" }));
        }
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return stats;
}
