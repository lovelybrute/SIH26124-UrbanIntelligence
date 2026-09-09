import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Activity, Bus, MapPin, ShieldAlert, Waves} from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function Stat({icon:Icon,label,value}){return <div className="card"><Icon size={22}/><div><span>{label}</span><strong>{value}</strong></div></div>}

function App(){
  const [stats,setStats]=useState({total_events:0,correlated_issues:0,active_bus_ids:[],by_type:{}});
  const [issues,setIssues]=useState([]);
  useEffect(()=>{
    const load=async()=>{
      try{
        const [s,i]=await Promise.all([fetch(`${API}/api/v1/stats`),fetch(`${API}/api/v1/issues`)]);
        if(s.ok) setStats(await s.json());
        if(i.ok) setIssues(await i.json());
      }catch(e){}
    };
    load(); const id=setInterval(load,3000); return ()=>clearInterval(id);
  },[]);

  return <main>
    <header><div><p>TEAM BRUTE • SIH26124</p><h1>Urban Intelligence Command Center</h1></div><div className="live"><i/> LIVE</div></header>
    <section className="stats">
      <Stat icon={Activity} label="Events" value={stats.total_events}/>
      <Stat icon={MapPin} label="Verified Issues" value={stats.correlated_issues}/>
      <Stat icon={Bus} label="Active Buses" value={stats.active_bus_ids.length}/>
      <Stat icon={ShieldAlert} label="Critical Signals" value={(stats.by_type?.vehicle_incident||0)+(stats.by_type?.pedestrian_risk||0)}/>
    </section>
    <section className="grid">
      <div className="panel map"><div className="mapGlow"/><h2>City Sensor Grid</h2><p>GIS layer placeholder ready for MapLibre/Mapbox integration.</p><div className="radar"><div className="ring r1"/><div className="ring r2"/><div className="ring r3"/>{issues.slice(0,8).map((x,n)=><span key={n} style={{left:`${15+(n*17)%70}%`,top:`${20+(n*23)%60}%`}}/> )}</div></div>
      <div className="panel"><h2>Recent Correlated Issues</h2><div className="feed">{issues.length===0?<p className="muted">Waiting for edge events…</p>:issues.slice(-8).reverse().map((x,n)=><article key={n}><div><b>{x.event_type.replaceAll('_',' ')}</b><small>{x.sightings} sightings • {(x.confidence*100).toFixed(1)}%</small></div><em>{x.latitude.toFixed(4)}, {x.longitude.toFixed(4)}</em></article>)}</div></div>
      <div className="panel"><h2>Detection Matrix</h2><div className="matrix">{Object.entries(stats.by_type||{}).map(([k,v])=><div key={k}><span>{k.replaceAll('_',' ')}</span><b>{v}</b></div>)}</div></div>
      <div className="panel"><h2>Edge Status</h2><div className="edge"><Waves/><div><b>Bandwidth-efficient event mode</b><p>Raw video stays at the edge; compact AI events flow to the central platform.</p></div></div></div>
    </section>
  </main>
}

createRoot(document.getElementById('root')).render(<App/>);
