import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Cell as PieCell } from "recharts";
import type { HourlyStat, AppStats } from "@/hooks/use-clickpulse";

interface ChartsProps {
  hourlyData: HourlyStat[];
  distribution: AppStats["clickDistribution"];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card/95 border border-border backdrop-blur-md p-3 rounded-lg shadow-xl">
        <p className="text-sm font-medium text-muted-foreground mb-1">{label}</p>
        <p className="text-lg font-bold text-foreground">
          {payload[0].value} <span className="text-sm font-normal text-muted-foreground">cliques</span>
        </p>
      </div>
    );
  }
  return null;
};

export function ChartsSection({ hourlyData, distribution }: ChartsProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className="lg:col-span-2 flex flex-col">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-1.5 h-6 bg-primary rounded-full" />
            Cliques por Hora
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 min-h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={hourlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.5} />
              <XAxis 
                dataKey="hour" 
                axisLine={false}
                tickLine={false}
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                dy={10}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
              />
              <Tooltip cursor={{ fill: 'hsl(var(--muted)/0.4)' }} content={<CustomTooltip />} />
              <Bar 
                dataKey="clicks" 
                radius={[4, 4, 0, 0]}
                animationDuration={1500}
              >
                {hourlyData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.clicks > 200 ? 'hsl(var(--primary))' : 'hsl(var(--primary)/0.5)'} 
                    className="hover:opacity-80 transition-opacity cursor-pointer"
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-1.5 h-6 bg-info rounded-full" />
            Tipos de Clique
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center min-h-[300px]">
          <div className="h-[220px] w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                  animationDuration={1500}
                >
                  {distribution.map((entry, index) => (
                    <PieCell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Center Text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-3xl font-bold font-mono">100%</span>
              <span className="text-xs text-muted-foreground">Total</span>
            </div>
          </div>
          
          <div className="w-full flex justify-center gap-4 mt-2">
            {distribution.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-sm font-medium">{item.name}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
