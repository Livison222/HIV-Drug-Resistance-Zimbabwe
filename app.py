import streamlit as st
import pandas as pd
from src.model_saver import load_model, predict_single, predict_batch

# Initialize Streamlit app
st.title('HIV Drug Resistance Prediction')

# Single sequence prediction
st.header('Single Sequence Prediction')
sequence_input = st.text_area("Enter RNA sequence:", "")
if st.button('Predict'):
    model = load_model()
    result = predict_single(model, sequence_input)
    st.success(f'Prediction: {result}')

# Batch prediction
st.header('Batch Prediction')
batch_file = st.file_uploader("Upload FASTA file:", type=['fasta', 'fa'])
if st.button('Predict Batch'):
    if batch_file is not None:
        model = load_model()
        results = predict_batch(model, batch_file)
        result_df = pd.DataFrame(results)
        st.write(result_df)
        st.download_button("Export results as CSV", result_df.to_csv().encode('utf-8'), "predictions.csv")

    else:
        st.error("Please upload a valid FASTA file.")