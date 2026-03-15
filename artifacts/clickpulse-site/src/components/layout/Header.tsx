import { useEffect, useState } from "react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Activity, MousePointer2 } from "lucide-react";
import { cn } from "@/lib/utils";

export function Header({ status }: { status: "active" | "pause" }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/60 backdrop-blur-xl">
      <div className="flex h-16 items-center px-4 md:px-8 max-w-[1600px] mx-auto w-full justify-between">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center h-10 w-10 rounded-xl bg-primary/10 border border-primary/20">
            <MousePointer2 className="h-5 w-5 text-primary" />
            {/* Pulse effect */}
            {status === "active" && (
              <span className="absolute top-0 right-0 flex h-3 w-3 -mt-1 -mr-1">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-success"></span>
              </span>
            )}
          </div>
          <div>
            <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
              ClickPulse Command Center
            </h1>
            <p className="text-xs text-muted-foreground flex items-center gap-1.5">
              <span className={cn(
                "inline-block w-1.5 h-1.5 rounded-full",
                status === "active" ? "bg-success" : "bg-destructive"
              )} />
              Monitoramento {status === "active" ? "Ativo" : "Pausado"}
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-6">
          <div className="flex flex-col items-end">
            <span className="text-sm font-medium text-foreground">
              {format(time, "HH:mm:ss")}
            </span>
            <span className="text-xs text-muted-foreground capitalize">
              {format(time, "EEEE, d 'de' MMMM", { locale: ptBR })}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
