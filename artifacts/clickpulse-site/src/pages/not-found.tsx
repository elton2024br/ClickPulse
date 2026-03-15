import { Link } from "wouter";
import { MousePointerClick } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background text-foreground">
      <div className="text-center flex flex-col items-center">
        <div className="w-16 h-16 bg-primary/20 text-primary rounded-2xl flex items-center justify-center mb-6">
          <MousePointerClick className="w-8 h-8" />
        </div>
        <h1 className="text-4xl font-bold font-mono mb-2">404</h1>
        <h2 className="text-xl text-muted-foreground mb-8">Página não encontrada</h2>
        <Link href="/" className="px-6 py-3 rounded-lg font-medium bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-0.5 transition-all shadow-lg shadow-primary/20">
          Voltar ao Dashboard
        </Link>
      </div>
    </div>
  );
}
