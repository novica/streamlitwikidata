import streamlit as st
from fct.functions import endpoint_url, get_results, wrangle_results, paste_query

def app():
    '''
    # Wikidata streamlit test app
    '''

    form = st.form(key='my_form')
    code = form.text_input(label='Wikidata Country Code')
    submit_button = form.form_submit_button(label='Submit code')

    if submit_button:
        st.write(paste_query(code))
        results = get_results(endpoint_url=endpoint_url(), query=paste_query(code))
        names = wrangle_results(results=results)
        st.write(names)

if __name__ == "__main__":
	app()
