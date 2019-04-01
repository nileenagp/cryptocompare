#Import required libraries
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly.tools import mpl_to_plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
from datetime import date
import datetime

#Get the coin list to populate currency picklist
url = "https://coinmarketcap.com/"
content = urllib.request.urlopen(url).read()
soup = BeautifulSoup(content,'lxml')
table = soup.find_all('table')[0] 
coin_list = pd.read_html(str(table))
coin_list = pd.DataFrame(coin_list[0])

#Extract the coin name to be used for the URL
coins=[]
for div in table.find_all('a', attrs={'class':'currency-name-container link-secondary'}):
    curr_url=div['href']
    if curr_url != None:
        val=curr_url[curr_url.index('/currencies')+12: ]
        coins.append(val.replace('/',''))

#Get the total market capitalization as of now
total_mkt_cap= soup.find("span", id="total-marketcap").text
print("total:" ,total_mkt_cap)

#Create the dash application
app = dash.Dash()

#Create the application layout
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

#Submit the user input for chart creations
@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input('button', 'n_clicks')],
    [State(component_id='COIN1', component_property='value'),
     State(component_id='COIN2', component_property='value')]    
)

#function to accept user inputs and create the charts
def update_value(clicks, coin1, coin2):
    if clicks is not None:
        input_data = [coin1, coin2]
        #list to save the market capitalization of selected currencies
        curr_mkt_cap=[]

        #Declare the total_mkt_cap as global to perform caculations within this function
        global total_mkt_cap

        print(input_data)
        print('Total_mkt_cap:',total_mkt_cap)
        
        #Define the plotly subplot layout
        fig = tools.make_subplots(rows=2, cols=2,subplot_titles=('<br>'+'<br>'+input_data[0],input_data[1],'<br>'                           
        '<b> Historical Market Capitalization </b> <br><br>'+input_data[0]+" Vs "+input_data[1], '<b> Total Market Capitalization-Dominance </b>'),
        horizontal_spacing=0.2,vertical_spacing=0.2,)
        
        #Loop through user input list and get their historical data
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
            # Trace for the Close amount
            trace1 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['Close**'],
                name = 'Close',
                line = dict(
                    color = 'green',
                    width = 2)
	        )
            # Trace for the Open amount
            trace2 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['Open*'],
                name = 'Open',
                line = dict(
                    color = 'blue',
                    width = 2)
	        )        
            # Trace for the High amount
            trace3 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['High'],
                name = 'High',
                line = dict(
                    color = 'red',
                    width = 2)
	        )    
            # Trace for the market capitalization
            trace4 = go.Scatter(
    	        x=dfCoin['Date'],
	            y=dfCoin['Market Cap'],
                fill= 'tozeroy',
                fillcolor = 'rgba(26,150,65,0.25)',
                opacity = 0.5,
	            name = 'Market Cap : '+curr
	        )

            #Customize the figure layout
            fig['layout'].update(height=850, width=1200, 
                            title='<br> <b> Historical Price comparison chart based on Open , High and Close amounts </b> <br> <br>'+'<br>')
            fig['layout']['titlefont'].update(color ='black', size = 14)
            fig['layout']['xaxis1'].update(title='Date')
            fig['layout']['yaxis1'].update(title='Price')
            fig['layout']['xaxis2'].update(title='Date')
            fig['layout']['yaxis2'].update(title='Price')
            fig['layout']['xaxis3'].update(title='Date')
            fig['layout']['yaxis3'].update(title='Price')
            
            #Create subplots
            fig.append_trace(trace1, 1, idx+1)  
            fig.append_trace(trace2, 1, idx+1)  
            fig.append_trace(trace3, 1, idx+1)  
    	
            fig.append_trace(trace4, 2, 1)          

            #Customize the subplot title size and color
            for i in fig['layout']['annotations']:
                i['font'] = dict(size=14, color='black')

            
            # Get the market capitilization of the currency
            curr_mkt_cap.append(float(soup.find("div", class_="coin-summary-item-detail").select_one("span")["data-usd"]))
            
        #Get the total market capitilization    
        total_mkt_cap = total_mkt_cap.replace ('$', '').replace(',', '')
        total_mkt_cap = float(total_mkt_cap)
        print('total_mkt_cap:',total_mkt_cap) 
        
               
        #Create subplot for total market capitalization dominance

        #Trace for currency 1
        today_date=date.today()
        print('today:',today_date)
        trace5 = go.Bar(
            x=["'%s'" % today_date],
            y=[curr_mkt_cap[0]],
            name=input_data[0],
            showlegend = False,
            marker=dict(
                color = 'rgba(26,150,65,0.5)'),
            text= [input_data[0]+' : '+str(round((curr_mkt_cap[0]/total_mkt_cap)*100,2))+'%'],
            textposition='inside'
        )
        #Trace for currency 2
        trace6 = go.Bar(
            x=["'%s'" % today_date],
            y=[curr_mkt_cap[1]],
            name=input_data[1],
            showlegend = False,
            marker=dict(
                color = 'rgba(100,75,30,0.5)'),
            text=[input_data[1]+' : '+str(round((curr_mkt_cap[1]/total_mkt_cap)*100,2))+'%'],
            textposition='inside'
        )
        #Trace for remaining currencies
        trace7 = go.Bar(
            x=["'%s'" % today_date],
            y=[total_mkt_cap-(curr_mkt_cap[1]+curr_mkt_cap[0])],
            name='Remaining Currencies',
            showlegend = False,
            marker=dict(
                color = 'rgba(50,150,30,0.5)'),
            text=['Remaining Currencies : '+str(round(((total_mkt_cap-(curr_mkt_cap[1]+curr_mkt_cap[0]))/total_mkt_cap)*100,2))+'%'],
            textposition='inside'
        )
        #Define the bar chart as stacked
        fig['layout'].update(barmode='stack')

        #Create subplots
        fig.add_trace(trace5,2,2) 
        fig.add_trace(trace6,2,2) 
        fig.add_trace(trace7,2,2) 

        fig['layout']['xaxis4'].update(title='Date',range=[today_date,today_date])
        fig['layout']['yaxis4'].update(title='Price')

        #Return the figure to application output section
        return dcc.Graph(id='myGraph', figure=fig
        )

#Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)
