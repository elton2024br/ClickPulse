import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ActivityTimeline() {
  // Generate a mock timeline representing a 24h period 
  // with random active (green) and pause (red) chunks
  const segments = Array.from({ length: 48 }).map((_, i) => {
    // Mostly active during day (16 to 36 = 8am to 6pm)
    const isDayTime = i >= 16 && i <= 36;
    let isActive = false;
    
    if (isDayTime) {
      // 80% active during day
      isActive = Math.random() > 0.2;
    } else {
      // 10% active at night
      isActive = Math.random() > 0.9;
    }
    
    return isActive;
  });

  return (
    <Card>
      <CardHeader className="pb-3">
         <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-1.5 h-6 bg-success rounded-full" />
            Timeline de Atividade
          </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="w-full h-10 rounded-lg overflow-hidden flex bg-muted/50 border border-border/50">
          {segments.map((isActive, i) => (
            <div 
              key={i} 
              className={`h-full flex-1 border-r border-background/20 last:border-0 hover:brightness-125 transition-all ${
                isActive ? 'bg-success/80' : 'bg-destructive/80'
              }`}
              title={`${Math.floor(i/2).toString().padStart(2, '0')}:${i%2===0?'00':'30'} - ${isActive ? 'Ativo' : 'Pausa'}`}
            />
          ))}
        </div>
        <div className="flex justify-between mt-2 text-xs text-muted-foreground font-mono">
          <span>00:00</span>
          <span>06:00</span>
          <span>12:00</span>
          <span>18:00</span>
          <span>23:59</span>
        </div>
        
        <div className="flex gap-4 mt-4 text-sm justify-center sm:justify-start">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm bg-success/80" />
            <span className="text-muted-foreground">Período Ativo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm bg-destructive/80" />
            <span className="text-muted-foreground">Pausa Detectada</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
