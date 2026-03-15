import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { DailyStat } from "@/hooks/use-clickpulse";

export function HistoryTable({ data }: { data: DailyStat[] }) {
  
  const maxClicks = Math.max(...data.map(d => d.total));

  return (
    <div className="flex flex-col gap-4 h-full">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-1.5 h-6 bg-secondary-foreground rounded-full" />
            Historico Semanal
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground bg-muted/50 uppercase border-b border-border">
                <tr>
                  <th className="px-4 py-3 rounded-tl-lg">Dia</th>
                  <th className="px-4 py-3 text-right">Total</th>
                  <th className="px-4 py-3 text-right text-info">Esq.</th>
                  <th className="px-4 py-3 text-right text-destructive">Dir.</th>
                  <th className="px-4 py-3 text-right text-warning">Meio</th>
                  <th className="px-4 py-3 text-right text-success">Ativo (min)</th>
                  <th className="px-4 py-3 text-right rounded-tr-lg">Pausa (min)</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.date} className="border-b border-border/30 hover:bg-muted/30 transition-colors">
                    <td className="px-4 py-3 font-medium text-foreground">{row.date}</td>
                    <td className="px-4 py-3 text-right font-mono font-bold">{row.total.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono text-muted-foreground">{row.left.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono text-muted-foreground">{row.right.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono text-muted-foreground">{row.middle.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono text-success/90">{row.activeMin}</td>
                    <td className="px-4 py-3 text-right font-mono text-destructive/90">{row.pauseMin}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-1.5 h-6 bg-primary rounded-full" />
            Comparativo Diario
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <XAxis 
                  dataKey="date" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                  dy={10}
                />
                <Tooltip 
                  cursor={{ fill: 'hsl(var(--muted)/0.4)' }}
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px', color: 'white' }}
                  formatter={(value: number) => [`${value} cliques`, 'Total']}
                  labelStyle={{ color: 'hsl(var(--muted-foreground))', marginBottom: '4px' }}
                />
                <Bar 
                  dataKey="total" 
                  radius={[4, 4, 0, 0]}
                  animationDuration={1500}
                >
                  {data.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.total === maxClicks ? 'hsl(var(--primary))' : 'hsl(var(--primary)/0.4)'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
