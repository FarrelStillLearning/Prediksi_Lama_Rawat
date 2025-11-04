import React, {useEffect, useState} from 'react'

const API_BASE = 'http://localhost:8000'

export default function App(){
  const [schema, setSchema] = useState(null)
  const [form, setForm] = useState({})
  const [result, setResult] = useState(null)

  useEffect(()=>{
    fetch(API_BASE + '/schema')
      .then(r => r.json())
      .then(s => {
        setSchema(s)
        // initialize form with first options where available
        const f = {}
        // initialize numeric field Umur with a reasonable default
        f['Umur'] = 30
        for(const k of Object.keys(s.categorical||{})){
          const opts = s.categorical[k]
          // keep first option as default if not Umur
          f[k]= (opts && opts.length>0)? opts[0] : ''
        }
        // add diagnosis fields (empty default so user types/searches)
        f['diagnosis_masuk'] = ''
        f['diagnosis_primer'] = ''
        setForm(f)
      }).catch(()=>{
        setSchema({categorical:{}, diagnosis_masuk:{}, diagnosis_primer:{}})
      })
  },[])

  if(!schema) return <div className="container"><h2>Loading schema...</h2></div>

  const onChange = (k, v) => setForm(prev=>({...prev, [k]: v}))

  const submit = async (e) =>{
    e.preventDefault()
    setResult(null)
    try{
  const resp = await fetch(API_BASE + '/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data: form})})
  const json = await resp.json()
  if(!resp.ok) throw new Error(json.detail || JSON.stringify(json))
  // Backend may return a decimal; present a rounded integer to users for "Lama Rawat (hari)"
  const predicted = json.prediction
  const rounded = (typeof predicted === 'number') ? Math.round(predicted) : predicted
  setResult(rounded)
    }catch(err){
      setResult('Error: ' + err.message)
    }
  }

  return (
    <div className="container">
      <h1>Prediksi Lama Rawat</h1>
      <form onSubmit={submit}>
        {/* Umur: explicit numeric input (always shown) */}
        <div className="field">
          <label>Umur</label>
          <input type="number" min={4} max={105} value={form['Umur']||''} onChange={e=>onChange('Umur', Number(e.target.value))} />
          <small>Masukkan umur pasien (rentang disarankan 4–105).</small>
        </div>

        {/* Render key categorical fields in a sensible order */}
        {(() => {
          const order = ['Jenis Kelamin','Segmentasi Peserta','Kepemilikan FKRTL','Jenis FKRTL','Tingkat Pelayanan FKRTL','Jenis Poli FKRTL']
          const elems = []
          for(const k of order){
            const opts = (schema.categorical||{})[k]
            if(!opts) continue
            elems.push(
              <div className="field" key={k}>
                <label>{k}</label>
                <select value={form[k]||''} onChange={e=>onChange(k, e.target.value)}>
                  {opts.map(o=> <option key={o} value={o}>{o}</option>)}
                </select>
              </div>
            )
          }
          // any other categorical fields not in order
          for(const [k, opts] of Object.entries(schema.categorical||{})){
            if(order.includes(k)) continue
            elems.push(
              <div className="field" key={k}>
                <label>{k}</label>
                <select value={form[k]||''} onChange={e=>onChange(k, e.target.value)}>
                  {opts.map(o=> <option key={o} value={o}>{o}</option>)}
                </select>
              </div>
            )
          }
          return elems
        })()}

        <div className="field">
          <label>Diagnosis Masuk (cari dengan nama diagnosis)</label>
          <input list="dm-list" value={form.diagnosis_masuk||''} onChange={e=>onChange('diagnosis_masuk', e.target.value)} placeholder="ketik nama diagnosis atau pilih dari saran" />
          <datalist id="dm-list">
            {Object.entries(schema.diagnosis_masuk||{}).map(([code,desc])=> (
              <option key={code} value={`${code} — ${desc}`}>{desc}</option>
            ))}
          </datalist>
        </div>

        <div className="field">
          <label>Diagnosis Primer (cari dengan nama diagnosis)</label>
          <input list="dp-list" value={form.diagnosis_primer||''} onChange={e=>onChange('diagnosis_primer', e.target.value)} placeholder="ketik nama diagnosis atau pilih dari saran" />
          <datalist id="dp-list">
            {Object.entries(schema.diagnosis_primer||{}).map(([code,desc])=> (
              <option key={code} value={`${code} — ${desc}`}>{desc}</option>
            ))}
          </datalist>
        </div>

        <div style={{marginTop:16}}>
          <button type="submit">Submit</button>
        </div>
      </form>

      {result !== null && (
        <div className="result">Prediksi: {String(result)} Hari</div>
      )}
    </div>
  )
}
