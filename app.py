import streamlit as st
import pandas as pd
import numpy as np
from src.model_saver import load_model, predict_single, predict_batch
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="HIV Drug Resistance Predictor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00d9ff;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --dark-bg: #f8f9fa;
        --card-bg: #ffffff;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .header-container p {
        margin: 5px 0;
        font-size: 1.1em;
        opacity: 0.95;
    }
    
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
    }
    
    .card-title {
        font-size: 1.5em;
        font-weight: 700;
        color: #333;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .stats-container {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        flex: 1;
        min-width: 150px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stat-value {
        font-size: 1.8em;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .stat-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .input-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 2px dashed #667eea;
    }
    
    .success-alert {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        margin-bottom: 15px;
    }
    
    .error-alert {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        margin-bottom: 15px;
    }
    
    .info-alert {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #17a2b8;
        margin-bottom: 15px;
    }
    
    .button-container {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        flex-wrap: wrap;
    }
    
    .section-divider {
        border-top: 2px solid #e0e0e0;
        margin: 30px 0;
    }
    
    .footer {
        text-align: center;
        padding-top: 30px;
        border-top: 1px solid #e0e0e0;
        color: #666;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'prediction_results' not in st.session_state:
    st.session_state.prediction_results = None
if 'last_prediction_time' not in st.session_state:
    st.session_state.last_prediction_time = None

# Header
st.markdown("""
    <div class="header-container">
        <h1>🧬 HIV Drug Resistance Predictor</h1>
        <p>Advanced ML-Powered Drug Resistance Prediction using ESM-2 Protein Language Model</p>
        <p style="font-size: 0.95em; opacity: 0.85;">Predict antiretroviral drug resistance from viral sequences</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Navigation")
    page = st.radio("Select Mode", ["Single Sequence", "Batch Prediction", "About"])
    
    st.markdown("---")
    st.markdown("### 📊 Model Information")
    st.info("""
    **Model:** ESM-2 Protein Language Model
    
    **Performance:**
    - Mean AUC: 0.968
    - Baseline AUC: 0.955
    - Improvement: +1.3%
    
    **Coverage:**
    - 18 Drugs Total
    - 8 Protease Inhibitors
    - 6 NRTIs
    - 4 NNRTIs
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ Help & Support")
    with st.expander("💡 How to use this tool"):
        st.markdown("""
        1. **Single Sequence**: Enter or paste an HIV protein sequence (RNA or amino acid)
        2. **Batch Prediction**: Upload a FASTA file with multiple sequences
        3. **Results**: View predictions and export as CSV
        
        For sequence format details, check the About section.
        """)

# Main content
if page == "Single Sequence":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔬 Single Sequence Prediction</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Enter Your Sequence")
        sequence_input = st.text_area(
            "Paste your HIV protein sequence below (FASTA format or raw sequence):",
            placeholder=">HIV_sample\nATGGGAGGGGATTAGACCAAGCCCGGGGGGGGGGGCGG...",
            height=150,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("#### Sequence Info")
        if sequence_input:
            # Remove fasta header if present
            seq_clean = sequence_input.split('\n', 1)[-1].replace('\n', '').replace(' ', '')
            st.metric("Sequence Length", len(seq_clean))
            if len(seq_clean) < 50:
                st.warning("Sequence too short")
            elif len(seq_clean) > 1000:
                st.warning("Sequence very long")
            else:
                st.success("Length OK")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Prediction button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        predict_button = st.button("🚀 Predict", use_container_width=True, type="primary")
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        sequence_input = ""
        st.session_state.prediction_results = None
        st.rerun()
    
    if predict_button:
        if not sequence_input.strip():
            st.markdown('<div class="error-alert">❌ Please enter a sequence first!</div>', unsafe_allow_html=True)
        else:
            with st.spinner('🔄 Processing sequence... This may take a moment.'):
                try:
                    model = load_model()
                    result = predict_single(model, sequence_input)
                    st.session_state.prediction_results = result
                    st.session_state.last_prediction_time = datetime.now()
                except Exception as e:
                    st.markdown(f'<div class="error-alert">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
    
    # Display results
    if st.session_state.prediction_results:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">✅ Prediction Results</div>', unsafe_allow_html=True)
        
        result_data = st.session_state.prediction_results
        
        # Create results visualization
        if isinstance(result_data, dict) and 'drugs' in result_data:
            drugs = result_data['drugs']
            probabilities = result_data['probabilities']
            
            # Create dataframe for display
            results_df = pd.DataFrame({
                'Drug Name': drugs,
                'Resistance Probability': probabilities
            })
            results_df['Resistance Status'] = results_df['Resistance Probability'].apply(
                lambda x: '🔴 Resistant' if x > 0.5 else '🟢 Susceptible'
            )
            results_df = results_df.sort_values('Resistance Probability', ascending=False)
            
            # Display as table
            st.dataframe(results_df, use_container_width=True, hide_index=True)
            
            # Create visualization
            fig = go.Figure()
            
            colors = ['#dc3545' if p > 0.5 else '#28a745' for p in results_df['Resistance Probability']]
            
            fig.add_trace(go.Bar(
                x=results_df['Drug Name'],
                y=results_df['Resistance Probability'],
                marker_color=colors,
                text=results_df['Resistance Probability'].round(3),
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Probability: %{y:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Drug Resistance Probability Across Predicted Drugs',
                xaxis_title='Drug',
                yaxis_title='Resistance Probability',
                height=400,
                showlegend=False,
                template='plotly_white',
                hovermode='x'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                resistant_count = (results_df['Resistance Probability'] > 0.5).sum()
                st.metric("Resistant Drugs", resistant_count)
            with col2:
                susceptible_count = (results_df['Resistance Probability'] <= 0.5).sum()
                st.metric("Susceptible Drugs", susceptible_count)
            with col3:
                avg_prob = results_df['Resistance Probability'].mean()
                st.metric("Average Probability", f"{avg_prob:.3f}")
        
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Batch Prediction":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📁 Batch Prediction (Multiple Sequences)</div>', unsafe_allow_html=True)
    
    st.markdown("#### Upload FASTA File")
    batch_file = st.file_uploader(
        "Choose a FASTA file with multiple sequences",
        type=['fasta', 'fa', 'txt'],
        label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        predict_batch_button = st.button("🚀 Predict Batch", use_container_width=True, type="primary")
    with col2:
        if st.button("📥 Download Sample FASTA", use_container_width=True):
            sample_fasta = """>HIV_Sample_1
ATGGAAGACCCGACGGAGACGACGACGAGACGACG
>HIV_Sample_2
ATGGAAGACCCGACGGAGACGACGACGAGACGACGATGATGATG
"""
            st.download_button(
                "📥 Download",
                sample_fasta,
                "sample.fasta",
                "text/plain"
            )
    
    if predict_batch_button:
        if batch_file is None:
            st.markdown('<div class="error-alert">❌ Please upload a FASTA file first!</div>', unsafe_allow_html=True)
        else:
            with st.spinner('🔄 Processing batch... This may take a while for large files.'):
                try:
                    model = load_model()
                    results = predict_batch(model, batch_file)
                    
                    result_df = pd.DataFrame(results)
                    st.session_state.prediction_results = result_df
                    
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<div class="success-alert">✅ Batch prediction completed successfully!</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-title">📊 Batch Results</div>', unsafe_allow_html=True)
                    
                    # Display statistics
                    st.metric(f"Total Sequences Processed: {len(result_df)}", "")
                    
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                    
                    # Download results
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Results as CSV",
                        csv,
                        f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f'<div class="error-alert">❌ Error: {str(e)}</div>', unsafe_allow_html=True)

elif page == "About":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📖 About This Application</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 Overview
    
    This application uses advanced machine learning to predict HIV drug resistance from viral sequences. 
    It leverages the **ESM-2 Protein Language Model** - a state-of-the-art pre-trained neural network 
    that understands protein sequences at a deep level.
    
    ### 🧬 How It Works
    
    1. **Input Processing**: Your HIV protein sequence is processed and formatted
    2. **Embedding Generation**: ESM-2 converts the sequence into a numerical representation (1,280 dimensions)
    3. **Attention Weighting**: The model focuses on resistance-critical positions
    4. **Classification**: Per-drug classifiers predict resistance probability for each antiretroviral drug
    
    ### 📈 Model Performance
    
    | Metric | Value |
    |--------|-------|
    | ESM-2 Mean AUC | **0.968** |
    | Baseline AUC | 0.955 |
    | Improvement | **+1.3%** (p=0.0017) |
    | DRM Enrichment | 2.48x |
    | Novel Positions | 228 |
    | Drugs Improved | 15/18 |
    
    ### 💊 Supported Drugs
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Protease Inhibitors (8)**")
        st.markdown("""
        - ATV (Atazanavir)
        - DRV (Darunavir)
        - FPV (Fosamprenavir)
        - IDV (Indinavir)
        - LPV (Lopinavir)
        - NFV (Nelfinavir)
        - SQV (Saquinavir)
        - TPV (Tipranavir)
        """)
    
    with col2:
        st.markdown("**NRTIs (6)**")
        st.markdown("""
        - ABC (Abacavir)
        - AZT (Zidovudine)
        - D4T (Stavudine)
        - DDI (Didanosine)
        - 3TC (Lamivudine)
        - TDF (Tenofovir)
        """)
    
    with col3:
        st.markdown("**NNRTIs (4)**")
        st.markdown("""
        - EFV (Efavirenz)
        - ETR (Etravirine)
        - NVP (Nevirapine)
        - RPV (Rilpivirine)
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🔧 Input Format
    
    The application accepts sequences in two formats:
    
    **FASTA Format** (recommended for batch):
    ```
    >SequenceName
    ATGGGGAACGCGCGC...
    ```
    
    **Raw Sequence**:
    ```
    ATGGGGAACGCGCGC...
    ```
    
    ### ⚠️ Important Notes
    
    - **Sequence Quality**: Ensure sequences are from authentic samples
    - **Reference**: Sequences should be aligned to HXB2 reference strain
    - **Length**: Minimum 50 bp recommended, typical range 200-1000 bp
    - **Confidence**: Model trained on Stanford HIVDB data
    
    ### 📚 References
    
    - **ESM-2**: [Meta AI Research](https://github.com/facebookresearch/esm)
    - **Stanford HIVDB**: [hivdb.stanford.edu](https://hivdb.stanford.edu/)
    - **IAS-USA**: [Drug Resistance Mutations](https://www.iasusa.org/)
    
    ### 📝 Citation
    
    If you use this tool, please cite:
    
    ```
    @software{hiv_esm2_2026,
      title={HIV Drug Resistance Prediction with ESM-2},
      author={Your Team},
      year={2026},
      url={https://github.com/Livison222/HIV-Drug-Resistance-Zimbabwe}
    }
    ```
    
    ### ⚕️ Disclaimer
    
    This tool is for **research purposes only** and should not be used as the sole basis 
    for clinical decision-making. Always consult with healthcare professionals for treatment decisions.
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>🧬 HIV Drug Resistance Predictor v1.0 | Built with ❤️ using Streamlit and ESM-2</p>
        <p>For questions or feedback, please visit the <a href="https://github.com/Livison222/HIV-Drug-Resistance-Zimbabwe" target="_blank">GitHub Repository</a></p>
        <p style="font-size: 0.85em; margin-top: 15px;">⚕️ <strong>Disclaimer:</strong> This tool is for research purposes only. Always consult healthcare professionals for clinical decisions.</p>
    </div>
""", unsafe_allow_html=True)
