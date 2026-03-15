import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { StatCards } from "@/components/dashboard/StatCards";
import { ChartsSection } from "@/components/dashboard/ChartsSection";
import { ActivityTimeline } from "@/components/dashboard/ActivityTimeline";
import { LiveFeed } from "@/components/dashboard/LiveFeed";
import { HistoryTable } from "@/components/dashboard/HistoryTable";
import { useClickPulse } from "@/hooks/use-clickpulse";

export default function Dashboard() {
  const stats = useClickPulse();

  return (
    <div className="min-h-screen flex flex-col bg-background relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[50%] rounded-full bg-info/10 blur-[120px] pointer-events-none" />

      <Header status={stats.status} />

      <main className="flex-1 w-full max-w-[1600px] mx-auto p-4 md:p-8 flex flex-col gap-6 md:gap-8 z-10">
        
        {/* Row 1: Key Stats */}
        <StatCards 
          total={stats.totalClicksToday}
          activeMin={stats.activeTimeMin}
          pauseMin={stats.pauseTimeMin}
          rate={stats.clicksPerHour}
        />

        {/* Row 2: Main Charts */}
        <ChartsSection 
          hourlyData={stats.hourlyData} 
          distribution={stats.clickDistribution} 
        />

        {/* Row 3: Activity Timeline */}
        <ActivityTimeline />

        {/* Row 4: History & Live Feed */}
        <div className="grid gap-6 md:gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <HistoryTable data={stats.weeklyData} />
          </div>
          <div className="h-[400px] lg:h-auto">
            <LiveFeed feed={stats.liveFeed} />
          </div>
        </div>

      </main>

      <Footer uptime={stats.uptimeMin} />
    </div>
  );
}
