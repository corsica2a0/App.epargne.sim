import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
import numpy as np

st.set_page_config(
    page_title="Calculateur d'épargne", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTextInput>div>div>input {
        color: #4B5563;
    }
    .stNumberInput>div>div>input {
        color: #4B5563;
    }
    </style>
    """, unsafe_allow_html=True)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

st.title("📈 Calculateur de Projection d'Épargne")
def calculate_savings(initial_capital, monthly_saving, yearly_saving, years, annual_rate, compound_interest=True):
    """
    Calcule l'évolution de l'épargne avec ou sans intérêts composés
    """
    data = []
    total = initial_capital
    total_contributions = initial_capital
    monthly_rate = annual_rate / 12
    
    if not compound_interest:
        total_months = years * 12
        total_investment = initial_capital + (monthly_saving * total_months) + (yearly_saving * years)
        simple_interest = total_investment * annual_rate * years
        
        current_investment = initial_capital
        for year in range(years + 1):
            data.append({
                'year': year,
                'total': round(current_investment + (simple_interest * year / years)),
                'contributions': round(current_investment),
                'earnings': round(simple_interest * year / years)
            })
            if year < years:
                current_investment += yearly_saving + (monthly_saving * 12)
        return pd.DataFrame(data)
    
    for year in range(years + 1):
        data.append({
            'year': year,
            'total': round(total),
            'contributions': round(total_contributions),
            'earnings': round(total - total_contributions)
        })
        
        if year < years:
            if year > 0:
                total = (total + yearly_saving) * (1 + monthly_rate)
                total_contributions += yearly_saving
            
            for _ in range(12):
                total = (total + monthly_saving) * (1 + monthly_rate)
                total_contributions += monthly_saving
    
    return pd.DataFrame(data)

def format_currency(value):
    """
    Formate un nombre en devise euro
    """
    return f"{value:,.0f} €"

def calculate_percentage(value, total):
    """
    Calcule et formate un pourcentage
    """
    if total == 0:
        return "0.0%"
    return f"{(value/total*100):.1f}%"

def monte_carlo_simulation(initial_capital, monthly_saving, yearly_saving, years, mean_return, volatility, n_simulations=1000):
    """
    Réalise une simulation Monte Carlo
    """
    monthly_return = mean_return / 12
    monthly_vol = volatility / np.sqrt(12)
    
    results = []
    for _ in range(n_simulations):
        total = initial_capital
        for year in range(years):
            if year > 0:
                total = (total + yearly_saving)
            for _ in range(12):
                return_rate = np.random.normal(monthly_return, monthly_vol)
                total = (total + monthly_saving) * (1 + return_rate)
        results.append(total)
    
    return np.array(results)


def create_line_plot(df):
    """
    Crée le graphique linéaire d'évolution du capital
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['total'],
        name='Capital Total',
        line=dict(color='#2563eb', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['contributions'],
        name='Total Versé',
        line=dict(color='#16a34a', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['earnings'],
        name='Plus-Values',
        line=dict(color='#dc2626', width=2)
    ))
    
    fig.update_layout(
        title='Évolution du capital dans le temps',
        xaxis_title='Années',
        yaxis_title='Montant (€)',
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_yaxes(tickformat=',.0f')
    return fig

def create_pie_chart(final_data, initial_capital):
    """
    Crée le graphique en secteurs de la répartition finale
    """
    fig = go.Figure(data=[go.Pie(
        values=[
            initial_capital,
            final_data['contributions'] - initial_capital,
            final_data['earnings']
        ],
        labels=['Capital initial', 'Versements', 'Plus-values'],
        marker_colors=['#2563eb', '#16a34a', '#dc2626'],
        hole=0.4
    )])
    
    fig.update_layout(
        title='Répartition finale du capital',
        template='plotly_white',
        legend=dict(orientation="h")
    )
    
    return fig

def create_monte_carlo_plot(results):
    """
    Crée le graphique pour la simulation Monte Carlo
    """
    fig = go.Figure()
    fig.add_trace(go.Box(
        y=results,
        name="Distribution des résultats",
        boxpoints='outliers'
    ))
    
    fig.update_layout(
        title="Distribution des résultats possibles",
        yaxis_title="Capital Final (€)",
        template='plotly_white'
    )
    
    return fig
    # Création des colonnes pour le formulaire
col1, col2, col3 = st.columns(3)

with col1:
    initial_capital = st.number_input("Capital initial (€)", 
                                    min_value=0, 
                                    value=1000, 
                                    step=500,
                                    help="Montant initial investi")
    monthly_saving = st.number_input("Épargne mensuelle (€)", 
                                   min_value=0, 
                                   value=150, 
                                   step=50,
                                   help="Montant épargné chaque mois")

with col2:
    yearly_saving = st.number_input("Épargne annuelle (€)", 
                                  min_value=0, 
                                  value=1000, 
                                  step=500,
                                  help="Versement supplémentaire annuel")
    years = st.number_input("Durée (années)", 
                          min_value=1, 
                          max_value=50, 
                          value=15,
                          help="Durée de l'investissement")

with col3:
    annual_rate = st.number_input("Taux annuel (%)", 
                                min_value=0.0, 
                                max_value=20.0, 
                                value=7.0, 
                                step=0.5,
                                help="Taux de rendement annuel espéré") / 100
    compound_interest = st.checkbox("Activer les intérêts composés", 
                                  value=True,
                                  help="Cochez pour réinvestir les intérêts")

df = calculate_savings(initial_capital, monthly_saving, yearly_saving, years, annual_rate, compound_interest)
final_data = df.iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Capital Final",
        format_currency(final_data['total']),
        format_currency(final_data['total'] - initial_capital)
    )

with col2:
    st.metric(
        "Total Versé",
        format_currency(final_data['contributions'])
    )

with col3:
    st.metric(
        "Plus-Values",
        format_currency(final_data['earnings']),
        calculate_percentage(final_data['earnings'], final_data['contributions'])
    )

st.plotly_chart(create_line_plot(df), use_container_width=True)
st.plotly_chart(create_pie_chart(final_data, initial_capital), use_container_width=True)

show_monte_carlo = st.checkbox("Afficher la simulation Monte Carlo",
                             help="Simule différents scénarios possibles")

if show_monte_carlo:
    volatility = st.slider("Volatilité annuelle (%)", 5, 30, 15) / 100
    results = monte_carlo_simulation(
        initial_capital, monthly_saving, yearly_saving,
        years, annual_rate, volatility
    )
    
    st.plotly_chart(create_monte_carlo_plot(results), use_container_width=True)
    
    percentiles = np.percentile(results, [5, 25, 50, 75, 95])
    st.write("Statistiques de la simulation :")
    st.write(f"- Capital minimum : {format_currency(results.min())}")
    st.write(f"- 5ème percentile : {format_currency(percentiles[0])}")
    st.write(f"- Médiane : {format_currency(percentiles[2])}")
    st.write(f"- 95ème percentile : {format_currency(percentiles[4])}")
    st.write(f"- Capital maximum : {format_currency(results.max())}")

st.subheader("📊 Détails des versements")
col1, col2 = st.columns(2)

with col1:
    st.write("Versements mensuels :")
    st.write(f"- Par mois : {format_currency(monthly_saving)}")
    st.write(f"- Par an : {format_currency(monthly_saving * 12)}")
    st.write(f"- Sur la durée : {format_currency(monthly_saving * 12 * years)}")

with col2:
    st.write("Versements annuels :")
    st.write(f"- Par an : {format_currency(yearly_saving)}")
    st.write(f"- Sur la durée : {format_currency(yearly_saving * years)}")
    st.write(f"- Total épargné par an : {format_currency(monthly_saving * 12 + yearly_saving)}")

if st.button("Télécharger les résultats (CSV)"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Confirmer le téléchargement",
        data=csv,
        file_name="projection_epargne.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>💡 Les projections sont basées sur un taux de rendement hypothétique constant.
    Les performances passées ne préjugent pas des performances futures.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.subheader("📈 Analyse de rendement")

col1, col2 = st.columns(2)

with col1:
    if years > 0:
        avg_return = ((final_data['total'] / initial_capital) ** (1/years) - 1) * 100
        st.metric(
            "Rendement annualisé moyen",
            f"{avg_return:.2f}%",
            help="Taux de rendement moyen sur la période"
        )

    total_return = ((final_data['total'] / initial_capital) - 1) * 100
    st.metric(
        "Rendement total",
        f"{total_return:.2f}%",
        help="Rendement total sur toute la période"
    )

with col2:
    multiplier = final_data['total'] / final_data['contributions']
    st.metric(
        "Multiplicateur d'investissement",
        f"x{multiplier:.2f}",
        help="Combien d'euros obtenus pour chaque euro investi"
    )

    efficiency_ratio = final_data['earnings'] / final_data['contributions'] * 100
    st.metric(
        "Ratio plus-values/versements",
        f"{efficiency_ratio:.1f}%",
        help="Pourcentage des plus-values par rapport aux versements"
    )

st.markdown("---")
st.subheader("🔄 Analyse des scénarios")

rates = [annual_rate - 0.02, annual_rate, annual_rate + 0.02]  # -2%, Base, +2%
scenarios_data = []

for rate in rates:
    df_scenario = calculate_savings(initial_capital, monthly_saving, yearly_saving, years, rate, compound_interest)
    final_scenario = df_scenario.iloc[-1]
    scenarios_data.append({
        'Scénario': f"Taux {rate*100:.1f}%",
        'Capital Final': final_scenario['total'],
        'Plus-Values': final_scenario['earnings']
    })

for scenario in scenarios_data:
    st.write(f"**{scenario['Scénario']}** :")
    st.write(f"- Capital final : {format_currency(scenario['Capital Final'])}")
    st.write(f"- Plus-values : {format_currency(scenario['Plus-Values'])}")

st.markdown("---")
st.subheader("💡 Recommandations")

recommendations = []

monthly_total = monthly_saving + (yearly_saving / 12)
if monthly_total < 100:
    recommendations.append("Essayez d'augmenter votre épargne mensuelle pour atteindre vos objectifs plus rapidement.")
elif monthly_total > 1000:
    recommendations.append("Votre taux d'épargne est excellent ! Pensez à diversifier vos investissements.")

if years < 5:
    recommendations.append("Pour un investissement en actions, privilégiez un horizon d'au moins 5 ans.")
elif years > 20:
    recommendations.append("Sur une longue période, pensez à réévaluer régulièrement votre stratégie d'investissement.")

if not compound_interest:
    recommendations.append("Le réinvestissement des gains (intérêts composés) peut significativement améliorer vos rendements.")

if recommendations:
    for rec in recommendations:
        st.write(f"- {rec}")
else:
    st.write("Votre stratégie d'investissement semble bien équilibrée.")

if st.button("Réinitialiser tous les paramètres"):
    st.experimental_rerun()

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>🔒 Cette application est fournie à titre informatif uniquement.</p>
    <p>📊 Les calculs sont basés sur des hypothèses simplifiées et ne tiennent pas compte de l'inflation ou de la fiscalité.</p>
    <p>💼 Consultez un conseiller financier pour des recommandations personnalisées.</p>
</div>
""", unsafe_allow_html=True)
