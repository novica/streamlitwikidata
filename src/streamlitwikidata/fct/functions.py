import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd


def endpoint_url():
    endpoint_url = "https://query.wikidata.org/sparql"
    return endpoint_url


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (
        sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def wrangle_results(results):
    df = pd.json_normalize(results['results']['bindings'])

    df_filtered = df[df.filter(like='value').columns]

    df_filtered = df_filtered.rename(
        columns={
            'dateOfBirth.value': 'dob',
            'personLabel.value': 'name',
            'personGenderLabel.value': 'gender',
            'politicalPartyLabel.value': 'party',
            'childLabel.value': 'child_name',
            'spouseLabel.value': 'spouse_name'
        })

    df_filtered.assign(
        dob=pd.to_datetime(df_filtered["dob"])
    )

    df_rel = df_filtered.dropna(
        subset=['child_name', 'spouse_name'], how='all')

    df_names = df_rel[['name', 'child_name', 'spouse_name']]

    df_names = df_names.drop_duplicates('name')

    df_names_long = pd.melt(df_names, id_vars=['name'], value_vars=['child_name', 'spouse_name'],
                            var_name='relationship_type', value_name='relationship_name')

    df_names_long = df_names_long.dropna(
        subset=['relationship_name']).sort_values(by=['name'], ignore_index=True)

    df_names_long.assign(relationship_type = df_names_long['relationship_type'].str.replace('_name', ''))

    return df_names_long


def paste_query(country_code):
        query = """SELECT ?personLabel ?personGenderLabel ?dateOfBirth ?politicalPartyLabel ?spouseLabel ?childLabel WHERE {{
                    ?person wdt:P106 wd:Q82955;
                    wdt:P27 {country_code};
                    wdt:P21 ?personGender;
                    wdt:P569 ?dateOfBirth;
                    OPTIONAL {{?person wdt:P102 ?politicalParty. }}
                    OPTIONAL {{?person wdt:P26 ?spouse. }}
                    OPTIONAL {{?person wdt:P40 ?child. }}
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                    }}
                    LIMIT 500""".format(country_code=country_code)
        return query

