#!/usr/bin/env python3
"""Portfolio page: slim stat grid (6→4 cards) + replace empty Performance chart with P/L bar chart"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── A) Slim stat grid: remove "Total Invested Capital" and "Total P/L (Combined)" ──
OLD_STAT = """  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat"><div class="stat-lbl">Total Invested Capital</div><div class="stat-val">${fRp(P.totalModal)}</div></div>
    <div class="stat gold"><div class="stat-lbl">Current Portfolio Value</div><div class="stat-val gold">${fRp(P.totalNilai)}</div></div>
    <div class="stat ${P.totalPnl>=0?'':''}"><div class="stat-lbl">Unrealized P/L</div><div class="stat-val ${gls(P.totalPnl)}">${fRp(P.totalPnl)}</div></div>
    <div class="stat ${(P.totalRealized||0)>=0?'':''}"><div class="stat-lbl">Realized P/L</div><div class="stat-val ${gls(P.totalRealized||0)}">${fRp(P.totalRealized||0)}</div></div>
    <div class="stat ${gls(P.totalCombinedPnl)}">
      <div class="stat-lbl">Total P/L (Combined)</div>
      <div class="stat-val ${gls(P.totalCombinedPnl)}">${fRp(P.totalCombinedPnl)}</div>
      <div class="stat-hint">Unrealized + Realized</div>
    </div>
    <div class="stat"><div class="stat-lbl">Total Return</div><div class="stat-val ${gls(P.totalRet)}">${fPct(P.totalRet)}</div></div>
  </div>"""

NEW_STAT = """  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat gold"><div class="stat-lbl">Nilai Portfolio</div><div class="stat-val gold">${fRp(P.totalNilai)}</div><div class="stat-hint">Modal ${fRp(P.totalModal)}</div></div>
    <div class="stat"><div class="stat-lbl">Unrealized P/L</div><div class="stat-val ${gls(P.totalPnl)}">${fRp(P.totalPnl)}</div></div>
    <div class="stat"><div class="stat-lbl">Realized P/L</div><div class="stat-val ${gls(P.totalRealized||0)}">${fRp(P.totalRealized||0)}</div></div>
    <div class="stat"><div class="stat-lbl">Total Return</div><div class="stat-val ${gls(P.totalRet)}">${fPct(P.totalRet)}</div><div class="stat-hint">Combined P/L ${fRp(P.totalCombinedPnl)}</div></div>
  </div>"""

assert OLD_STAT in content, "A) stat grid not found"
content = content.replace(OLD_STAT, NEW_STAT, 1)
print("A) stat grid slimmed to 4 cards")

# ── B) Replace Performance chart panel with P/L per Asset Class bar chart ──
OLD_PERF_PANEL = """    <div class="chart-card" style="margin:0">
      <div class="chart-hdr"><div class="chart-title">📈 Portfolio Performance</div></div>
      <div id="port-perf-empty" style="display:none;text-align:center;padding:40px;color:var(--t3);font-size:13px">Belum ada data histori.</div>
      <div class="chart-wrap" style="height:240px"><canvas id="ch-port-perf"></canvas></div>
    </div>"""

NEW_PERF_PANEL = """    <div class="chart-card" style="margin:0">
      <div class="chart-hdr"><div class="chart-title">📊 P/L per Jenis Aset</div></div>
      <div class="chart-wrap" style="height:240px"><canvas id="ch-port-pnl"></canvas></div>
    </div>"""

assert OLD_PERF_PANEL in content, "B) Performance panel not found"
content = content.replace(OLD_PERF_PANEL, NEW_PERF_PANEL, 1)
print("B) Performance chart panel replaced with P/L bar chart panel")

# ── C) Replace chart rendering JS: perf → pnl bar ──
OLD_CHART_JS = """  // Performance — pakai snapshot totalInvestasi
  const perfCtx = document.getElementById('ch-port-perf')?.getContext('2d');
  const emptyEl = document.getElementById('port-perf-empty');
  if(perfCtx){
    const data = STATE.snapshots.filter(s=>s.totalInvestasi>0);
    if(!data.length){ if(emptyEl){emptyEl.style.display='block';perfCtx.canvas.style.display='none';} }
    else{
      if(emptyEl) emptyEl.style.display='none'; perfCtx.canvas.style.display='block';
      if(CHARTS.portPerf) CHARTS.portPerf.destroy();
      const grad=perfCtx.createLinearGradient(0,0,0,240);
      grad.addColorStop(0,'rgba(212,168,75,.15)'); grad.addColorStop(1,'rgba(212,168,75,0)');
      CHARTS.portPerf=new Chart(perfCtx,{
        type:'line',
        data:{labels:data.map(s=>{const d=new Date(s.date);return d.toLocaleDateString('id-ID',{day:'numeric',month:'short'});}),
          datasets:[{label:'Nilai Investasi',data:data.map(s=>s.totalInvestasi),borderColor:'#d4a84b',backgroundColor:grad,borderWidth:2.5,pointRadius:data.length>60?0:3,tension:.35,fill:true}]},
        options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#4a5268',maxTicksLimit:8,font:{size:10}},grid:{color:'rgba(255,255,255,.04)'}},y:{ticks:{color:'#4a5268',callback:v=>'Rp'+Math.round(v/1e6)+'jt'},grid:{color:'rgba(255,255,255,.04)'}}}}
      });
    }
  }"""

NEW_CHART_JS = """  // P/L per Jenis Aset bar chart
  const pnlCtx = document.getElementById('ch-port-pnl')?.getContext('2d');
  if(pnlCtx){
    const segs = P.byTipe.filter(b=>b.modal>0);
    const unrealized = segs.map(b=>b.nilai-b.modal);
    const realized = segs.map(b=>{
      const tipeKey=b.tipe==='Bitcoin'?'BTC':b.tipe;
      return portPositions.filter(p=>tipeKey==='BTC'?p.kode==='BTC':p.tipe===tipeKey).reduce((s,p)=>s+(p.realizedPnl||0),0);
    });
    if(CHARTS.portPnl) CHARTS.portPnl.destroy();
    CHARTS.portPnl=new Chart(pnlCtx,{
      type:'bar',
      data:{
        labels:segs.map(s=>s.tipe),
        datasets:[
          {label:'Unrealized P/L',data:unrealized,backgroundColor:unrealized.map(v=>v>=0?'rgba(82,196,126,.7)':'rgba(240,85,88,.7)'),borderRadius:4},
          {label:'Realized P/L',data:realized,backgroundColor:realized.map(v=>v>=0?'rgba(82,196,126,.4)':'rgba(240,85,88,.4)'),borderRadius:4}
        ]
      },
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#8892a4',font:{size:11}}},tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${fRp(ctx.raw)}`}}},scales:{x:{ticks:{color:'#4a5268',font:{size:11}},grid:{display:false}},y:{ticks:{color:'#4a5268',callback:v=>v>=0?'+'+Math.round(v/1e6)+'jt':Math.round(v/1e6)+'jt'},grid:{color:'rgba(255,255,255,.04)'}}}}
    });
  }"""

assert OLD_CHART_JS in content, "C) Chart JS not found"
content = content.replace(OLD_CHART_JS, NEW_CHART_JS, 1)
print("C) Chart JS replaced with P/L bar chart rendering")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Done. {len(content)} chars written.")
