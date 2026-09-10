import React,{useEffect,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Activity,Bus,MapPin,ShieldAlert,Waves,Gauge,HeartPulse,Route,Wrench,CheckCircle2,PlayCircle} from 'lucide-react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import './styles.css';

const API=import.meta.env.VITE_API_URL||'http://127.0.0.1:8000';

function Stat({icon:Icon,label,value,suffix=''}){return <div className="card"><Icon size={22}/><div><span>{label}</span><strong>{value}{suffix}</strong></div></div>}

function GISMap({geojson}){
  const node=useRef(null),mapRef=useRef(null);
  useEffect(()=>{
    if(mapRef.current||!node.current)return;
    const map=new maplibregl.Map({container:node.current,center:[78.4867,17.3850],zoom:12,style:{version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap contributors'}},layers:[{id:'osm',type:'raster',source:'osm'}]}});
    map.addControl(new maplibregl.NavigationControl(),'top-right');
    map.on('load',()=>{
      map.addSource('issues',{type:'geojson',data:geojson});
      map.addLayer({id:'issues-glow',type:'circle',source:'issues',paint:{'circle-radius':['interpolate',['linear'],['get','sightings'],1,7,5,15],'circle-color':['match',['get','event_type'],'pothole','#ff5d73','waterlogging','#3ea6ff','pedestrian_risk','#ffc857','traffic_congestion','#ff8c42','#6ae4ff'],'circle-opacity':.78,'circle-stroke-width':2,'circle-stroke-color':'#ffffff'}});
    });
    mapRef.current=map;return()=>{map.remove();mapRef.current=null};
  },[]);
  useEffect(()=>{const map=mapRef.current;if(!map)return;const update=()=>{const src=map.getSource('issues');if(src)src.setData(geojson)};if(map.isStyleLoaded())update();else map.once('load',update)},[geojson]);
  return <div ref={node} className="mapCanvas"/>;
}

function App(){
  const [stats,setStats]=useState({total_events:0,persisted_events:0,correlated_issues:0,authority_work_items:0,active_bus_ids:[],by_type:{}});
  const [geojson,setGeojson]=useState({type:'FeatureCollection',features:[]});
  const [health,setHealth]=useState({road_health_score:100,congestion_index:0,safety_risk_score:0,priority_issues:[]});
  const [workItems,setWorkItems]=useState([]);
  const [online,setOnline]=useState(false);

  const load=async()=>{
    try{
      const [s,h,g,w]=await Promise.all([fetch(`${API}/api/v1/stats`),fetch(`${API}/api/v1/analytics/urban-health`),fetch(`${API}/api/v1/gis/issues.geojson`),fetch(`${API}/api/v1/authority/work-items`)]);
      if(s.ok)setStats(await s.json());if(h.ok)setHealth(await h.json());if(g.ok)setGeojson(await g.json());if(w.ok)setWorkItems(await w.json());setOnline(s.ok&&h.ok&&g.ok&&w.ok);
    }catch(e){setOnline(false)}
  };

  useEffect(()=>{load();const id=setInterval(load,2500);return()=>clearInterval(id)},[]);

  const transition=async(item,status)=>{
    const body={status,assignee:item.assignee||'City Operations',note:`Updated from SIH26124 command center to ${status}`};
    const response=await fetch(`${API}/api/v1/authority/work-items/${item.id}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    if(response.ok)await load();
  };

  return <main>
    <header><div><p>TEAM BRUTE • SIH26124</p><h1>Urban Intelligence Command Center</h1></div><div className={`live ${online?'':'offline'}`}><i/> {online?'LIVE':'OFFLINE'}</div></header>
    <section className="stats"><Stat icon={Activity} label="Loaded events" value={stats.total_events}/><Stat icon={MapPin} label="Correlated issues" value={stats.correlated_issues}/><Stat icon={Bus} label="Active buses" value={stats.active_bus_ids.length}/><Stat icon={Wrench} label="Authority jobs" value={stats.authority_work_items||0}/></section>
    <section className="healthGrid"><Stat icon={HeartPulse} label="Road health" value={health.road_health_score} suffix="%"/><Stat icon={Gauge} label="Congestion index" value={health.congestion_index} suffix="%"/><Stat icon={ShieldAlert} label="Safety risk" value={health.safety_risk_score} suffix="%"/><Stat icon={Route} label="Persisted events" value={stats.persisted_events||0}/></section>
    <section className="grid">
      <div className="panel map"><h2>Live GIS Intelligence Map</h2><p>Correlated fleet observations rendered from the backend GeoJSON feed.</p><GISMap geojson={geojson}/></div>
      <div className="panel"><h2>Priority Intelligence</h2><div className="feed">{health.priority_issues?.length===0?<p className="muted">Waiting for repeated fleet observations…</p>:health.priority_issues.map((x,n)=><article key={n}><div><b>{x.event_type.replaceAll('_',' ')}</b><small>{x.sightings} sightings • priority {x.priority_score}</small></div><em>{(x.confidence*100).toFixed(1)}%</em></article>)}</div></div>
      <div className="panel authorityPanel"><h2>Authority Workflow</h2><div className="feed">{workItems.length===0?<p className="muted">No authority work items yet.</p>:workItems.slice(0,8).map(x=><article key={x.id} className="workItem"><div><b>{x.event_type.replaceAll('_',' ')}</b><small>{x.status} • severity {x.severity} • {(x.confidence*100).toFixed(0)}%</small><small>{x.assignee||'Unassigned'}</small></div><div className="workActions">{!['in_progress','resolved','rejected'].includes(x.status)&&<button onClick={()=>transition(x,'in_progress')}><PlayCircle size={14}/> Start</button>}{x.status!=='resolved'&&x.status!=='rejected'&&<button onClick={()=>transition(x,'resolved')}><CheckCircle2 size={14}/> Resolve</button>}</div></article>)}</div></div>
      <div className="panel"><h2>Detection Matrix</h2><div className="matrix">{Object.entries(stats.by_type||{}).map(([k,v])=><div key={k}><span>{k.replaceAll('_',' ')}</span><b>{v}</b></div>)}</div></div>
      <div className="panel"><h2>Fleet Nodes</h2><div className="fleetList">{stats.active_bus_ids.length?stats.active_bus_ids.map(id=><span key={id}>{id}</span>):<p className="muted">Run the fleet simulator to populate live buses.</p>}</div></div>
      <div className="panel"><h2>Edge Processing</h2><div className="edge"><Waves/><div><b>Bandwidth-efficient event mode</b><p>Continuous video remains at the vehicle edge. Only compact detections, metadata and selected evidence are transmitted.</p></div></div></div>
    </section>
  </main>
}

createRoot(document.getElementById('root')).render(<App/>);
