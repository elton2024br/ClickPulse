import { MousePointerClick, Timer, PauseCircle, Activity } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";

interface StatCardsProps {
  total: number;
  activeMin: number;
  pauseMin: number;
  rate: number;
}

function formatMinToHours(minutes: number) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h ${m}m`;
}

export function StatCards({ total, activeMin, pauseMin, rate }: StatCardsProps) {
  const stats = [
    {
      title: "Cliques Hoje",
      value: total.toLocaleString(),
      icon: MousePointerClick,
      color: "text-primary",
      bg: "bg-primary/10",
      border: "border-primary/20",
    },
    {
      title: "Tempo Ativo",
      value: formatMinToHours(activeMin),
      icon: Timer,
      color: "text-success",
      bg: "bg-success/10",
      border: "border-success/20",
    },
    {
      title: "Pausas",
      value: formatMinToHours(pauseMin),
      icon: PauseCircle,
      color: "text-destructive",
      bg: "bg-destructive/10",
      border: "border-destructive/20",
    },
    {
      title: "Cliques / Hora",
      value: rate.toLocaleString(),
      icon: Activity,
      color: "text-info",
      bg: "bg-info/10",
      border: "border-info/20",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, i) => (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1, duration: 0.4, ease: "easeOut" }}
        >
          <Card className="hover:shadow-xl hover:border-border transition-all duration-300 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between space-y-0 pb-2">
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </p>
                <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${stat.bg} ${stat.border} border group-hover:scale-110 transition-transform duration-300`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <h2 className="text-3xl font-bold tracking-tight text-foreground font-mono">
                  {stat.value}
                </h2>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
