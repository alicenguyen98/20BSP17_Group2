import os
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score

import pandas as pd
import numpy as np

import db_manager, data_analyzer

app = dash.Dash(__name__)

dropdown_values = []
series_sentiment = None


def run():
    body = [
        html.H1('Sentiment Analysis results')
    ]

    performance = db_manager.get_all_classification_performance()

    if performance:
        df = get_performance_df(performance)
        df_train, df_test = split_performance_df(df)

        # Training data column
        div_train = html.Div(
            className='grid-col', 
            children=[
                html.H2('Training Dataset'),
                dcc.Graph(figure=get_barchart(df_train, 'Bar chart')),
                dcc.Graph(figure=get_heatmap(df_train, 'Heatmap'))
            ])

        # Testing data column
        div_test = html.Div(
            className='grid-col',
            children=[
                html.H2('Testing Dataset'),
                dcc.Graph(figure=get_barchart(df_test, 'Bar chart')),
                dcc.Graph(figure=get_heatmap(df_test, 'Heatmap'))
            ])

        # Initiate dropdown values and corresponding tuple values
        global dropdown_values
        dropdown_values = [x for x in df[['model_id', 'model_name', 'label']].itertuples(index=False)]

        # initial model id and label
        model_id = int(df.iloc[0]['model_id'])
        label = df.iloc[0]['label']

        # ROC and Confusion matrix column
        df_classification = get_classification_df(model_id, label)

        dropdown = dcc.Dropdown(
            id='model-dropdown',
            options=[ { 'value': i, 'label': f'{dropdown_values[i][1]} ({dropdown_values[i][2]})' } for i in range(len(dropdown_values))],
            value=model_id,
            clearable=False
            )

        roc_title_span = html.Span(
            id='roc-span', 
            children=[
                html.H2('ROC & Confusion Matrix'), 
                dropdown
            ])

        div_roc = html.Div(
            className='grid-col', 
            children=[
                roc_title_span,
                dcc.Graph(id='roc-curve', figure=get_roc_curve(df_classification)),
                dcc.Graph(id='confusion-matrix', figure=get_confusion_matrix(df_classification)),
            ])
        
        # finally
        body.append(html.Div(
            id='contents-grid', 
            children=[
                div_train,
                div_test,
                div_roc
            ]))
    else:
         body.append(html.H2('No performance data found! Please perform the whole cycle of model training, analyzing and performance evaluation.'))      

    app.layout = html.Div(children=body)

    app.run_server(debug=True)

def get_heatmap(df, title):
    fig_data = df.to_numpy()

    x = list(df.columns.values)
    y = list(df.index.values)

    fig = ff.create_annotated_heatmap(fig_data, x=x, y=y, annotation_text= np.around(fig_data, 4), showscale=True)
    fig.update_xaxes(side='bottom')
    fig.update_yaxes(title='model names')
    fig.update_layout(title=title)

    return fig

def get_confusion_matrix(df):
    matrix = confusion_matrix(df['sentiment'], df['classification'], labels=[-1, 0, 1])
    x = y = ['negative', 'neutral', 'positive']
    fig = ff.create_annotated_heatmap(np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), x=x, y=y,annotation_text=matrix, colorscale='pinkyl')
    fig.update_xaxes(title='Actual values')
    fig.update_yaxes(title='Predicted values', autorange='reversed')
    fig.update_layout(title='Confusion Matrix')
    return fig

def get_roc_curve(df):
    y_true = pd.get_dummies(df['sentiment'], columns=[-1, 0, 1])
    y_score = pd.get_dummies(df['classification'], columns=[-1, 0, 1])

    fig = go.Figure()
    fig.add_shape(type='line', line={'dash':'dash'}, x0=0, x1=1, y0=0, y1=1)

    for label, name in [(-1, 'negative'), (0, 'neutral'), (1, 'positive')]:
        try:
            fpr, tpr, _ = roc_curve(y_true[label], y_score[label], pos_label=1)
            auc_score = roc_auc_score(y_true[label], y_score[label])
            trace = go.Scatter(x=fpr, y=tpr, name=f'{name} (AUC={auc_score:.4f})', mode='lines')
            fig.add_trace(trace)
        except Exception as err:
            print(err)

    fig.update_layout(
        title='ROC curves',
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        xaxis=dict(scaleanchor='x', scaleratio=1),
        yaxis=dict(constrain='domain')
    )
    return fig

def get_barchart(df, title):
    fig = px.bar(df)
    fig.update_layout(title=title)
    return fig

def split_performance_df(df) -> tuple:
    df = df.set_index('model_name')
    columns = ['accuracy', 'precision', 'recall', 'f1']
    return df.loc[df['label'] == 'train'][columns], df.loc[df['label'] == 'test'][columns]

def get_performance_df(performance):
    df = pd.DataFrame(performance, columns=['model_id', 'label', 'accuracy', 'precision', 'recall', 'f1'])
    for index, id in df['model_id'].drop_duplicates().iteritems():
        name = db_manager.get_analysis_model_name(id)
        df.loc[df['model_id'] == id, 'model_name'] = name

    return df

def get_classification_df(model_id, label):
    # Check and initialize sentiment series
    global series_sentiment
    if not isinstance(series_sentiment, pd.Series):
        series_sentiment = data_analyzer.get_reviewed_tweets()['sentiment']
        
    classification = db_manager.get_classification(model_id, label)
    if not classification:
        return None
    
    df = pd.DataFrame(classification, columns=['id', 'classification']).set_index('id')
    df = pd.concat([df, series_sentiment], join='inner', axis=1).dropna()
    return df

#region callbacks

@app.callback(
    [Output('roc-curve', 'figure'), Output('confusion-matrix', 'figure')],
    Input('model-dropdown', 'value'))
def update_output(value):
    model_id, _, label = dropdown_values[value]
    df_classification = get_classification_df(model_id, label)
    return [get_roc_curve(df_classification), get_confusion_matrix(df_classification)]

#endregion

if __name__ == '__main__':
    run()