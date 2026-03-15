import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import type { LiveClick } from "@/hooks/use-clickpulse";

export function LiveFeed({ feed }: { feed: LiveClick[] }) {
  
  const getTypeColor = (type: string) => {
    switch(type) {
      case 'left': return 'text-info bg-info/10 border-info/20';
      case 'right': return 'text-destructive bg-destructive/10 border-destructive/20';
      case 'middle': return 'text-warning bg-warning/10 border-warning/20';
      default: return 'text-primary bg-primary/10 border-primary/20';
    }
  };

  const getTypeLabel = (type: string) => {
    switch(type) {
      case 'left': return 'Botão Esquerdo';
      case 'right': return 'Botão Direito';
      case 'middle': return 'Botão do Meio';
      default: return 'Clique';
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 border-b border-border/50">
        <CardTitle className="text-lg flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            Live Feed
          </div>
          <span className="text-xs font-normal text-muted-foreground px-2 py-1 bg-muted rounded-md">
            Últimos 50
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 flex-1 overflow-hidden relative">
        <div className="absolute inset-0 overflow-y-auto p-4 custom-scrollbar">
          <div className="space-y-2">
            <AnimatePresence initial={false}>
              {feed.map((click) => (
                <motion.div
                  key={click.id}
                  initial={{ opacity: 0, height: 0, scale: 0.9, y: -20 }}
                  animate={{ opacity: 1, height: "auto", scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card/40 hover:bg-card/80 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded border ${getTypeColor(click.type)}`}>
                      {getTypeLabel(click.type)}
                    </span>
                    <span className="text-xs font-mono text-muted-foreground">
                      X:{click.x.toString().padStart(4, ' ')} Y:{click.y.toString().padStart(4, ' ')}
                    </span>
                  </div>
                  <span className="text-xs font-mono text-muted-foreground opacity-70">
                    {format(click.timestamp, "HH:mm:ss.SSS")}
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {feed.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground/50 py-10">
                <span className="text-sm">Aguardando atividade do mouse...</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
