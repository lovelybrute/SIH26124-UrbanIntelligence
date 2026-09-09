import React,{useEffect,useMemo,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Activity,Bus,MapPin,ShieldAlert,Waves,Gauge,HeartPulse,Route} from 'lucide-react';
import './styles.css';

const API=import.meta.env.VITE_API_URL||'http://127.0.0.1:8000';

function Stat({icon:Icon,label,value,suffix=''}){return <div className="card"><Icon size={22}/><div><span>{label}</span><strong>{value}{suffix}</strong></div></div>}

function App(){
  const [stats,setStats]=useState({total_events:0,persisted_events:0,correlated_issues:0,active_bus_ids:[],by_type:{}});
  const [issues,setIssues]=useState([]);
  const [health,setHealth]=useState({road_health_score:100,congestion_index:0,safety_risk_score:0,priority_issues:[]});
  const [online,setOnline]=useState(false);

  useEffect(()=>{
    const load=async()=>{
      try{
        const [s,i,h]=await Promise.all([
          fetch(`${API}/api/v1/stats`),
          fetch(`${API}/api/v1/issues`),
          fetch(`${API}/api/v1/analytics/urban-health`)
        ]);
        if(s.ok)setStats(await s.json());
        if(i.ok)setIssues(await i.json());
        if(h.ok)setHealth(await h.json());
        setOnline(s.ok&&i.ok&&h.ok);
      }catch(e){setOnline(false)}
    };
    load();const id=setInterval(load,2500);return()=>clearInterval(id);
  },[]);

  const bounds=useMemo(()=>{
    if(!issues.length)return {minLat:17.38,maxLat:17.39,minLon:78.48,maxLon:78.50};
    const lats=issues.map(x=>x.latitude),lons=issues.map(x=>x.longitude);
    return {minLat:Math.min(...lats)-.0002,maxLat:Math.max(...lats)+.0002,minLon:Math.min(...lons)-.0002,maxLon:Math.max(...lons)+.0002};
  },[issues]);

  const pointStyle=(x)=>({
    left:`${8+84*((x.longitude-bounds.minLon)/(bounds.maxLon-bounds.minLon||1))}%`,
    top:`${92-84*((x.latitude-bounds.minLat)/(bounds.maxLat-bounds.minLat||1))}%`
  });

  return <main>
    <header><div><p>TEAM BRUTE • SIH26124</p><h1>Urban Intelligence Command Center</h1></div><div className={`live ${online?'':'offline'}`}><i/> {online?'LIVE':'OFFLINE'}</div></header>

    <section className="stats">
      <Stat icon={Activity} label="Events this run" value={stats.total_events}/>
      <Stat icon={MapPin} label="Correlated issues" value={stats.correlated_issues}/>
      <Stat icon={Bus} label="Active buses" value={stats.active_bus_ids.length}/>
      <Stat icon={ShieldAlert} label="Critical signals" value={(stats.by_type?.vehicle_incident||0)+(stats.by_type?.pedestrian_risk||0)}/>
    </section>

    <section className="healthGrid">
      <Stat icon={HeartPulse} label="Road health" value={health.road_health_score} suffix="%"/>
      <Stat icon={Gauge} label="Congestion index" value={health.congestion_index} suffix="%"/>
      <Stat icon={ShieldAlert} label="Safety risk" value={health.safety_risk_score} suffix="%"/>
      <Stat icon={Route} label="Persisted events" value={stats.persisted_events||0}/>
    </section>

    <section className="grid">
      <div className="panel map"><h2>Live Urban Sensor Grid</h2><p>Spatially plotted correlated detections from the moving bus fleet.</p><div className="radar"><div className="ring r1"/><div className="ring r2"/><div className="ring r3"/>{issues.slice(-30).map((x,n)=><span title={`${x.event_type} • ${x.sightings} sightings`} key={n} className={x.event_type} style={pointStyle(x)}/>)}</div></div>
      <div className="panel"><h2>Priority Intelligence</h2><div className="feed">{health.priority_issues?.length===0?<p className="muted">Waiting for repeated fleet observations…</p>:health.priority_issues.map((x,n)=><article key={n}><div><b>{x.event_type.replaceAll('_',' ')}</b><small>{x.sightings} sightings • priority {x.priority_score}</small></div><em>{(x.confidence*100).toFixed(1)}%</em></article>)}</div></div>
      <div className="panel"><h2>Detection Matrix</h2><div className="matrix">{Object.entries(stats.by_type||{}).map(([k,v])=><div key={k}><span>{k.replaceAll('_',' ')}</span><b>{v}</b></div>)}</div></div>
      <div className="panel"><h2>Fleet Nodes</h2><div className="fleetList">{stats.active_bus_ids.length?stats.active_bus_ids.map(id=><span key={id}>{id}</span>):<p className="muted">Run the fleet simulator to populate live buses.</p>}</div></div>
      <div className="panel"><h2>Edge Processing</h2><div className="edge"><Waves/><div><b>Bandwidth-efficient event mode</b><p>Continuous video remains at the vehicle edge. Only compact detections, metadata and selected evidence are transmitted.</p></div></div></div>
    </section>
  </main>
}

createRoot(document.getElementById('root')).render(<App/>);
