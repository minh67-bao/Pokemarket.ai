import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="POKÉMARKET AI", page_icon="🃏", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
:root{color-scheme:dark}
.block-container{max-width:1200px;padding:1rem 1rem 3rem}
h1{letter-spacing:-.04em}
[data-testid="stMetric"]{background:#151d2b;border:1px solid #28364b;padding:12px;border-radius:14px}
div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]{gap:.65rem}
.cardbox{background:#151d2b;border:1px solid #28364b;border-radius:16px;padding:14px;margin:5px 0}
.muted{color:#9ba9bc;font-size:.82rem}
.signal{font-weight:700;color:#8be0ae}
@media(max-width:700px){.block-container{padding:.65rem .7rem 2rem} h1{font-size:1.8rem!important}}
</style>
""",unsafe_allow_html=True)

# Explicitly illustrative records; no live provider feeds are connected in this build.
data = [
 {"card":"Southern Islands Mew","set":"Southern Islands","pokemon":"Mew","era":"Vintage","condition":"Raw","market":240,"fair":285,"pop10":420,"pop_total":2400,"pokemon_score":96,"set_score":91,"art_score":96,"sales30":62,"momentum":74,"liquidity":66},
 {"card":"Neo Destiny Shining Charizard","set":"Neo Destiny","pokemon":"Charizard","era":"Vintage","condition":"Raw","market":1450,"fair":1575,"pop10":35,"pop_total":510,"pokemon_score":99,"set_score":95,"art_score":98,"sales30":18,"momentum":81,"liquidity":52},
 {"card":"EX Team Rocket Returns Mudkip Gold Star","set":"EX Team Rocket Returns","pokemon":"Mudkip","era":"Mid-era","condition":"Raw","market":780,"fair":930,"pop10":18,"pop_total":190,"pokemon_score":76,"set_score":90,"art_score":84,"sales30":9,"momentum":67,"liquidity":31},
 {"card":"Evolving Skies Umbreon VMAX Alt Art","set":"Evolving Skies","pokemon":"Umbreon","era":"Modern","condition":"Raw","market":1250,"fair":1190,"pop10":180,"pop_total":2100,"pokemon_score":99,"set_score":97,"art_score":98,"sales30":145,"momentum":88,"liquidity":91},
 {"card":"Skyridge Crystal Charizard","set":"Skyridge","pokemon":"Charizard","era":"Vintage","condition":"PSA 10","market":18500,"fair":19200,"pop10":9,"pop_total":210,"pokemon_score":99,"set_score":96,"art_score":99,"sales30":3,"momentum":69,"liquidity":20},
 {"card":"POP Series 5 Umbreon Gold Star","set":"POP Series 5","pokemon":"Umbreon","era":"Mid-era","condition":"Raw","market":2100,"fair":2300,"pop10":12,"pop_total":105,"pokemon_score":99,"set_score":88,"art_score":94,"sales30":5,"momentum":71,"liquidity":23},
]
df=pd.DataFrame(data)
df["undervaluation"]=(df.fair/df.market-1)*100
df["scarcity_score"]=(100-(df.pop_total.clip(lower=1).apply(lambda n:min(100,18*__import__("math").log10(n))))).clip(0,100)
df["value_score"]=(50+df.undervaluation).clip(0,100)
df["score"]=(df.value_score*.25+df.scarcity_score*.15+df.pokemon_score*.15+df.set_score*.10+df.art_score*.15+df.momentum*.10+df.liquidity*.10).clip(0,100)
df["signal"]=df.score.apply(lambda x:"BUY WATCH" if x>=75 else "RESEARCH" if x>=60 else "WAIT")

st.title("🃏 POKÉMARKET AI")
st.caption("GLOBAL POKÉMON CARD MARKET INTELLIGENCE")
st.warning("DEMO MODE — All card prices, populations, scores and forecasts shown here are illustrative examples. No live eBay or grading-provider data is connected yet.")

with st.expander("Filters & strategy",expanded=False):
    era=st.multiselect("Era",sorted(df.era.unique()),default=sorted(df.era.unique()))
    cond=st.multiselect("Condition",sorted(df.condition.unique()),default=sorted(df.condition.unique()))
    strategy=st.selectbox("Strategy",["Balanced","Fast growth","Long-term value"])
    horizon=st.selectbox("Forecast horizon",["7 days","30 days","90 days","6 months","1 year","2 years"])
view=df[df.era.isin(era)&df.condition.isin(cond)].copy()
if strategy=="Fast growth": view["rank_score"]=view.momentum*.55+view.score*.45
elif strategy=="Long-term value": view["rank_score"]=view.value_score*.55+view.scarcity_score*.25+view.score*.20
else:view["rank_score"]=view.score
view=view.sort_values("rank_score",ascending=False)

a,b,c=st.columns(3)
a.metric("Cards tracked",len(view))
b.metric("Potential opportunities",int((view.signal=="BUY WATCH").sum()))
c.metric("Market coverage","8 regions*")
st.caption("*Global market coverage is planned; not live in this demo.")
st.divider()
st.subheader("Today's opportunity scanner")
for _,r in view.iterrows():
    with st.container():
        st.markdown(f"""
        <div class="cardbox">
        <div style="display:flex;justify-content:space-between;gap:10px;align-items:center">
        <div><b>{r.card}</b><div class="muted">{r.set} · {r.pokemon} · {r.condition}</div></div>
        <div style="text-align:right"><b>{r.rank_score:.0f}/100</b><div class="signal">{r.signal}</div></div>
        </div>
        </div>""",unsafe_allow_html=True)
        x,y,z=st.columns(3)
        x.metric("Demo market",f"${r.market:,.0f}")
        y.metric("Model fair value",f"${r.fair:,.0f}",f"{r.undervaluation:+.1f}%")
        z.metric("PSA 10 pop",f"{r.pop10:,}")

st.divider()
st.subheader("Card research")
choice=st.selectbox("Select card",view.card.tolist() if len(view) else df.card.tolist())
r=df[df.card==choice].iloc[0]
p,q,t,u=st.columns(4)
p.metric("Pokémon popularity",f"{r.pokemon_score}/100")
q.metric("Set popularity",f"{r.set_score}/100")
t.metric("Artwork score",f"{r.art_score}/100")
u.metric("Sales / 30 days",f"{r.sales30}")
factor=pd.DataFrame({"Factor":["Value","Scarcity","Pokémon","Set","Artwork","Momentum","Liquidity"],"Score":[r.value_score,r.scarcity_score,r.pokemon_score,r.set_score,r.art_score,r.momentum,r.liquidity]})
fig=px.bar(factor,x="Score",y="Factor",orientation="h",range_x=[0,100],title="Illustrative card factor scores")
fig.update_layout(height=320,margin=dict(l=5,r=5,t=45,b=5))
st.plotly_chart(fig,use_container_width=True)
st.subheader("Forecast workspace")
days={"7 days":7,"30 days":30,"90 days":90,"6 months":182,"1 year":365,"2 years":730}[horizon]
daily=(r.momentum-50)/10000
scenario=r.market*((1+daily)**days)
st.metric(f"Illustrative {horizon} scenario",f"${scenario:,.0f} AUD")
st.caption("This is a toy scenario formula, not a trained forecast. Production forecasts require real historical sales and walk-forward backtesting.")

st.divider()
st.subheader("Global sold-sales data")
st.write("Planned ingestion: eBay AU, US, UK, CA, DE, FR, IT and ES. Each sale will retain source, listing ID, sold date, currency, shipping, condition, grade and confidence.")
st.subheader("Data integrity rules")
st.markdown("- Sold transactions only; asking prices are excluded.\n- Raw, PSA, BGS, CGC, language and variant are kept separate.\n- Currency conversion uses the exchange rate on the sale date.\n- Duplicates and suspicious outliers are flagged.\n- Population means graded submissions, not total copies in existence.")
st.caption("POKÉMARKET AI · Mobile-first cloud prototype")
