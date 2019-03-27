from bs4 import BeautifulSoup
import urllib.request
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import pandas as pd
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly.tools import mpl_to_plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

#Get the coin list
url = "https://coinmarketcap.com/"
content = urllib.request.urlopen(url).read()
soup = BeautifulSoup(content,'lxml')
table = soup.find_all('table')[0] 
coin_list = pd.read_html(str(table))
coin_list = pd.DataFrame(coin_list[0])

#find the coin name for the history data
coins=[]
for div in table.find_all('a', attrs={'class':'currency-name-container link-secondary'}):
    curr_url=div['href']
    curr=div.text
    if curr_url != None:
        val=curr_url[curr_url.index('/currencies')+12: ]
        coins.append(val.replace('/',''))
print(coins)

app = dash.Dash()

app.layout = html.Div(children=[
    html.Div(children='''Cryptocurrency comparison''', style={'fontFamily': 'Courier New, monospace', 'fontSize': 25, 'color':'black', 'font-weight':'bold','textAlign': 'center', 'marginBottom': 50, 'marginTop': 25}),
    html.Div(children='''
        Please select the currencies to compare
    ''', style={'textAlign': 'center', 'fontFamily': 'Courier New, monospace', 'fontSize': 18, 'color': 'black', 'marginBottom': 50}),
    html.Span('''
        Currency 1:
    ''' , style={'fontFamily': 'Courier New, monospace', 'fontSize': 17, 'color': 'black'}),
    dcc.Dropdown(
                id="COIN1",
                options=[{
                    'label': i,
                    'value': i
                } for i in coins],
                value='',
                style={'width': '30%',
               'display': 'inline-block',
               'vertical-align': 'middle', 'fontFamily': 'Courier New, monospace', 'fontSize': 15, 'color': '#7f7f7f'}),
    html.Span('''
        Currency 2:
    ''', style={'fontFamily': 'Courier New, monospace', 'fontSize': 17, 'color': 'black'}),
    dcc.Dropdown(
                id="COIN2",
                options=[{
                    'label': i,
                    'value': i
                } for i in coins],
                value='',
                style={'width': '30%',
               'display': 'inline-block',
               'vertical-align': 'middle', 'fontFamily': 'Courier New, monospace', 'fontSize': 15, 'color': '#7f7f7f'}),
    html.Button('Submit', id='button', style={'fontFamily': 'Courier New, monospace', 'fontSize': 15, 'fontWeight': 'bold', 'color': '#7f7f7f'}),
    html.Div(id='output-graph'),
])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input('button', 'n_clicks')],
    [State(component_id='COIN1', component_property='value'),
     State(component_id='COIN2', component_property='value')]    
)
def update_value(clicks, coin1, coin2):
    if clicks is not None:
        input_data = [coin1, coin2]
        print(input_data)

        fig = tools.make_subplots(rows=2, cols=2,subplot_titles=('<br>'+'<br>'+input_data[0],input_data[1],'<br>'                           
        '                   <b> Historical Market Capitization </b> <br><br>'+input_data[0]+" Vs "+input_data[1]),
        horizontal_spacing=0.2,vertical_spacing=0.2,)
        #Loop through user input list
        for idx,curr in enumerate(input_data):
            url="https://coinmarketcap.com/currencies/"+curr+"/historical-data/"
            print(url)
            content=urllib.request.urlopen(url).read()
            soup = BeautifulSoup(content,'lxml')
            table = soup.find_all('table')[0] 
            dfCoinhtml = pd.read_html(str(table))
    
        #Convert the html table into a dataframe
            dfCoin=pd.DataFrame(dfCoinhtml[0])
            dfCoin['Date']=pd.to_datetime(dfCoin['Date'])

        #Start plotting graphs

            trace1 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['Close**'],
                showlegend = False,
                name = 'Close',
                line = dict(
                    color = 'green',
                    width = 2)
	        )
	
            trace2 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['Open*'],
                name = 'Open',
                line = dict(
                    color = 'blue',
                    width = 2)
	        )        
	
            trace3 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['High'],
                name = 'High',
                line = dict(
                    color = 'red',
                    width = 2)
	        )    
        
            trace4 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['Market Cap'],
                fill= 'tozeroy',
                fillcolor = 'rgba(26,150,65,0.25)',
                opacity = 0.5,
	            name = 'Market Cap : '+curr
	        )
	
            fig['layout'].update(height=850, width=1200, 
                            title='<br> <b> Historical Price comparison chart based on Open , High and Close amounts </b> <br> <br>'+'<br>')
            fig['layout']['titlefont'].update(color ='black', size = 14)

            
            fig.append_trace(trace1, 1, idx+1)  
            fig.append_trace(trace2, 1, idx+1)  
            fig.append_trace(trace3, 1, idx+1)  
    	
            fig.append_trace(trace4, 2, 1)          

            for i in fig['layout']['annotations']:
                i['font'] = dict(size=14, color='black')
        #plotly_fig = mpl_to_plotly(fig)
        
        return dcc.Graph(id='myGraph', figure=fig
        )

if __name__ == '__main__':
    app.run_server(debug=True)
