import React from 'react'
import { createRoot } from 'react-dom/client'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer } from 'recharts'

const API = 'http://localhost:8000'

function App() {
  const [filters, setFilters] = React.useState({ regions: [], countries: [], years: [], metrics: [] })
  const [options, setOptions] = React.useState({ regions: [], countries: [], years: [], metrics: [] })
  const [summary, setSummary] = React.useState({ total: 0, average: 0, records: 0 })
  const [lineData, setLineData] = React.useState([])
  const [barData, setBarData] = React.useState([])
  const [lastUpload, setLastUpload] = React.useState(null)

  const qs = (f) => {
    const p = new URLSearchParams()
    Object.entries(f).forEach(([k, arr]) => arr.forEach(v => p.append(k, v)))
    return p.toString()
  }

  const fetchAll = async (current = filters) => {
    const q = qs(current)
    const [fRes, sRes, lRes, bRes, uRes] = await Promise.all([
      fetch(`${API}/filters?${qs({ regions: current.regions })}`),
      fetch(`${API}/summary?${q}`),
      fetch(`${API}/aggregate?group_by=year&agg=sum&${q}`),
      fetch(`${API}/aggregate?group_by=country&agg=sum&${q}`),
      fetch(`${API}/last-upload`)
    ])
    setOptions(await fRes.json())
    setSummary(await sRes.json())
    setLineData(await lRes.json())
    setBarData(await bRes.json())
    setLastUpload((await uRes.json()).uploaded_at)
  }

  React.useEffect(() => {
    const saved = localStorage.getItem('dashboard_filters')
    if (saved) {
      const parsed = JSON.parse(saved)
      setFilters(parsed)
      fetchAll(parsed)
    } else {
      fetchAll()
    }
  }, [])

  React.useEffect(() => {
    localStorage.setItem('dashboard_filters', JSON.stringify(filters))
    fetchAll(filters)
  }, [filters])

  React.useEffect(() => {
    const id = setInterval(async () => {
      const res = await fetch(`${API}/last-upload`)
      const body = await res.json()
      if (body.uploaded_at && body.uploaded_at !== lastUpload) fetchAll(filters)
    }, 10000)
    return () => clearInterval(id)
  }, [lastUpload, filters])

  const toggle = (key, val) => {
    setFilters(prev => {
      const has = prev[key].includes(val)
      return { ...prev, [key]: has ? prev[key].filter(x => x !== val) : [...prev[key], val] }
    })
  }

  return <div style={{display:'grid', gridTemplateColumns:'280px 1fr', minHeight:'100vh', fontFamily:'sans-serif'}}>
    <aside style={{padding:16, borderRight:'1px solid #ddd'}}>
      <h3>Filters</h3>
      {['regions','countries','years','metrics'].map(k => <div key={k}><strong>{k}</strong>{options[k]?.map(v => <div key={v}><label><input type='checkbox' checked={filters[k].includes(v)} onChange={() => toggle(k, v)} /> {v}</label></div>)}</div>)}
      <hr/>
      <a href={`${API}/export?${qs(filters)}`}>Export CSV</a>
    </aside>
    <main style={{padding:16}}>
      <h2>Monitoring Dashboard</h2>
      <small>Last upload: {lastUpload || 'none'}</small>
      <div style={{display:'flex', gap:12}}>
        <Card label='Total' value={summary.total?.toFixed?.(2) ?? 0} />
        <Card label='Average' value={summary.average?.toFixed?.(2) ?? 0} />
        <Card label='Records' value={summary.records ?? 0} />
      </div>
      <h3>Trend by Year</h3>
      <Chart><LineChart data={lineData}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey='key'/><YAxis/><Tooltip/><Legend/><Line type='monotone' dataKey='value'/></LineChart></Chart>
      <h3>Country Comparison</h3>
      <Chart><BarChart data={barData}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey='key'/><YAxis/><Tooltip/><Legend/><Bar dataKey='value'/></BarChart></Chart>
    </main>
  </div>
}

function Card({label, value}) { return <div style={{padding:12,border:'1px solid #ccc',borderRadius:8,minWidth:120}}><div>{label}</div><strong>{value}</strong></div> }
function Chart({children}) { return <div style={{width:'100%', height:320}}><ResponsiveContainer>{children}</ResponsiveContainer></div> }

createRoot(document.getElementById('root')).render(<App />)
