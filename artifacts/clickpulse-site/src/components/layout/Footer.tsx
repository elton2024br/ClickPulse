import { Database, Server, Clock, Mouse } from "lucide-react";

export function Footer({ uptime }: { uptime: number }) {
  const formatUptime = (min: number) => {
    const h = Math.floor(min / 60);
    const m = min % 60;
    return `${h}h ${m}m`;
  };

  return (
    <footer className="w-full border-t border-border/40 bg-card/50 backdrop-blur mt-8">
      <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row items-center justify-between py-3 px-4 md:px-8 text-xs text-muted-foreground">
        
        <div className="flex items-center gap-4 mb-3 sm:mb-0">
          <div className="flex items-center gap-1.5 text-success">
            <Server className="w-3.5 h-3.5" />
            <span className="font-medium">App Running</span>
          </div>
          <div className="w-px h-3 bg-border" />
          <div className="flex items-center gap-1.5">
            <Mouse className="w-3.5 h-3.5" />
            <span>Driver Ativo</span>
          </div>
          <div className="w-px h-3 bg-border hidden sm:block" />
          <div className="hidden sm:flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5" />
            <span>SQLite Local (2.4 MB)</span>
          </div>
          <div className="w-px h-3 bg-border hidden sm:block" />
          <div className="hidden sm:flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            <span>Uptime: {formatUptime(uptime)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 opacity-70 hover:opacity-100 transition-opacity">
          <span>Desenvolvido por</span>
          <span className="font-bold text-primary bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
            Elton
          </span>
        </div>
        
      </div>
    </footer>
  );
}
