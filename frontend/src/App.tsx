import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  Search, 
  Clock, 
  Zap, 
  CheckCircle2, 
  XCircle,
  Package, 
  Eye, 
  Settings, 
  Sparkles,
  LayoutDashboard,
  Cpu,
  BarChart3,
  RefreshCw,
  Plus,
  Loader2,
  Video,
  ExternalLink,
  Globe
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "./components/Card.tsx";
import { Badge } from "./components/Badge.tsx";
import { Button } from "./components/Button.tsx";
import { ScrollArea } from "./components/ScrollArea.tsx";
import { cn } from "./lib/utils.ts";
import { initializeApp } from "firebase/app";
import { getFirestore, collection, onSnapshot, doc, query, where, orderBy, updateDoc, deleteDoc } from "firebase/firestore";
// @ts-ignore
import firebaseConfig from "../../server/firebase-applet-config.json";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export default function App() {
  const [activeTab, setActiveTab] = useState("mining");
  
  // States for Data
  const [miningItems, setMiningItems] = useState<any[]>([]);
  const [vitrineItems, setVitrineItems] = useState<any[]>([]);
  const [scheduledPosts, setScheduledPosts] = useState<any[]>([]);
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [engineStatus, setEngineStatus] = useState<any>(null);
  const [processingTasks, setProcessingTasks] = useState<any[]>([]);
  
  // States for Tools
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [updatingVitrine, setUpdatingVitrine] = useState(false);

  // Real-time Listeners
  useEffect(() => {
    const qMining = query(collection(db, "mining"), where("status", "==", "pending"), orderBy("timestamp", "desc"));
    const unsubMining = onSnapshot(qMining, (snap: any) => {
      setMiningItems(snap.docs.map((d: any) => ({ id: d.id, ...d.data() })));
    });

    const qVitrine = query(collection(db, "mining"), where("status", "==", "approved"), orderBy("timestamp", "desc"));
    const unsubVitrine = onSnapshot(qVitrine, (snap: any) => {
      setVitrineItems(snap.docs.map((d: any) => ({ id: d.id, ...d.data() })));
    });

    const qSchedule = query(collection(db, "schedule"), orderBy("postTime", "asc"));
    const unsubSchedule = onSnapshot(qSchedule, (snap: any) => {
      setScheduledPosts(snap.docs.map((d: any) => ({ id: d.id, ...d.data() })));
    });

    const unsubAnalytics = onSnapshot(doc(db, "analytics", "global"), (snap: any) => {
      if (snap.exists()) setAnalyticsData(snap.data());
    });

    const unsubStatus = onSnapshot(doc(db, "status", "engine"), (snap: any) => {
      if (snap.exists()) setEngineStatus(snap.data());
    });

    const qProcessing = query(collection(db, "processing"), where("status", "==", "processing"));
    const unsubProcessing = onSnapshot(qProcessing, (snap: any) => {
       setProcessingTasks(snap.docs.map((d: any) => ({ id: d.id, ...d.data() })));
    });

    return () => {
      unsubMining(); unsubVitrine(); unsubSchedule(); unsubAnalytics(); unsubStatus(); unsubProcessing();
    };
  }, []);

  const handleApprove = async (item: any) => {
    try {
      await updateDoc(doc(db, "mining", item.id), { status: "approved" });
    } catch (e) {
      console.error("Approval error:", e);
    }
  };

  const handleIAEdit = async (item: any) => {
    try {
      await fetch("/api/process/video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          videoPath: item.path || item.image,
          productName: item.title,
          productDesc: item.title,
          price: item.price,
          productId: item.id.substring(0, 8)
        })
      });
    } catch (e) {
      console.error("IA Edit error:", e);
    }
  };

  const handleUpdateVitrine = async () => {
    setUpdatingVitrine(true);
    try {
      await fetch("/api/vitrine/update", { method: "POST" });
      setTimeout(() => setUpdatingVitrine(false), 3000);
    } catch (e) {
      console.error("Vitrine update error:", e);
      setUpdatingVitrine(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery) return;
    setSearching(true);
    setSearchResults([]);
    try {
      const response = await fetch("/api/scrape/shopee", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: searchQuery })
      });
      const result = await response.json();
      if (result.success && result.data) {
        setSearchResults([{ id: result.id || Math.random().toString(), ...result.data }]);
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setSearching(false);
    }
  };

  const motors = [
    { name: "Shopee Trends Scraper", status: engineStatus?.shopee?.status || "OFFLINE", desc: "Monitorando 'Mais Vendidos'", color: engineStatus?.shopee?.status === "ATIVO" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400" },
    { name: "Social Media Crawler", status: engineStatus?.social?.status || "OFFLINE", desc: "Capturando Reels/TikTok", color: engineStatus?.social?.status === "ATIVO" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400" },
    { name: "Automation Engine", status: engineStatus?.main?.status || "OFFLINE", desc: "Orquestrador Principal", color: engineStatus?.main?.status === "ATIVO" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400" },
    { name: "Price Monitor", status: engineStatus?.price?.status || "OFFLINE", desc: "Validando estoque Shopee", color: engineStatus?.price?.status === "SINC" ? "bg-blue-500/20 text-blue-400" : "bg-amber-500/20 text-amber-400" },
  ];

  return (
    <div className="flex h-screen w-full bg-[#0D0F14] text-[#E8EAF0] overflow-hidden font-inter">
      <aside className="w-64 border-r border-white/5 bg-[#0f1117] flex flex-col shrink-0">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-orange-600 flex items-center justify-center shadow-lg shadow-orange-600/20">
            <Cpu className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">SIAA <span className="text-orange-500">2026</span></h1>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Cérebro Digital</p>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          {[
            { id: "mining", label: "Mineração", icon: LayoutDashboard },
            { id: "triagem", label: "Triagem", icon: Eye, count: miningItems.length },
            { id: "vitrine", label: "Minha Vitrine", icon: Package },
            { id: "studio", label: "IA Studio", icon: Sparkles },
            { id: "analytics", label: "Analytics", icon: BarChart3 },
            { id: "settings", label: "Configurações", icon: Settings },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                "w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200",
                activeTab === item.id ? "bg-orange-600/10 text-orange-500 border border-orange-500/20" : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              )}
            >
              <div className="flex items-center gap-3">
                <item.icon className={cn("w-5 h-5", activeTab === item.id ? "text-orange-500" : "text-slate-400")} />
                <span className="font-semibold text-sm">{item.label}</span>
              </div>
              {item.count ? <Badge className="bg-orange-600 text-white">{item.count}</Badge> : null}
            </button>
          ))}
        </nav>
      </aside>

      <main className="flex-1 flex flex-col relative overflow-hidden bg-grid-white/[0.02]">
        <header className="h-16 border-b border-white/5 bg-[#0D0F14]/80 backdrop-blur-xl flex items-center justify-between px-8 z-10 sticky top-0">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="rounded-full bg-orange-600/10 text-orange-500 border-orange-500/20">LIVE</Badge>
            <span className="text-xs text-slate-500 font-medium">Pipeline: Ativo</span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input 
                placeholder="URL Shopee..." 
                className="bg-white/5 border border-white/10 rounded-full pl-10 pr-4 py-1.5 text-xs w-64 focus:outline-none"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
            </div>
            <Button size="sm" variant="outline" className="rounded-full h-8 px-4 border-white/10">
              <Plus className="w-4 h-4 mr-2" /> Novo Post
            </Button>
          </div>
        </header>

        <ScrollArea className="flex-1 p-8">
          <div className="max-w-6xl mx-auto space-y-8">
            {/* PROCESSING TASKS */}
            {processingTasks.length > 0 && (
              <div className="space-y-3">
                {processingTasks.map((task) => (
                  <div key={task.id} className="p-4 bg-blue-600/10 border border-blue-500/20 rounded-2xl flex items-center gap-4">
                    <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-1">
                        <p className="text-xs font-bold text-blue-400">{task.step}</p>
                        <p className="text-[10px] font-mono text-blue-500">{task.progress}%</p>
                      </div>
                      <div className="w-full bg-blue-900/30 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-full transition-all duration-500" style={{ width: `${task.progress}%` }} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {searching && (
              <div className="flex items-center gap-3 p-4 bg-orange-600/10 border border-orange-500/20 rounded-2xl animate-pulse">
                <RefreshCw className="w-5 h-5 text-orange-500 animate-spin" />
                <p className="text-sm font-bold text-orange-500">Minerando dados da Shopee... Aguarde.</p>
              </div>
            )}

            {searchResults.map((item, i) => (
              <Card key={i} className="bg-white/5 border-white/10 overflow-hidden flex items-center p-4 gap-4 animate-in fade-in slide-in-from-top-4">
                <img src={item.image_url || item.path} className="w-16 h-16 rounded-xl object-cover" alt="" />
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-bold truncate">{item.titulo}</h4>
                  <p className="text-xs text-orange-500 font-bold">{item.preco}</p>
                </div>
                <Button size="sm" onClick={() => handleApprove(item)}>Aprovar</Button>
              </Card>
            ))}

            {activeTab === "mining" && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {[
                    { label: "Postagens Agendadas", val: scheduledPosts.length.toString(), icon: Clock, color: "text-blue-500" },
                    { label: "Pendentes Triagem", val: miningItems.length.toString(), icon: TrendingUp, color: "text-orange-500" },
                    { label: "Taxa de Conversão", val: analyticsData?.conversions ? ((analyticsData.conversions / (analyticsData.clicks || 1)) * 100).toFixed(1) + "%" : "0%", icon: Zap, color: "text-emerald-500" },
                    { label: "Cliques de Afiliado", val: analyticsData?.clicks?.toLocaleString() || "0", icon: Search, color: "text-purple-500" },
                  ].map((stat, i) => (
                    <Card key={i} className="bg-white/5 border-white/10">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-xs font-medium text-slate-400 mb-1">{stat.label}</p>
                            <h3 className="text-2xl font-bold tracking-tight">{stat.val}</h3>
                          </div>
                          <div className={cn("p-2 rounded-lg bg-white/5", stat.color)}>
                            <stat.icon className="w-5 h-5" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                   <Card className="lg:col-span-2 bg-white/5 border-white/10">
                    <CardHeader>
                      <CardTitle className="text-sm font-bold uppercase tracking-widest text-slate-500">Últimos Minerados</CardTitle>
                    </CardHeader>
                    <div className="divide-y divide-white/5">
                      {miningItems.length > 0 ? miningItems.slice(0, 5).map((item, i) => (
                        <div key={i} className="p-4 flex items-center gap-4 hover:bg-white/5 transition-colors">
                          <img src={item.image} className="w-12 h-12 rounded-lg object-cover" alt="" />
                          <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-bold truncate">{item.title}</h4>
                            <p className="text-xs text-slate-500">{item.price} · {item.source}</p>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="ghost" className="text-blue-500 hover:bg-blue-500/10" onClick={() => handleIAEdit(item)}>
                              <Video className="w-4 h-4" />
                            </Button>
                            <Button size="sm" variant="ghost" className="text-emerald-500 hover:bg-emerald-500/10" onClick={() => handleApprove(item)}>
                              <CheckCircle2 className="w-5 h-5" />
                            </Button>
                          </div>
                        </div>
                      )) : <div className="p-12 text-center text-slate-500 text-sm">Nada pendente.</div>}
                    </div>
                  </Card>

                  <Card className="bg-white/5 border-white/10">
                    <CardHeader>
                      <CardTitle className="text-sm font-bold uppercase tracking-widest text-slate-500">Motores</CardTitle>
                    </CardHeader>
                    <div className="divide-y divide-white/5">
                      {motors.map((m, i) => (
                        <div key={i} className="p-5 flex items-center justify-between">
                          <div className="flex flex-col">
                            <span className="text-sm font-bold">{m.name}</span>
                            <span className="text-[10px] text-slate-500">{m.desc}</span>
                          </div>
                          <Badge className={cn("rounded-full text-[9px] font-bold uppercase", m.color)}>{m.status}</Badge>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
              </div>
            )}

            {activeTab === "triagem" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold">Triagem</h2>
                  <Badge variant="outline" className="text-orange-500">{miningItems.length} pendentes</Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {miningItems.map((item, i) => (
                    <Card key={i} className="bg-white/5 border-white/10 group overflow-hidden">
                      <div className="relative aspect-square">
                         <img src={item.image} className="w-full h-full object-cover group-hover:scale-105 transition-transform" alt="" />
                         <div className="absolute top-2 right-2 flex gap-2">
                            <Badge className="bg-black/40">{item.source}</Badge>
                         </div>
                      </div>
                      <CardContent className="p-4 space-y-3">
                        <h3 className="font-bold text-sm line-clamp-1">{item.title}</h3>
                        <p className="text-lg font-black text-orange-500">{item.price}</p>
                        <div className="flex flex-col gap-2">
                           <Button className="w-full" onClick={() => handleApprove(item)}>Aprovar</Button>
                           <div className="flex gap-2">
                              <Button variant="outline" className="flex-1 text-blue-500" onClick={() => handleIAEdit(item)}>
                                 <Sparkles className="w-4 h-4 mr-2" /> IA Edit
                              </Button>
                              <Button variant="outline" onClick={async () => await deleteDoc(doc(db, "mining", item.id))}><XCircle className="w-4 h-4" /></Button>
                           </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {activeTab === "vitrine" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-6 bg-orange-600/10 border border-orange-500/20 rounded-2xl">
                  <div>
                    <h2 className="text-2xl font-bold">Vitrine GitHub Pages</h2>
                    <p className="text-sm text-slate-400">Sincronize seus produtos aprovados com o Linktree público.</p>
                  </div>
                  <div className="flex gap-3">
                    <Button variant="outline" className="rounded-xl border-white/10" onClick={() => window.open("https://barbaravsilva.github.io/VitrineSIAA", "_blank")}>
                      <Globe className="w-4 h-4 mr-2" /> Ver Vitrine
                    </Button>
                    <Button className="rounded-xl bg-orange-600 hover:bg-orange-700" onClick={handleUpdateVitrine} disabled={updatingVitrine}>
                      {updatingVitrine ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
                      Atualizar Agora
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {vitrineItems.map((item, i) => (
                    <Card key={i} className="bg-white/5 border-white/10 overflow-hidden flex flex-col">
                       <img src={item.image} className="aspect-video object-cover" alt="" />
                       <div className="p-3 space-y-2">
                          <p className="text-xs font-bold truncate">{item.title}</p>
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-orange-500 font-bold">{item.price}</span>
                            <ExternalLink className="w-3 h-3 text-slate-500" />
                          </div>
                       </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </main>
    </div>
  );
}
